"""标准库解析实际 typed FX：核显式 M/S 与末层选行，不执行图。"""
import ast
import re


def require(ok, message):
    if not ok: raise ValueError(message)


def dotted(node):
    if isinstance(node, ast.Name): return node.id
    if isinstance(node, ast.Attribute): return dotted(node.value) + '.' + node.attr
    return ''


def annotation(node):
    return node.value if isinstance(node, ast.Constant) and isinstance(node.value, str) else ''


def shape(text):
    match = re.fullmatch(r'(?:bf16|i32|i64)\[(.*)\]', text)
    return [x.strip() for x in match[1].split(',')] if match else None


def verify_provenance(tree):
    """仅解释FX数据来源/tuple槽；不执行图，也不从局部形参名字猜来源。"""
    class Origin:
        def __init__(self, kind, args=(), label=''):
            self.kind, self.args, self.label = kind, tuple(args), label
    def flatten(value):
        if isinstance(value, Origin): return [value]
        if isinstance(value, (tuple, list)): return [x for v in value for x in flatten(v)]
        return []
    def ancestors(value):
        found = set()
        def walk(x):
            if not isinstance(x, Origin) or x in found: return
            found.add(x)
            for y in x.args: walk(y)
        for x in flatten(value): walk(x)
        return found
    def weights(value, fragment):
        return any(n.kind == 'input' and fragment in n.label for n in ancestors(value))
    outer = next(c for c in tree.body if isinstance(c, ast.ClassDef) and c.name == 'GraphModule')
    modules = {c.name: c for c in outer.body if isinstance(c, ast.ClassDef)}
    root = next(f for f in outer.body if isinstance(f, ast.FunctionDef) and f.name == 'forward')
    inputs = {a.arg:Origin('input', label=a.arg) for a in root.args.args if a.arg != 'self'}
    indices = [x for k,x in inputs.items() if 'tail_logits_indices' in k.lower()]
    require(len(indices) == 1, 'provenance缺原indices')
    index = indices[0]
    seen = []; active = set(); gather_nodes = []; scatter_nodes = []; projection_nodes = {}; last_query = []; last_output = []; live_attention = []; live_updates = []
    def storage_base(value):
        # 原Attention先view输出buffer，custom op写该buffer，随后view回二维。
        while isinstance(value,Origin) and value.kind.endswith(('.view','.reshape')) and value.args:
            value=value.args[0]
        return value
    def interpret(function, bindings, tag):
        require(tag not in active, 'FX递归调用拒绝')
        active.add(tag); env = dict(bindings)
        def evaluate(node):
            if node is None: return None
            if isinstance(node, ast.Name): return env.get(node.id)
            if isinstance(node, ast.Constant): return node.value
            if isinstance(node, ast.Attribute) and dotted(node).startswith('torch.'):
                return dotted(node)
            if isinstance(node, (ast.Tuple, ast.List)): return tuple(evaluate(x) for x in node.elts)
            if isinstance(node, ast.Subscript):
                value, item = evaluate(node.value), evaluate(node.slice)
                if isinstance(value, tuple) and isinstance(item, int):
                    require(-len(value) <= item < len(value), 'tuple槽越界'); return value[item]
                if isinstance(value, Origin) and item is index:
                    result = Origin('gather', (value, index)); gather_nodes.append(result); return result
                return Origin('getitem', flatten(value)+flatten(item), label=str(item))
            if isinstance(node, ast.Call):
                name = dotted(node.func)
                args = [evaluate(x) for x in node.args]
                kw = {x.arg:evaluate(x.value) for x in node.keywords}
                if name.startswith('self.') and name[5:] in modules:
                    child = modules[name[5:]]
                    f = next(x for x in child.body if isinstance(x,ast.FunctionDef) and x.name=='forward')
                    names = [a.arg for a in f.args.args if a.arg!='self']
                    require(len(args) == len(names) and not kw, 'submod实参/形参不闭合')
                    require(child.name not in seen, '重复submod调用拒绝')
                    seen.append(child.name)
                    return interpret(f, dict(zip(names,args)), child.name)
                receiver = evaluate(node.func.value) if isinstance(node.func,ast.Attribute) else None
                children = flatten(args)+flatten(tuple(kw.values()))
                if not name.startswith(('torch.','operator.')): children = flatten(receiver)+children
                if name in ('operator.getitem',) and len(args)==2:
                    if isinstance(args[0],tuple) and isinstance(args[1],int): return args[0][args[1]]
                    return Origin('getitem',flatten(args[0]),label=str(args[1]))
                if name == 'torch._C._nn.linear' and len(args)>=2:
                    for key in ('self_attn_modules_o_proj','mlp_modules_gate_up_proj','mlp_modules_down_proj'):
                        if weights(args[1], 'layers_modules_41_modules_'+key):
                            result=Origin(key,children); projection_nodes.setdefault(key,[]).append(result); return result
                if 'fused_add_rms_norm' in name:
                    kind='norm'
                    if weights(args[2], 'layers_modules_41_modules_input_layernorm_'):kind='input_norm41'
                    if weights(args[2], 'self_modules_norm_parameters_weight_'):kind='final_norm'
                    parent=Origin(kind,children)
                    return (Origin(kind+'_output',(parent,)),Origin(kind+'_residual',(parent,)))
                if name.endswith(('unified_attention_with_output', 'unified_kv_cache_update')):
                    layer_names=[x for x in args if isinstance(x,str) and re.fullmatch(r'model\.layers\.\d+\.self_attn\.attn',x)]
                    require(len(layer_names)==1, '可达Attention/KV层号缺失')
                    layer=int(layer_names[0].split('.')[2])
                    target=live_attention if name.endswith('unified_attention_with_output') else live_updates
                    target.append(layer)
                    if target is live_attention and layer==41:
                        last_query.append(args[0]);last_output.append(args[3])
                if isinstance(node.func,ast.Attribute) and node.func.attr in ('index_copy','index_copy_'):
                    require(len(args)==3 and args[0]==0, 'scatter axis错误')
                    result=Origin('scatter',flatten(receiver)+flatten(args[1])+flatten(args[2]))
                    scatter_nodes.append((result, receiver, args[1],args[2]))
                    if node.func.attr=='index_copy_' and isinstance(node.func.value,ast.Name):env[node.func.value.id]=result
                    return result
                kind='zeros' if isinstance(node.func,ast.Attribute) and node.func.attr=='new_zeros' else name or 'call'
                return Origin(kind,children)
            return Origin(type(node).__name__, [x for child in ast.iter_child_nodes(node) for x in flatten(evaluate(child))])
        result=None
        for statement in function.body:
            if isinstance(statement,(ast.Assign,ast.AnnAssign)):
                value=evaluate(statement.value)
                targets=statement.targets if isinstance(statement,ast.Assign) else [statement.target]
                for target in targets:
                    require(isinstance(target,ast.Name),'未知FX赋值目标');env[target.id]=value
            elif isinstance(statement,ast.Expr):evaluate(statement.value)
            elif isinstance(statement,ast.Return):result=evaluate(statement.value);break
        active.remove(tag);return result
    returned=flatten(interpret(root,inputs,'GraphModule'))
    require(sorted(live_attention)==list(range(42)) and sorted(live_updates)==list(range(42)), '根入口未到达全部42 Attention/KV')
    require(len(scatter_nodes)==1 and len(returned)==1 and returned[0] is scatter_nodes[0][0], '实际根返回未连接唯一scatter')
    require(all(len(projection_nodes.get(key,[]))==1 for key in ('self_attn_modules_o_proj','mlp_modules_gate_up_proj','mlp_modules_down_proj')), '实际调用projection不唯一')
    op=projection_nodes['self_attn_modules_o_proj'][0]
    gate=projection_nodes['mlp_modules_gate_up_proj'][0];down=projection_nodes['mlp_modules_down_proj'][0]
    require(len(gather_nodes)==2, '实际原indices未唯一进入双gather')
    require(len(last_output)==1, '实际末层Attention输出buffer不唯一')
    hg=[x for x in gather_nodes if storage_base(x.args[0]) is storage_base(last_output[0])]
    rg=[x for x in gather_nodes if x.args[0].kind=='input_norm41_residual']
    require(len(hg)==len(rg)==1 and hg[0] is not rg[0], '双gather未取实际末层Attention输出buffer和inputnorm residual')
    require(len(last_query)==1 and rg[0].args[0].args[0] in ancestors(last_query[0]), '末层residual未与本层Attention共享inputnorm')
    require(hg[0] in ancestors(op) and op in ancestors(gate) and rg[0] in ancestors(gate) and gate in ancestors(down), 'Attention→gather→oproj→postnorm→gate/down链断开')
    _,zero,idx,selected=scatter_nodes[0]
    require(isinstance(zero,Origin) and zero.kind=='zeros', 'scatter目标不是实际zeros')
    def same_index(x):
        return x is index or (isinstance(x,Origin) and x.kind.endswith('.to') and len(x.args)==1 and same_index(x.args[0]))
    require(same_index(idx), 'scatter未使用原indices或其直接dtype cast')
    require(isinstance(selected,Origin) and selected.kind=='final_norm_output'
        and down in ancestors(selected) and rg[0] in ancestors(selected), 'scatter源未走实际down/residual/finalnorm')
    return dict(root_returns_scatter=True, original_indices_bound=True, visited_submodules=seen,
                last_inputnorm_shared_with_attention=True, attention_output_before_oproj=True, suffix_chain=True)


