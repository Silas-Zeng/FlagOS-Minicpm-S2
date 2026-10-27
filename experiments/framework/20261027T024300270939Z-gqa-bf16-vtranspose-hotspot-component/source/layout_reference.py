"""整数位型CPU参考；仅变更地址，不经过浮点转换。"""
import numpy as np


def offsets(kind, head, slot):
    dims = np.arange(128, dtype=np.int64)
    if kind == 0:
        return slot * 256 + head * 128 + dims
    return 4096 + head * 2048 + dims * 16 + slot


def pack(bits):
    assert bits.dtype == np.uint16 and bits.shape[1:] == (2, 16, 2, 128)
    out = np.empty((len(bits), 8192), dtype=np.uint16)
    out[:, :4096] = bits[:, 0].reshape(-1, 4096)
    out[:, 4096:] = bits[:, 1].transpose(0, 2, 3, 1).reshape(-1, 4096)
    return out


def unpack(bits):
    assert bits.dtype == np.uint16 and bits.shape[1:] == (8192,)
    out = np.empty((len(bits), 2, 16, 2, 128), dtype=np.uint16)
    out[:, 0] = bits[:, :4096].reshape(-1, 16, 2, 128)
    out[:, 1] = bits[:, 4096:].reshape(-1, 2, 128, 16).transpose(0, 3, 1, 2)
    return out
