
    # _biv150_noop_allocate_v1
    try:
        from vllm_fl.patches.biv150_noop_allocate import install as _install_noop_allocate
        _install_noop_allocate(enabled=True)
    except Exception as _noop_error:
        try:
            print("BIV150_ALLOCATOR_NOOP_REJECTED " + type(_noop_error).__name__, flush=True)
        except Exception:
            pass
