"""服务结束后核真实 execute 首次命中；本文件不启动设备、不把安装视为命中。"""
import argparse
import json
from pathlib import Path
import re

MARKER = "BIV150_C3_VIEWS_FIRST_ACTUAL_EXECUTE_SELECTED"


def review(text):
    records = []
    engine_pids = set(map(int, re.findall(r"EngineCore[^\n]*?pid=(\d+)", text)))
    for line in text.splitlines():
        if MARKER in line:
            payload = json.loads(line.split(MARKER, 1)[1].strip())
            if (payload.get("actual_execute") is not True
                    or payload.get("complete_step_return") is not True
                    or payload.get("selected_forward_calls_in_execute", 0) <= 0
                    or payload.get("scheduled_tokens", 0) <= 0
                    or payload.get("pid") not in engine_pids):
                raise RuntimeError("真实 Engine execute 命中记录不完整")
            records.append(payload)
    if len(records) != 1:
        raise RuntimeError("首次真实 execute 命中必须恰有一条；未命中不能称端到端收益")
    return records


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("run_dir", type=Path)
    args = parser.parse_args()
    run = args.run_dir
    if (run / "exit-code").read_text().strip() != "0":
        raise RuntimeError("原短筛未成功退出")
    records = review((run / "server.log").read_text(errors="replace"))
    result = {"actual_execute_selected": True, "records": records,
              "limit": "只证明至少一个真实步骤命中；不是全程覆盖率或性能收益"}
    with (run / "c3views-actual-selection.json").open("x", encoding="utf-8") as stream:
        json.dump(result, stream, ensure_ascii=False, indent=2)
        stream.write("\n")
    print(json.dumps(result, ensure_ascii=False))


if __name__ == "__main__":
    main()
