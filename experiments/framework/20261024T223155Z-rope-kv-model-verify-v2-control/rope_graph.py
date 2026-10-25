"""只读FX调用图：沿真实submodule实参/形参/返回值追Q/K/dep；不执行FX。"""
import ast
from dataclasses import dataclass
import re

FUSION = {'torch.ops.vllm.biv150_rope_kv', 'torch.ops.vllm.biv150_rope_kv.default'}
ATTENTION = {'torch.ops.vllm.unified_attention_with_output', 'torch.ops.vllm.unified_attention_with_output.default'}
OLD_UPDATE = {'torch.ops.vllm.unified_kv_cache_update', 'torch.ops.vllm.unified_kv_cache_update.default'}


def dotted(node):
    if isinstance(node, ast.Name):return node.id
    if isinstance(node, ast.Attribute):return dotted(node.value) + '.' + node.attr
    return ''


def require(ok, message):
    if not ok:raise ValueError(message)


def layer_number(node):
    require(isinstance(node, ast.Constant) and isinstance(node.value, str), 'FX层名不是固定字符串')
    match = re.fullmatch(r'model\.layers\.(\d+)\.self_attn\.attn', node.value)
    require(match is not None, 'FX层名不符MiniCPM实例')
    return int(match.group(1))


@dataclass(frozen=True)
class Origin:
    key: tuple
    output: int


