#!/usr/bin/env python3
"""仅从既有登记生成中文团队视图；不修改/重验实验原件。"""
import csv
import hashlib
import io
import json
import os
from pathlib import Path
import re
from urllib.parse import quote

ROOT = Path(__file__).resolve().parents[1]
TEAM = ROOT / 'team'
MARK = '<!-- 自动生成：python scripts/build_team_view.py；登记源 experiments/registry.csv -->\n\n'
GROUPS = {
    'cpu-combination': ('CPU metadata + async token 组合', '两种CPU准备方法的组合；方法正确性与短服务性能分别记录。', ['cpu-metadata', 'async-token-update']),
    'cpu-metadata': ('CPU metadata 复用', '复用已计算的CPU视图，写回原GPU缓冲区；回退和事件边界见原报告。', ['cpu-metadata']),
    'async-token': ('异步 token 更新', '整数gather/scatter更新；既有索引、stream和回退条件保留。', ['async-token-update']),
    'kv-pitched': ('KV 二维 SAVE 复制', '保留KV字节和逻辑顺序的正等差复制；单层信号与真实42层诊断分开看。', ['kv-pitched-copy']),
    'kv-contiguous': ('KV 连续页复制', '连续页合并提交工具；提交不是完成ACK，工具与服务协议分开看。', ['kv-contiguous-copy']),
    'kv-progress': ('抢占请求选择与进展', '抢占瞬间观察、请求选择及其对照；失配结果也保留。', []),
    'kv-memory': ('KV 启动内存观察', '启动内存组成和容量分项诊断，不作为性能成绩。', []),
    'kv-protocol': ('KV 保存 / 恢复协议', '单victim、容量下界、私有页序与FULL恢复；VERIFY诊断不等于性能。', []),
    'kv-observation': ('KV 生命周期观察', '分配失败、抢占与恢复的观察原件，不自动等于可回收机会。', []),
    'gqa-decode-kernel': ('专用 GQA decode attention kernel', '为 MiniCPM5-2B 的 16Q/2KV、head128、单 token decode 重写的 attention kernel 与其段归约；只在该守卫命中时生效，其余路径走原 kernel。', ['gqa-decode-kernel']),
    'int8-decision': ('int8 与 W8A8 决策测量', '真实形状上的 int8 GEMM、W8A16、_int_mm+融合 epilogue 及 QDQ 精度模拟；负结果与候选并存，不混用证据级别。', []),
    'admission': ('准入与输出增长', '准入候选及其负结果、未激活和容量限制。', []),
    'mapped-attention': ('非前缀 decode 映射', '单层构造、服务实际命中与重复结果分开记录。', []),
    'mm-cta': ('矩阵乘 CTA 分组', '固定tile下的映射与守卫诊断；单层收益不外推服务。', []),
    'buffers': ('缓冲区 gather 与 token bucket', '输入几何、padding和缓冲区复用候选。', []),
    'event': ('Event / graph 能力与等待', '能力门、完成性及等待CPU的正负结果。', []),
    'sql': ('SQLite 反射及 SQL+C2/C3 组合', '目标反射与历史组合；#9/#10只用于组合来源导航，组合成绩不能拆分归于单项方法，也不表示#8必须依赖两者。', ['sql-reflection', 'decode3d', 'mixed-attention']),
    'official': ('完整官方吞吐对照', '原版与完整候选的原始官方结果；保留DB、KV和计分边界。', []),
    'attention': ('Attention 分流与 launch', 'prefill、3D decode、mixed分流、可见prefix及重叠等路径；相关PR不等于各实验已包含或独立验证全部方法。', ['prefill', 'decode3d', 'mixed-attention']),
    'early': ('早期集成、块表与 profile', '早期基点、块表提交、集成短筛和profile，不自动作为诊断开关或top-p单项性能。', ['diagnostics', 'top-p']),
    'other': ('其它登记与控制记录', '没有足够字段继续归类的登记；不补猜实验结论。', []),
}
CODE = {
    'gqa-decode-kernel': ['patches/framework/biv150_gqa_decode.py'],
    'cpu-combination': ['docs/pr-preparation/combination-artifacts/resolved/vllm_fl/worker/model_runner.py', 'patches/framework/biv150_cpu_metadata.py', 'patches/framework/biv150_async_token_update.py'],
    'cpu-metadata': ['patches/framework/biv150_cpu_metadata.py'],
    'async-token': ['patches/framework/biv150_async_token_update.py'],
    'kv-contiguous': ['patches/framework/biv150_kv_page_copy.py'],
    'kv-pitched': ['patches/framework/candidates/biv150_kv_pitched_copy.py', 'patches/framework/candidates/biv150_kv_pitched_bridge.cpp'],
    'sql': ['patches/framework/biv150_sql_reflection.py'],
    'event': ['scripts/remote/validate_event_wait_gate.py', 'scripts/remote/validate_native_event_wait_gate.py'],
}


