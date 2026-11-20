"""原测量wrapper接口适配到已审528图门；不新增请求。"""
from pathlib import Path
import rope_graph_gate
def capture(run, source, role, verification_control, env):
    if role != 'main':
        raise ValueError('复用测量driver角色必须为main；528方法身份由真实图核定')
    return rope_graph_gate.capture(Path(run), Path(source), env, Path(verification_control))