def inspect_graph(text):
    tree = ast.parse(text)
    static = {kind: [n for n in ast.walk(tree) if isinstance(n, ast.Call) and dotted(n.func) in ops]
              for kind, ops in (('fusion', FUSION), ('attention', ATTENTION), ('old', OLD_UPDATE))}
    require(not static['old'], '真实FX仍有旧unified_kv_cache_update')
    classes = [n for n in tree.body if isinstance(n, ast.ClassDef)]
    modules = {}
    def register(cls, path):
        methods = [n for n in cls.body if isinstance(n, ast.FunctionDef) and n.name == 'forward']
        require(len(methods) == 1, 'FX模块缺少唯一forward: ' + '.'.join(path))
        require(path not in modules, '重复FX模块')
        modules[path] = methods[0]
        for child in cls.body:
            if isinstance(child, ast.ClassDef):register(child, path + (child.name,))
    if classes:
        require(len(classes) == 1, 'FX顶层模型模块不唯一')
        root = (classes[0].name,)
        register(classes[0], root)
    else:
        functions = [n for n in tree.body if isinstance(n, ast.FunctionDef)]
        require(len(functions) == 1, '未拆分FX缺少唯一入口')
        root = (functions[0].name,)
        modules[root] = functions[0]
    fusions, consumers, invocations = [], [], []
    visited_fusions, visited_attention = [], []
    active = set()

    def invoke(path, arguments, keywords, call_path):
        require(path in modules and path not in active, '未知或递归FX子模块')
        fn = modules[path]
        require(not fn.args.vararg and not fn.args.kwarg and not fn.args.kwonlyargs
                and not fn.args.defaults, 'FX forward参数形式未支持')
        formals = fn.args.posonlyargs + fn.args.args
        if formals and formals[0].arg == 'self':formals = formals[1:]
        require(len(arguments) <= len(formals), 'FX子模块实参数量过多')
        env = {p.arg: value for p, value in zip(formals, arguments)}
        for name, value in keywords.items():
            require(name in {p.arg for p in formals} and name not in env, 'FX子模块keyword绑定冲突')
            env[name] = value
        require(set(env) == {p.arg for p in formals}, 'FX子模块实参/形参未闭合')
        active.add(path)
        invocations.append({'module': '.'.join(path), 'call_path': list(call_path)})

        def value(node):
            if isinstance(node, ast.Name):return env.get(node.id)
            if isinstance(node, (ast.Tuple, ast.List)):return tuple(value(n) for n in node.elts)
            if isinstance(node, ast.Subscript):
                base = value(node.value)
                if isinstance(base, tuple):
                    require(isinstance(node.slice, ast.Constant) and type(node.slice.value) is int,
                            '已追踪tuple必须使用固定整数下标')
                    index = node.slice.value
                    require(-len(base) <= index < len(base), 'FX tuple下标越界')
                    return base[index]
                return None
            if not isinstance(node, ast.Call):return None
            op = dotted(node.func)
            if op in FUSION:
                require(len(node.args) == 4 and not node.keywords, '融合op参数非预期')
                layer = layer_number(node.args[3])
                key = call_path + (fn.lineno, node.lineno)
                fusions.append({'key': list(key), 'layer': layer, 'line': node.lineno,
                                'module': '.'.join(path)})
                visited_fusions.append(node.lineno)
                return tuple(Origin(key, i) for i in range(3))
            if op in ATTENTION:
                require(len(node.args) >= 5, '原Attention参数缺失')
                layer = layer_number(node.args[4])
                deps = [k.value for k in node.keywords if k.arg == 'kv_cache_dummy_dep']
                require(len(deps) == 1, '原Attention缺少唯一显式dep')
                q, k, dep = value(node.args[0]), value(node.args[1]), value(deps[0])
                require(all(isinstance(x, Origin) for x in (q, k, dep))
                        and q.key == k.key == dep.key and (q.output, k.output, dep.output) == (0, 1, 2),
                        'Q/K/dep没有沿实际调用图来自同一个融合op的0/1/2返回')
                match = [f for f in fusions if tuple(f['key']) == dep.key]
                require(len(match) == 1 and match[0]['layer'] == layer, '融合返回接入另一层Attention')
                consumers.append({'fusion_key': list(dep.key), 'layer': layer, 'line': node.lineno,
                                  'module': '.'.join(path), 'call_path': list(call_path)})
                visited_attention.append(node.lineno)
                return None
            if isinstance(node.func, ast.Attribute) and isinstance(node.func.value, ast.Name) and node.func.value.id == 'self':
                child = path + (node.func.attr,)
                require(child in modules, '未知FX self调用: ' + '.'.join(child))
                require(all(k.arg is not None for k in node.keywords), '不接受展开keyword')
                return invoke(child, [value(n) for n in node.args],
                              {k.arg: value(k.value) for k in node.keywords}, call_path + (node.lineno,))
            if op in ('operator.getitem', 'getitem') and len(node.args) == 2:
                return value(ast.Subscript(value=node.args[0], slice=node.args[1], ctx=ast.Load()))
            if isinstance(node.func, ast.Attribute) and node.func.attr in ('view', 'reshape', 'flatten'):
                original = value(node.func.value)
                return original if isinstance(original, Origin) else None
            # 未知算术不继承其输入来源；不得把计算结果当成原Q/K/dep。
            return None

        def assign(target, result):
            if isinstance(target, ast.Name):env[target.id] = result
            elif isinstance(target, (ast.Tuple, ast.List)):
                require(result is None or isinstance(result, tuple) and len(result) == len(target.elts),
                        'FX解包长度不符')
                for i, item in enumerate(target.elts):assign(item, None if result is None else result[i])
            else:raise ValueError('未支持的FX赋值目标')

        try:
            for statement in fn.body:
                if isinstance(statement, (ast.Assign, ast.AnnAssign)):
                    result = value(statement.value)
                    targets = statement.targets if isinstance(statement, ast.Assign) else [statement.target]
                    for target in targets:assign(target, result)
                elif isinstance(statement, ast.Expr):value(statement.value)
                elif isinstance(statement, ast.Return):return value(statement.value)
                elif isinstance(statement, ast.Pass):continue
                else:raise ValueError('FX入口包含未支持的控制流: ' + type(statement).__name__)
            return None
        finally:active.remove(path)

    params = modules[root].args.posonlyargs + modules[root].args.args
    count = len(params) - (1 if params and params[0].arg == 'self' else 0)
    invoke(root, [None] * count, {}, ())
    require(sorted(visited_fusions) == sorted(n.lineno for n in static['fusion'])
            and sorted(visited_attention) == sorted(n.lineno for n in static['attention']),
            '存在未沿顶层实际调用到达或重复执行的融合/Attention')
    require(len(fusions) == 42 and sorted(f['layer'] for f in fusions) == list(range(42)),
            '真实调用图未包含唯一42层rope_kv')
    require(len(consumers) == 42 and sorted(c['layer'] for c in consumers) == list(range(42))
            and sorted(c['fusion_key'] for c in consumers) == sorted(f['key'] for f in fusions),
            '融合返回与42层原Attention消费未一一闭合')
    return {'fusion_count': 42, 'old_update_count': 0, 'attention_consumers': 42,
            'layers': list(range(42)), 'q_k_dep_from_same_fusion': True,
            'parser': 'top_level_call_arguments_and_returns_v2', 'module_invocations': invocations,
            'fusions': fusions, 'consumers': consumers}