def group(row):
    s = (row['profile_id'] + ' ' + row['run_id']).lower()
    if row['profile_id'] == 'launcher_only':
        parent = BY_ID.get(row['run_id'].removesuffix('-control'))
        return group(parent[0]) if parent else 'other'
    for key, pattern in [
        ('gqa-decode-kernel', r'gqa[_-]decode|gqa_decode_kernel'),
        ('int8-decision', r'int8|intmm|w8a8|w8a16|quantdequant'),
        ('cpu-combination', r'cpu[_-]combination|cpu_metadata_async_token'),
        ('cpu-metadata', r'cpu[_-]metadata'), ('async-token', r'async[_-]token'),
        ('kv-pitched', r'kv[_-]pitched|kv_save_threeway'), ('kv-contiguous', r'kv[_-]page[_-]copy'),
        ('kv-progress', r'progress[_-]victim|preemption[_-]snapshot'), ('kv-memory', r'kv[_-](memory|startup)'),
        ('kv-observation', r'kv[_-]completion'), ('kv-protocol', r'kv[_-]'),
        ('admission', r'growth'), ('mapped-attention', r'mapped[_-]decode'),
        ('mm-cta', r'cta|mm[_-]'), ('buffers', r'hidden|bucket'),
        ('event', r'event'), ('official', r'official|original13eb'),
        ('sql', r'sql'), ('attention', r'attention|mixed|decode_launch|direct_decode|\bc[23]\b'),
        ('early', r'\bb[0o]\b|\bc1\b|native[_-]decode|dirty_block_table|host[_-]gap'),
    ]:
        if re.search(pattern, s):
            return key
    return 'other'


def platform(row):
    value = row['device'].strip()
    return {'Iluvatar BI-V150': ('bi-v150', '天数 BI-V150'), 'CPU': ('cpu', 'CPU')}.get(
        value, ('unrecorded', value or '未记录'))


def link(target, current, label):
    rel = Path(os.path.relpath(target, current.parent)).as_posix()
    return '[' + label.replace(']', '') + '](' + quote(rel, safe='/.-_') + ')'


def cell(value):
    return str(value or '未记录').replace('|', '\\|').replace('\n', ' ')


def brief(value, limit=220):
    value = re.sub(r'\s+', ' ', value or '').strip()
    if not value:
        return '未记录'
    # 只摘录原句，不计算/改判结果；优先结果句，并带其适用边界。
    clauses = [x.strip() for x in re.split('[。；]', value) if x.strip()]
    metric = next((x for x in clauses if re.search(r'%|pct|倍|无CPU下降|未见.*收益', x)), None)
    chosen = [metric] if metric else [next((x for x in clauses if re.search('失败|通过|不支持|未激活|不报', x)), clauses[0])]
    boundary = next((x for x in clauses if x not in chosen and re.search('非稳定|非E2E|不外推|仅.*诊断|未.*accuracy|不继承|不报.*收益', x)), None)
    if boundary:
        chosen.append(boundary)
    value = '；'.join(chosen)
    value = re.sub(r'\b[0-9a-f]{32,64}\b', '〔标识见原件〕', value)
    value = value[:limit] + ('…' if len(value) > limit else '')
    return value if re.search('[\u4e00-\u9fff]', value) else '原记录：' + value