def inspect_graph(text):
    tree = ast.parse(text)
    outer = [x for x in tree.body if isinstance(x, ast.ClassDef) and x.name == 'GraphModule']
    require(len(outer) == 1, '缺少唯一FX GraphModule')
    root = [x for x in outer[0].body if isinstance(x, ast.FunctionDef) and x.name == 'forward']
    require(len(root) == 1, '缺少唯一FX入口')
    args = root[0].args.args
    token = [a for a in args if 'input_ids' in a.arg.lower()]
    sample = [a for a in args if 'tail_logits_indices' in a.arg.lower()]
    require(len(token) == len(sample) == 1, '缺少显式M/S输入Tensor')
    M = shape(annotation(token[0].annotation)); S = shape(annotation(sample[0].annotation))
    require(M and S and len(M) == len(S) == 1 and M != S
            and not M[0].isdigit() and not S[0].isdigit(), 'M/S未独立动态化')
    M, S = M[0], S[0]
    require(re.fullmatch(r's\d+', M) and re.fullmatch(r'u\d+', S), '未形成BACKED M与独立unbacked S')
    attention = []; updates = []; gathers = []; projections = {}; scatters = []
    functions = [(c.name + '.' + f.name, f) for c in ast.walk(tree) if isinstance(c, ast.ClassDef)
                 for f in c.body if isinstance(f, ast.FunctionDef)]
    for scope, f in functions:
        types = {a.arg: annotation(a.annotation) for a in f.args.args}
        indices = {a.arg for a in f.args.args if 'tail_logits_indices' in a.arg.lower()}
        zero = set(); selected = set(); cast_indices = set(indices)
        for statement in f.body:
            if not isinstance(statement, (ast.Assign, ast.AnnAssign, ast.Expr)): continue
            value = statement.value
            targets = statement.targets if isinstance(statement, ast.Assign) else (
                [statement.target] if isinstance(statement, ast.AnnAssign) else [])
            names = [n.id for n in targets if isinstance(n, ast.Name)]
            out_type = annotation(statement.annotation) if isinstance(statement, ast.AnnAssign) else ''
            if out_type:
                for name in names: types[name] = out_type
            if isinstance(value, ast.Constant) and value.value is None:
                for name in names:
                    indices.discard(name); cast_indices.discard(name); zero.discard(name); selected.discard(name)
                continue
            if isinstance(value, ast.Name):
                for name in names:
                    if value.id in indices: indices.add(name)
                    if value.id in cast_indices: cast_indices.add(name)
                    if value.id in zero: zero.add(name)
                continue
            if isinstance(value, ast.Subscript) and isinstance(value.value, ast.Name) and isinstance(value.slice, ast.Name):
                if value.slice.id in indices and shape(types.get(value.value.id, '')) == [M, '2048']:
                    require(shape(out_type) == [S, '2048'], '选行结果不是S×2048')
                    gathers.append(dict(function=scope, line=statement.lineno, input=value.value.id, index=value.slice.id))
                    selected.update(names)
            if not isinstance(value, ast.Call): continue
            name = dotted(value.func)
            if name.endswith('unified_attention_with_output') or name.endswith('unified_kv_cache_update'):
                layers = [int(re.search(r'layers\.(\d+)\.', a.value)[1]) for a in value.args
                    if isinstance(a, ast.Constant) and isinstance(a.value, str) and re.search(r'layers\.(\d+)\.', a.value)]
                require(len(layers) == 1, 'Attention/KV层号不唯一')
                target = attention if name.endswith('unified_attention_with_output') else updates
                target.append(layers[0])
                if layers[0] == 41 and target is attention:
                    require(isinstance(value.args[0], ast.Name) and shape(types.get(value.args[0].id, '')) == [M, '16', '128'],
                            '末层Attention的Q未保持M行')
            if name == 'torch._C._nn.linear' and len(value.args) >= 2:
                weight = dotted(value.args[1])
                if 'layers_modules_41_' in weight:
                    for key, rows, cols in [('self_attn_modules_o_proj', S, '2048'),
                                           ('mlp_modules_gate_up_proj', S, '12288'),
                                           ('mlp_modules_down_proj', S, '2048')]:
                        if key in weight:
                            require(key not in projections and shape(out_type) == [rows, cols], '末层projection行数/唯一性错误:'+key)
                            projections[key] = dict(function=scope, line=statement.lineno, shape=shape(out_type))
            if isinstance(value.func, ast.Attribute):
                base = value.func.value
                if value.func.attr == 'to' and isinstance(base, ast.Name) and base.id in indices:
                    require(shape(out_type) == [S], 'scatter索引cast改变行数')
                    cast_indices.update(names)
                if value.func.attr == 'new_zeros':
                    require(shape(out_type) == [M, '2048'], 'dense zero不是M×2048')
                    zero.update(names)
                if value.func.attr in ('index_copy_', 'index_copy'):
                    require(isinstance(base, ast.Name) and base.id in zero and len(value.args) == 3
                            and isinstance(value.args[0], ast.Constant) and value.args[0].value == 0
                            and isinstance(value.args[1], ast.Name) and value.args[1].id in cast_indices
                            and isinstance(value.args[2], ast.Name) and shape(types.get(value.args[2].id, '')) == [S, '2048']
                            and shape(out_type) == [M, '2048'], 'zero/scatter未闭合原索引与M/S')
                    scatters.append(dict(function=scope, line=statement.lineno, target=names, dense=base.id))
    require(sorted(attention) == list(range(42)) and sorted(updates) == list(range(42)), '未保持42 Attention/42旧KV更新')
    require(len(gathers) == 2 and len(projections) == 3 and len(scatters) == 1, '末层双gather/projection/scatter不完整')
    suffix = scatters[0]['function']
    require(all(x['function'] == suffix for x in gathers) and all(x['function'] == suffix for x in projections.values()),
            '末层路径跨未知切分，需按实际图审阅')
    # FX子module的函数通常均名forward，因此使用实际class归属核返回。
    suffix_classes = [c for c in ast.walk(tree) if isinstance(c, ast.ClassDef)
        and any(isinstance(n, ast.AnnAssign) and n.lineno == scatters[0]['line'] for n in ast.walk(c))]
    require(suffix_classes, 'scatter不属于实际FX module')
    leaf = min(suffix_classes, key=lambda c: len(list(ast.walk(c))))
    leaf_forward = next(x for x in leaf.body if isinstance(x, ast.FunctionDef) and x.name == 'forward')
    ret = [n for n in leaf_forward.body if isinstance(n, ast.Return)]
    returned_names = {n.id for n in ast.walk(ret[-1].value) if isinstance(n, ast.Name)} if ret else set()
    require(bool(returned_names & set(scatters[0]['target'] + [scatters[0]['dense']])), '末层返回未依赖dense scatter')
    outputs = []
    for statement in root[0].body:
        if isinstance(statement, (ast.Assign, ast.AnnAssign)) and isinstance(statement.value, ast.Call) and dotted(statement.value.func) == 'self.'+leaf.name:
            targets = statement.targets if isinstance(statement, ast.Assign) else [statement.target]
            outputs.extend(t.id for t in targets if isinstance(t, ast.Name))
    returned = [n for n in root[0].body if isinstance(n, ast.Return)]
    require(len(outputs) == 1 and returned and any(isinstance(n, ast.Name) and n.id == outputs[0] for n in ast.walk(returned[-1].value)), '入口返回未连接唯一末层module')
    chain = verify_provenance(tree)
    return dict(M=M, S=S, attention_layers=sorted(attention), kv_update_layers=sorted(updates), provenance=chain,
                gathers=gathers, projections=projections, scatters=scatters, o_proj_pruned=True, unbacked_samples=True,
                limitation='静态typed FX接线，不代表编译核数值/完整准确率或端到端收益')
