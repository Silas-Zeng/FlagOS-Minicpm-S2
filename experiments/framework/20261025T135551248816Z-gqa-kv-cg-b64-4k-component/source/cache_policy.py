"""实际 CoreX 访存指令证据；不把 PTX 文档直接等同 BI-V150 行为。"""
import re


def cache_evidence(baseline, candidate):
    def loads(text):
        result = []
        for line in text.splitlines():
            instruction = line.split(";", 1)[0].strip()
            if re.match(r"(?:ml|sl)_lsa_(?:blkload|load)_", instruction):
                result.append(re.sub(r"\s+", " ", instruction))
        return result

    a, b = loads(baseline), loads(candidate)
    cg = lambda rows: [line for line in rows if re.search(r",\s*cg\s*$", line)]
    if not a or not b:
        raise RuntimeError("没有可识别的实际 CoreX LSA load 指令；保留原件，不计时")
    if a == b or not cg(b) or len(cg(b)) <= len(cg(a)):
        raise RuntimeError(".cg 未形成新增机器读指令，或 load 指令相同；保留原件，不计时")
    return dict(baseline_load_count=len(a), candidate_load_count=len(b),
                baseline_cg_count=len(cg(a)), candidate_cg_count=len(cg(b)),
                candidate_cg_instructions=cg(b), machine_loads_differ=True,
                limitation="证明编译结果有 cg load；不声称已测缓存命中率或物理 L1 行为")