def result(row, limit=190):
    """只摘结果/失败原句，不把审计与库身份搬入主视图。"""
    note = re.sub(r'\s+', ' ', row['conclusion']).strip()
    if row['profile_id'] == 'launcher_only':
        return '启动或收集记录，实验结果见对应主run。'
    clauses = [x.strip() for x in re.split(r'[。；;]', note) if x.strip()]
    positive = next((x for x in clauses if re.search(r'(?i)(?:TPS|TTFT|吞吐|耗时|wall|event)\s*(?:[+−-]\d|省\d|提升|降低)|\d+(?:\.\d+)?(?:%|pct|倍)|throughput factor\s+\d', x)), None)
    negative = next((x for x in clauses if re.search(r'无CPU下降|未见.*收益|无正信号|不支持.*收益|未激活|未命中|失败|遮蔽.*循环', x)), None)
    correctness = next((x for x in clauses if re.search(r'字段.*过|checks.*(?:过|true)|全bytes|全字节|bitwise|RNG.*(?:同|过|true)|输出.*通过|正确性.*通过', x, re.I)), None)
    choice = positive or negative or correctness
    if not choice:
        measured = re.search(r'\d+(?:\.\d+)?s/\d+(?:\.\d+)?(?:total|TPS)/TTFT\d+(?:\.\d+)?ms', note, re.I)
        choice = measured[0] if measured else (clauses[0] if clauses else '')
    if not choice:
        return '结果未单列；见原始记录。'
    # 从语义结果开始，不展示前置的SHA、seal、源码数、审计话术。
    start = re.search(r'(?i)TPS[+−-]|TTFT[+−-]|吞吐|耗时|wall|event|无CPU下降|未见|无正信号|未激活|未命中|\d+\s*成功\s*[/,，]?\s*\d+\s*失败|\d+\s*失败|失败|遮蔽|五case|两case|四case|\d+checks|全bytes|全字节|bitwise|RNG|字段|输出', choice)
    text = choice[start.start():] if start else choice
    text = re.sub(r'(?i)\b[0-9a-f]{8,64}\b(?=[^\w.]|$)', lambda m: '' if re.search('[a-f]', m[0], re.I) else m[0], text)
    text = re.sub(r'(?i)\d+seal|\b(?:SHA|schema|logical)[^，,；。 ]*|审计[^：:]*[：:]|后验[^：:]*[：:]', '', text)
    text = text.strip(' ，,：:/')
    # 结果正文限长；适用限制单独保留，不能在截断时把限制一并丢掉。
    boundary_pattern = r'非稳定|非E2E|不外推|不作.*归因|不报.*收益|不继承|无新accuracy|未.*accuracy|(?:DB|KV).*不同|(?:DB|KV).*未.*(?:快照|匹配)|not snapshotted|no (?:stable|model|new accuracy)|no .*comparison|never ready'
    boundaries = [x for x in clauses if re.search(boundary_pattern, x, re.I)]
    summary = text[:limit] + ('…' if len(text) > limit else '') if text else clauses[0][:limit]
    missing = [x for x in boundaries if x not in summary and not (x.endswith(text) and len(text) <= limit)]
    if missing:
        # 首段结果与至多两条直接限制即可导航；其它细节仍在完整原登记。
        summary += '；' + '；'.join(missing[:2])
        if len(missing) > 2:
            summary += '；其余限制见完整原登记'
    return summary


def keep(row):
    text = row['conclusion']
    state = row['status'].lower()
    if row['profile_id'] == 'launcher_only':
        return '保留作过程记录。'
    if re.search(r'baseline|reference|original13eb|^b0$', row['profile_id'], re.I):
        return '保留作对照基线；不据此判断候选收益。'
    if re.search(r'failed|reject|error|no_.*cpu_reduction', state) or re.search(r'不集成|未集成|不启用|不服务集成|无CPU下降|未见.*收益|无正信号', text):
        return '未集成；失败或无收益记录保留。'
    if 'positive_signal' in state or re.search(r'信号.{0,8}保留|保留.{0,8}候选|小收益.{0,8}保留', text):
        return '保留作候选，仍待确认；不等于默认启用。'
    return '待确认；通过某项检查不自动等于优化保留。'


def how(row):
    phase = row['phase'].lower()
    if row['profile_id'] == 'launcher_only':
        return '只记录启动、日志或封存，不单独测性能。'
    kind = next((label for pattern, label in [
        ('official', '原官方吞吐对照'), ('accuracy', '准确率门'), ('profile', '性能分析诊断'),
        ('gate|correctness|byte', '局部正确性或能力门'), ('smoke|startup|descriptor', '启动或描述符诊断'),
        ('context|screen|decode|4k|16k', '真实服务短负载')]
        if re.search(pattern, phase)), '具体测法未单列，见原命令')
    shape = ' / '.join(row[key] or '未记录' for key in ('input_len', 'output_len', 'concurrency', 'num_prompts'))
    return kind + '；输入 / 输出 / 并发 / 请求数：' + shape + '。'


