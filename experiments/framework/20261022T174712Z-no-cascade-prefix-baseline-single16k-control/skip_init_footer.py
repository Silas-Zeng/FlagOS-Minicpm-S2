
    # _biv150_no_cascade_prefix_skip
    import os as _prefix_os
    if _prefix_os.environ.get("BIV150_NO_CASCADE_PREFIX_SKIP") == "1":
        _prefix_skip_handle = None
        try:
            import atexit as _prefix_atexit
            from vllm_fl.patches.biv150_no_cascade_prefix import install as _prefix_skip_install
            _prefix_skip_handle = _prefix_skip_install(enabled=True, mode="skip")
            _prefix_atexit.register(_prefix_skip_handle["restore"])
            print("BIV150_PREFIX_SKIP_CORE_HOOKED mode=skip", flush=True)
        except Exception:
            if _prefix_skip_handle is not None:
                try:
                    _prefix_skip_handle["restore"]()
                except Exception:
                    pass
