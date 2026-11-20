"""将每个实际tt.dot的B SSA值关联到local_load的同一dot_op布局声明。"""
import re


def b_sme_contract(text):
    aliases={}
    for name,body in re.findall(r'(?m)^\s*(#[\w.-]+)\s*=\s*#ttg\.dot_op<\{([^}]*)\}>',text):
        aliases[name]=body
    loads={}
    for line in text.splitlines():
        found=re.match(r'^\s*(%[\w.$#-]+)\s*=\s*ttg\.local_load\b.*?\s->\s(.+)$',line)
        if not found:continue
        value,destination=found.groups()
        inline=re.findall(r'#ttg\.dot_op<\{([^}]*)\}>',destination)
        layouts=inline+[body for name,body in aliases.items()
                        if re.search(re.escape(name)+r'(?![\w.-])',destination)]
        loads[value]=layouts
    records=[]
    for a,b in re.findall(r'\btt\.dot\s+(%[\w.$#-]+)\s*,\s*(%[\w.$#-]+)\s*,',text):
        layouts=loads.get(b,[])
        # 两个条件必须来自实际B load所用的同一dot_op声明，不能跨声明拼接。
        matched=[body for body in layouts if re.search(r'\bopIdx\s*=\s*1\b',body)
                 and re.search(r'\buseSme\s*=\s*[12]\b',body)]
        records.append(dict(A=a,B=b,B_local_load_found=b in loads,
                            B_dot_op_layouts=layouts,B_useSme_values=[int(v) for body in layouts for v in re.findall(r'\buseSme\s*=\s*(\d+)\b',body)],B_same_layout_opIdx1_useSme_nonzero=len(matched)==1))
    return dict(passed=bool(records) and all(r['B_same_layout_opIdx1_useSme_nonzero'] for r in records),
                dot_count=len(records),records=records)
