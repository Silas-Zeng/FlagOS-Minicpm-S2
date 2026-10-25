"""真实编译产物的固定SIMT机制记录；资源只诊断，不推算动态HBM或占用。"""
import hashlib
import re


def evidence(compiled,arm):
    asm=compiled.asm
    ttgir=asm.get('ttgir','')
    llir=asm.get('llir','')
    machine=asm.get('asm','')
    def field(text,pattern):
        values=re.findall(pattern,text)
        return int(values[0]) if len(set(values))==1 else None
    metadata=compiled.metadata
    def meta(name):
        return metadata.get(name) if isinstance(metadata,dict) else getattr(metadata,name,None)
    num_warps=field(ttgir,r'"ttg\.num-warps"\s*=\s*(\d+)')
    warp_size=field(ttgir,r'"ttg\.threads-per-warp"\s*=\s*(\d+)')
    dot_lines=[line for line in ttgir.splitlines() if re.search(r'\btt(?:g|ng)?\.(?:dot|warp_group_dot|mma)\b',line)]
    mma_lines=[line for line in machine.splitlines() if re.search(r'^\s*(?:[a-z]+_matrix_(?:mad|mma)\w*|(?:wgmma|mma|mfma|wmma)\S*)\s',line)]
    global_loads=[line for line in ttgir.splitlines() if re.search(r'\btt\.load\b',line)]
    global_stores=[line for line in ttgir.splitlines() if re.search(r'\btt\.store\b',line)]
    stores_3d=[line for line in global_stores if re.search(r'tensor<\d+x\d+x\d+x!tt\.ptr',line)]
    layouts=[line for line in ttgir.splitlines() if line.startswith('#') and ('#ttg.blocked' in line or '#ttg.slice' in line or '#ttg.iluvatar_mma' in line)]
    resources={name:field(machine,r'\.'+name+r':\s*(\d+)') for name in
               ('sgpr_count','sgpr_spill_count','vgpr_count','vgpr_spill_count','private_segment_fixed_size')}
    resources.update(shared=meta('shared'),metadata_num_warps=meta('num_warps'),metadata_num_stages=meta('num_stages'))
    hashes={name:hashlib.sha256(value.encode() if isinstance(value,str) else value).hexdigest()
            for name,value in asm.items() if isinstance(value,(str,bytes))}
    valid=bool(ttgir and llir and machine and getattr(compiled,'hash',None) and
               num_warps==8 and warp_size==64 and meta('num_warps')==8 and meta('num_stages')==1
               and not dot_lines and not mma_lines and not stores_3d)
    return dict(valid=valid if arm=='candidate' else None,compiled_hash=getattr(compiled,'hash',None),
        num_warps=num_warps,warp_size=warp_size,resources=resources,asm_sha256=hashes,
        dot_lines=dot_lines,mma_lines=mma_lines,global_3d_stores=stores_3d,layouts=layouts,
        global_loads=global_loads,global_stores=global_stores,
        limitation='源ABI和stores无新增全局3D中间buffer；记录真实布局/地址供读取，不能据静态load行数证明HBM不复制。spill不是失败门，完整ABBA衡量成本。')
