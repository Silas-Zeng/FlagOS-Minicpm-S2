# 原件与复现位置

本目录的分析脚本、中文结论和派生表均由既有轨迹生成，没有新 GPU 实验。原始 ixsys 的远端路径、字节数及 SHA 在 receipt.json；文件约394MB，保留在实验机及本地，未复制到 GitHub。

复现时在一个工作区根目录解开 metadata-window.tar.gz（唯一成员及 SHA 见 metadata-archive-receipt.json），将本目录小文件和核验过的 baseline.ixsys 放到该根下 tmp/main6971-existing-timeline-20261027/attempt-20261027T035459Z/，再按 summary.md 运行原脚本。脚本直接校验两个输入 SHA；统计过程和本次已运行版本不变。Windows 的 Python 绝对路径可替换为本机 Python。
