"""仅标准库：明确量化舍入与独立整数参考，不导入Torch/Triton。"""
import math
import struct

GROUP = 256
INT32_BOUND = GROUP * 127 * 127


def f32(x):
    return struct.unpack('<f', struct.pack('<f', x))[0]


def quantize_group(values):
    if len(values) != GROUP or not all(math.isfinite(x) for x in values):
        raise ValueError('必须是256个有限数')
    values = [f32(x) for x in values]
    peak = max(max(abs(x) for x in values), f32(1.0e-6))
    scale = f32(peak / 127.0)
    result = []
    for x in values:
        u = f32(x / scale)
        r = math.floor(f32(abs(u) + f32(.5)))
        r = -r if u < 0 else r
        result.append(max(-127, min(127, r)))
    return result, scale


def integer_dot(a, b):
    if len(a) != GROUP or len(b) != GROUP:
        raise ValueError('组长度错误')
    if any(type(x) is not int or not -127 <= x <= 127 for x in [*a, *b]):
        raise ValueError('组元素不是合法INT8量化值')
    # Python整数无溢出；刻意不用GPU dot或同一Triton表达式作参考。
    return sum(x * y for x, y in zip(a, b))


def dequantized_dot(a_groups, a_scales, w_groups, w_scales):
    if not (len(a_groups) == len(a_scales) == len(w_groups) == len(w_scales) == 24):
        raise ValueError('必须恰有24组')
    value = f32(0.)
    for aq, sa, wq, sw in zip(a_groups, a_scales, w_groups, w_scales):
        part = integer_dot(aq, wq)
        factor = f32(f32(sa) * f32(sw))
        term = f32(f32(part) * factor)
        value = f32(value + term)
    return value


def output_error(actual, reference):
    if len(actual) != len(reference) or not reference:
        raise ValueError('比较长度不匹配/空比较')
    finite = all(math.isfinite(x) for x in [*actual, *reference])
    if not finite:
        return {'finite': False, 'passed': False}
    error2 = sum((a-b)**2 for a, b in zip(actual, reference))
    norm2 = sum(b*b for b in reference)
    max_ref = max(abs(x) for x in reference)
    relative_l2 = math.sqrt(error2 / max(norm2, 1.e-30))
    normalized_max = max(abs(a-b) for a,b in zip(actual,reference)) / max(max_ref,1.e-15)
    # 预声明工程淘汰线；不等于100/105准确率资格或原BF16逐位合同。
    return dict(finite=True, relative_l2=relative_l2, normalized_max=normalized_max,
                passed=relative_l2 <= .02 and normalized_max <= .05)
