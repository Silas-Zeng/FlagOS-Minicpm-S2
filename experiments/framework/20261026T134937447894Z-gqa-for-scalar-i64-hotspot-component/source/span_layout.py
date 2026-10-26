def plan_span(shape, strides, storage_offset, storage_elements):
    """合法原4D cache -> 相同data_ptr的连续二维backing span，不复制。"""
    assert len(shape) == len(strides) == 4
    assert shape[1:] == (16, 2, 128)
    assert strides[-1] == 1 and all(s > 0 for s in strides)
    assert all(s % 128 == 0 for s in strides[:-1])
    assert storage_offset >= 0 and storage_elements >= storage_offset
    span = 1 + sum((n - 1) * s for n, s in zip(shape, strides))
    assert span % 128 == 0
    assert storage_offset + span <= storage_elements
    return dict(size=(span // 128, 128), stride=(128, 1),
                storage_offset=storage_offset, span=span,
                row_strides=tuple(s // 128 for s in strides[:-1]))