def code_links(key, page):
    paths = [ROOT / x for x in CODE.get(key, ['patches/framework']) if (ROOT / x).exists()]
    return '；'.join(link(x, page, x.name) for x in paths) or '未单列，见原件源码清单'


def status(row):
    value = row['status'].lower()
    for needle, text in [('confounded', '不可直接比较'), ('inconclusive', '结论未定'),
                         ('not_activated', '未激活'), ('no_activation', '未激活'),
                         ('failed', '失败/未通过'), ('reject', '失败/未通过'),
                         ('error', '失败/未通过'),
                         ('partial', '部分记录'), ('running', '进行中'), ('pending', '待处理'),
                         ('complete', '已完成'), ('pass', '通过'), ('candidate', '候选，见短记'),
                         ('integration_only', '仅集成记录'), ('launch', '启动/控制记录'),
                         ('profile', '诊断记录')]:
        if needle in value:
            return text
    return '已登记，见短记' if row['status'] else '未记录'


def write(path, text):
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.exists() and not path.read_text(encoding='utf-8').startswith(MARK):
        raise RuntimeError('不覆盖人工文件：' + str(path))
    path.write_text(MARK + text.rstrip() + '\n', encoding='utf-8', newline='\n')
    GENERATED.append(path.relative_to(ROOT).as_posix())


def evidence(rows):
    folders = [ROOT / r['artifacts'] for r in rows if r['artifacts']]
    folders = list(dict.fromkeys(p for p in folders if p.is_dir()))
    commands, manifests, raw, logs = [], [], [], []
    for folder in folders:
        control = folder.with_name(folder.name + '-control')
        for base in (folder, control):
            if not base.is_dir():
                continue
            commands += [base / n for n in ('command.json', 'command.txt', 'benchmark-command.json', 'load-commands.json', 'launch-command.json', 'launch.sh') if (base / n).is_file()]
            manifests += [base / n for n in ('manifest.json', 'purpose.json', 'source-sha256.json', 'postflight-full.json', 'postflight.json') if (base / n).is_file()]
        raw += [folder / n for n in ('results.json', 'result.json') if (folder / n).is_file()]
        raw += [p for pattern in ('*/results/*.json', '*/results/*.csv', '*.csv', '*/*.csv') for p in folder.glob(pattern) if p.name != 'gpu.csv' and 'source' not in p.parts]
        logs += [folder / n for n in ('server.log', 'worker.log', 'gate.log', 'gpu.csv', 'exit-code') if (folder / n).is_file()]
    return folders, {'原命令': commands, '环境 / 源码 / 后态': manifests, '原始结果': raw, '日志 / 采样': logs}


