"""只读真实FX：每层融合Q/K/dep必须进入同层原Attention，禁止旧KV update。"""
import ast
import re

def dotted(node):
    if isinstance(node,ast.Name): return node.id
    if isinstance(node,ast.Attribute): return dotted(node.value)+'.'+node.attr
    return ''

def require(ok,message):
    if not ok:raise ValueError(message)

def layer_number(node):
    require(isinstance(node,ast.Constant) and isinstance(node.value,str),'FX layer_name不是已知固定字符串')
    match=re.fullmatch(r'model\.layers\.(\d+)\.self_attn\.attn',node.value)
    require(match is not None,'FX layer_name不符MiniCPM实例')
    return int(match.group(1))

def inspect_graph(text):
    tree=ast.parse(text);fusions=[];consumers=[];old=[]
    fusion_ops={'torch.ops.vllm.biv150_rope_kv','torch.ops.vllm.biv150_rope_kv.default'}
    attention_ops={'torch.ops.vllm.unified_attention_with_output','torch.ops.vllm.unified_attention_with_output.default'}
    update_ops={'torch.ops.vllm.unified_kv_cache_update','torch.ops.vllm.unified_kv_cache_update.default'}
    for node in ast.walk(tree):
        if isinstance(node,ast.Call) and dotted(node.func) in update_ops:old.append(node.lineno)
    require(not old,'真实FX仍有旧unified_kv_cache_update: '+repr(old))
    for fn in (n for n in ast.walk(tree) if isinstance(n,ast.FunctionDef)):
        aliases={};outputs={}
        def origin(value):
            if isinstance(value,ast.Name):return aliases.get(value.id)
            if isinstance(value,ast.Subscript) and isinstance(value.value,ast.Name):
                base=outputs.get(value.value.id)
                if base is not None and isinstance(value.slice,ast.Constant) and type(value.slice.value) is int:
                    return (base,value.slice.value)
            if isinstance(value,ast.Call):
                if dotted(value.func) in ('operator.getitem','getitem') and len(value.args)==2:
                    return origin(ast.Subscript(value=value.args[0],slice=value.args[1],ctx=ast.Load()))
                if isinstance(value.func,ast.Attribute) and value.func.attr in ('view','reshape','flatten'):
                    return origin(value.func.value)
            return None
        for statement in fn.body:
            if isinstance(statement,(ast.Assign,ast.AnnAssign)):
                targets=statement.targets if isinstance(statement,ast.Assign) else [statement.target]
                value=statement.value
            elif isinstance(statement,ast.Expr):targets=[];value=statement.value
            else:continue
            if isinstance(value,ast.Call) and dotted(value.func) in fusion_ops:
                require(len(value.args)==4 and len(targets)==1,'融合op调用/返回绑定非预期')
                layer=layer_number(value.args[3]);key=(fn.lineno,statement.lineno)
                fusions.append({'key':list(key),'layer':layer,'line':statement.lineno})
                target=targets[0]
                if isinstance(target,ast.Name):outputs[target.id]=key
                elif isinstance(target,(ast.Tuple,ast.List)):
                    require(len(target.elts)==3 and all(isinstance(x,ast.Name) for x in target.elts),'融合tuple绑定非法')
                    for i,x in enumerate(target.elts):aliases[x.id]=(key,i)
                else:raise ValueError('融合返回未命名')
                continue
            if isinstance(value,ast.Call) and dotted(value.func) in attention_ops:
                require(len(value.args)>=5,'原Attention参数缺失')
                layer=layer_number(value.args[4]);dep=[k.value for k in value.keywords if k.arg=='kv_cache_dummy_dep']
                require(len(dep)==1,'原Attention缺少唯一显式dep')
                q,k,d=origin(value.args[0]),origin(value.args[1]),origin(dep[0])
                require(q is not None and k is not None and d is not None
                        and q[0]==k[0]==d[0] and (q[1],k[1],d[1])==(0,1,2),
                        'Q/K/dep没有来自同一个融合op的0/1/2返回')
                match=[x for x in fusions if tuple(x['key'])==d[0]]
                require(len(match)==1 and match[0]['layer']==layer,'融合dep接入另一层Attention')
                consumers.append({'fusion_key':list(d[0]),'layer':layer,'line':statement.lineno})
            provenance=origin(value)
            for target in targets:
                if isinstance(target,ast.Name):
                    outputs.pop(target.id,None)
                    if provenance is None:aliases.pop(target.id,None)
                    else:aliases[target.id]=provenance
    require(len(fusions)==42 and sorted(x['layer'] for x in fusions)==list(range(42)),
            '真实FX未包含唯一42层rope_kv')
    require(len(consumers)==42 and sorted(x['layer'] for x in consumers)==list(range(42))
            and sorted(x['fusion_key'] for x in consumers)==sorted(x['key'] for x in fusions),
            '融合返回与42层原Attention消费未一一闭合')
    return {'fusion_count':42,'old_update_count':0,'attention_consumers':42,
            'layers':list(range(42)),'q_k_dep_from_same_fusion':True,'fusions':fusions,'consumers':consumers}
