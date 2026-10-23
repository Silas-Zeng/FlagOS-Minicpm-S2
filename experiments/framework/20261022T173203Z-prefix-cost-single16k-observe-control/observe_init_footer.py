
    # _biv150_prefix_cost_observe_only
    import os as _prefix_os
    if _prefix_os.environ.get("BIV150_PREFIX_COST_OBSERVE") == "1":
        _prefix_observe_handle = None
        try:
            import atexit as _prefix_atexit
            from vllm_fl.patches.biv150_no_cascade_prefix import install as _prefix_observe_install
            _prefix_observe_handle = _prefix_observe_install(enabled=True, mode="observe")
            _prefix_atexit.register(_prefix_observe_handle["restore"])
            print("BIV150_PREFIX_COST_CORE_HOOKED observe_only=1", flush=True)
        except Exception:
            if _prefix_observe_handle is not None:
                try:
                    _prefix_observe_handle["restore"]()
                except Exception:
                    pass
