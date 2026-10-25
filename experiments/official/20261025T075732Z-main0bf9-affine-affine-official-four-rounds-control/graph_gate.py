"""原测量wrapper接口适配到已审527图门；不新增请求。"""
from pathlib import Path
import affine_graph_gate
def capture(run, source, role, verification_control, env):
    if role != 'main':
        raise ValueError('复用测量driver角色必须为main；527方法身份由真实图核定')
    return affine_graph_gate.capture(Path(run), Path(source), env, Path(verification_control))
