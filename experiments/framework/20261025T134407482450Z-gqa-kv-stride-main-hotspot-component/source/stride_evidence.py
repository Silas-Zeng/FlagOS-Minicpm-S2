"""只判实际 CoreX 地址乘法是否被特化掉，不用源码差异代替机器证据。"""
import re


def inspect_asm(text, source):
    page_lines = {i for i, line in enumerate(source.splitlines(), 1)
                  if "page * k_stride_block" in line or "page * v_stride_block" in line}
    if len(page_lines) != 4:
        raise RuntimeError("页寻址源码锚点不符")
    muls, page_muls, cg, ca = [], [], [], []
    current = None
    for raw in text.splitlines():
        loc = re.match(r"\s*\.loc\s+(\d+)\s+(\d+)\s+", raw)
        if loc:
            current = (int(loc[1]), int(loc[2]))
        line = re.sub(r"\s+", " ", raw.split(";", 1)[0].strip())
        if re.match(r"(?:sl|ml)_(?:mul_u64_u32|mull_u32)\b", line):
            muls.append(line)
            if current is not None and current[0] == 1 and current[1] in page_lines:
                page_muls.append(line)
        if re.match(r"(?:ml|sl)_lsa_(?:blkload|load)_", line) and re.search(r",\s*cg$", line):
            cg.append(line)
        if re.match(r"(?:ml|sl)_lsa_(?:blkload|load)_", line) and re.search(r",\s*ca$", line):
            ca.append(line)
    return dict(integer_multiply_count=len(muls), page_multiply_count=len(page_muls),
                page_multiply_instructions=page_muls, cg_load_count=len(cg),
                ca_load_count=len(ca), page_source_lines=sorted(page_lines))


def specialization_evidence(baseline, candidate, base_source, candidate_source):
    a, b = inspect_asm(baseline, base_source), inspect_asm(candidate, candidate_source)
    if not a["ca_load_count"] or not b["ca_load_count"] or a["cg_load_count"] or b["cg_load_count"]:
        raise RuntimeError("双臂未保留原 ca 策略，或意外混入 cg load；保留原件，不计时")
    if not a["page_multiply_count"] or b["page_multiply_count"]:
        raise RuntimeError("未证实实际页地址乘法消除；保留原件，不计时")
    if a["integer_multiply_count"] - b["integer_multiply_count"] < 4:
        raise RuntimeError("实际整数乘法未至少减少四条；不因位置标记改变计收益")
    return dict(baseline=a, candidate=b, page_multiply_loc_count_zero=True, integer_multiply_reduced=True,
                limitation="证明总整数乘法减少且原页源行不再标乘法；不把行号当完整依赖追踪。实际原件留存供窄读，净性能取同原生产 GQA 的 Graph ABBA")