def main():
    global BY_ID, GENERATED
    GENERATED = []
    registry = ROOT / 'experiments/registry.csv'
    raw = registry.read_bytes()
    rows = list(csv.DictReader(io.StringIO(raw.decode('utf-8'))))
    BY_ID = {}
    for index, row in enumerate(rows, 1):
        row['_index'] = index
        BY_ID.setdefault(row['run_id'], []).append(row)
    # 相关说明只建立既有链接，不重算其结论或审计证据。
    reports = {}
    for p in (ROOT / 'analysis').glob('*.md'):
        for rid in set(re.findall(r'20\d{6}T\d{6}Z-[A-Za-z0-9_-]+', p.read_text(encoding='utf-8', errors='replace'))):
            if rid in BY_ID:
                reports.setdefault(rid, []).append(p)
    prs = {}
    receipt = ROOT / 'docs/pr-preparation/publication-receipt.json'
    if receipt.is_file():
        prs = {p['method']: p['url'] for p in json.loads(receipt.read_text(encoding='utf-8'))['pull_requests']}
    # root已实际创建的新PR；仅导航，不改变原实验的归因/依赖/准确率。
    prs.update({method: 'https://github.com/Silas-Zeng/FlagOS-S2-vllm-plugin-FL/pull/' + str(number)
                for method, number in [('diagnostics', 5), ('prefill', 6), ('top-p', 7),
                                       ('sql-reflection', 8), ('decode3d', 9), ('mixed-attention', 10)]})
    pr_labels = {'cpu-metadata': 'CPU metadata #1', 'async-token-update': '异步token更新 #2',
                 'kv-contiguous-copy': '连续页KV工具 #3', 'kv-pitched-copy': '二维SAVE工具 #4',
                 'diagnostics': '诊断配置 #5', 'prefill': 'prefill #6', 'top-p': 'top-p #7',
                 'sql-reflection': 'SQL反射 #8', 'decode3d': '3D decode #9', 'mixed-attention': 'mixed Attention #10'}
    run_pages, buckets = {}, {key: [] for key in GROUPS}
    for rid, records in BY_ID.items():
        slug, hardware = platform(records[0])
        page = TEAM / 'runs' / slug / (rid + '.md')
        run_pages[rid] = page
        body = '# ' + rid + '\n\n平台：' + hardware + '。本页只摘录既有登记；未记录字段不补猜。\n\n'
        for row in records:
            key = group(row)
            buckets[key].append(row)
            body += '## 登记 #' + str(row['_index']) + ' · ' + GROUPS[key][0] + '\n\n'
            body += '- **尝试**：' + GROUPS[key][1] + '\n'
            body += '- **改动**：相关实现 ' + code_links(key, page) + '；本轮准确变体以原件源码清单为准。\n'
            body += '- **怎么测**：' + how(row) + '\n'
            body += '- **结果**：' + cell(result(row)) + '\n'
            body += '- **是否保留**：' + keep(row) + '\n\n'
            body += '<details><summary>完整原登记（含UTC、状态、过程与标识）</summary>\n\n```json\n' + json.dumps({k: v for k, v in row.items() if not k.startswith('_')}, ensure_ascii=False, indent=2) + '\n```\n\n</details>\n\n'
        folders, links = evidence(records)
        body += '## 原件与说明\n\n'
        body += '- 原始目录：' + ('；'.join(link(p, page, p.name) for p in folders) or '未记录') + '\n'
        for label, paths in links.items():
            paths = list(dict.fromkeys(paths))[:8]
            body += '- ' + label + '：' + ('；'.join(link(p, page, p.name) for p in paths) or '未单列，见原始目录') + '\n'
        related = sorted(reports.get(rid, []), key=lambda p: (rid.split('T')[1][:6] not in p.name, 'framework-experiments' in p.name, len(p.name)))[:3]
        body += '- 相关说明：' + ('；'.join(link(p, page, p.stem) for p in related) or '未记录') + '\n'
        body += '- 完整原登记：' + link(registry, page, 'registry.csv') + '（登记序号见上；同一run可有多个阶段）\n'
        write(page, body)
    table = TEAM / 'experiments.md'
    text = '# 实验总表\n\n唯一登记源：' + link(registry, table, 'registry.csv') + '。共' + str(len(rows)) + '条登记、' + str(len(BY_ID)) + '个run；同一run的不同阶段保留。设备空白显示未记录，不自动归平台。\n\n'
    text += '| 平台 | 登记 | UTC开始 | 方法 | 状态 | 输入/输出/并发/请求 | 原登记摘录 | 每轮短记与原件 |\n|---|---:|---|---|---|---|---|---|\n'
    for row in sorted(rows, key=lambda r: (platform(r)[0], r['_index'])):
        key = group(row)
        text += '| ' + platform(row)[1] + ' | ' + str(row['_index']) + ' | ' + cell(row['utc_start']) + ' | ' + link(TEAM / 'methods' / (key + '.md'), table, GROUPS[key][0]) + ' | ' + cell(status(row)) + ' | ' + '/'.join(row[k] or '未记录' for k in ('input_len', 'output_len', 'concurrency', 'num_prompts')) + ' | ' + cell(result(row, 110)) + ' | ' + link(run_pages[row['run_id']], table, row['run_id']) + ' |\n'
    write(table, text)
    for key, (title, description, methods) in GROUPS.items():
        records = buckets[key]
        if not records:
            continue
        page = TEAM / 'methods' / (key + '.md')
        text = '# ' + title + '\n\n' + description + '\n\n'
        text += '相关代码：' + code_links(key, page) + '。\n\n'
        text += '相关方法PR：' + ('；'.join('[' + pr_labels.get(method, method) + '](' + prs[method] + ')' for method in methods if method in prs) or '未记录') + '。\n\n'
        text += '下列是既有登记摘要，不叠加单项收益、不把诊断当端到端或完整准确率。完整条件沿每轮原件查阅。\n\n'
        for slug in ('bi-v150', 'cpu', 'unrecorded'):
            subset = [r for r in records if platform(r)[0] == slug]
            if not subset:
                continue
            text += '## ' + platform(subset[0])[1] + '\n\n'
            for row in subset:
                text += '- ' + link(run_pages[row['run_id']], page, row['run_id']) + '（登记#' + str(row['_index']) + '）：' + cell(result(row, 150)) + ' **是否保留：** ' + keep(row) + '\n'
            text += '\n'
        write(page, text)
    for slug, label in [('bi-v150', '天数 BI-V150'), ('c500', '沐曦－曦云 C500'), ('cpu', 'CPU'), ('unrecorded', '未记录平台')]:
        page = TEAM / 'platforms' / (slug + '.md')
        subset = [r for r in rows if platform(r)[0] == slug]
        text = '# ' + label + '\n\n'
        text += ('现有登记' + str(len(subset)) + '条。打开' + link(table, page, '唯一实验总表') + '查看平台列和每轮原件。\n\n') if subset else '当前registry无该平台登记，不引用其它平台成绩。\n\n'
        text += '\n'.join('- ' + link(TEAM / 'methods' / (key + '.md'), page, GROUPS[key][0]) for key in GROUPS if any(group(r) == key for r in subset))
        write(page, text)
    archive = TEAM / 'archive-index.md'
    write(archive, '# 详细记录与 AI 交接归档入口\n\n这里只建立入口，不搬动原文件，固定脚本/manifest路径继续有效。\n\n' + '\n'.join('- ' + link(ROOT / path, archive, title) for path, title in [
        ('docs/agent-work-index.md', '子智能体交接索引'), ('docs/agent-work', '各智能体完整工作记录'),
        ('CURRENT_WORK.md', '当前工作与API交接'), ('analysis', '详细研究、过程稿与长报告'),
        ('analysis/source', '独立审计JSON、源码摘录与机器记录'), ('experiments/framework', '框架实验原件'),
        ('experiments/official', '官方吞吐原件'), ('experiments/accuracy', '准确率原件'),
        ('experiments/source-audits', '实际安装源码只读取证'), ('docs/pr-preparation', '早期PR材料与组合证据'),
        ('docs/pr-rebuild', '原始基线与方法PR重建材料'), ('docs/github-publications', '完整发布回执')
    ] if (ROOT / path).exists()))
    home = TEAM / 'README.md'
    write(home, '# 团队实验导航\n\n先看' + link(table, home, '唯一实验总表') + '，再打开每轮短记和原始证据。登记源保持为registry，不另造成绩或补猜缺字段。\n\n## 按平台\n\n' + '\n'.join('- ' + link(TEAM / 'platforms' / (slug + '.md'), home, label) for slug, label in [('bi-v150', '天数 BI-V150'), ('c500', '沐曦－曦云 C500'), ('cpu', 'CPU'), ('unrecorded', '设备字段未记录')]) + '\n\n## 按方法\n\n' + '\n'.join('- ' + link(TEAM / 'methods' / (key + '.md'), home, GROUPS[key][0]) for key in GROUPS if buckets[key]) + '\n\n' + link(archive, home, 'AI交接、详细SHA及过程稿归档入口') + '\n\n更新：`python scripts/build_team_view.py`。仅重建本目录自动视图，不修改登记和证据。')
    assert registry.read_bytes() == raw
    write(TEAM / 'generated-index.md', '# 自动视图来源\n\n登记：`experiments/registry.csv`；SHA256 `' + hashlib.sha256(raw).hexdigest() + '`。\n\n共' + str(len(rows)) + '条登记、' + str(len(BY_ID)) + '个run。程序只读取目录/既有说明建立链接，不重验实验。\n')
    print(json.dumps({'registry_records': len(rows), 'unique_runs': len(BY_ID), 'generated_files': len(GENERATED), 'entry': 'team/README.md', 'registry_unchanged': True}, ensure_ascii=False))


if __name__ == '__main__':
    main()
