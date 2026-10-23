
    # _biv150_sparse_admission_observer
    import os as _admission_os
    if _admission_os.environ.get("BIV150_ADMISSION_OBSERVE") == "1":
        _admission_handle = None
        try:
            import atexit as _admission_atexit
            from vllm_fl.patches.biv150_admission_observer import install as _admission_install
            _admission_handle = _admission_install(enabled=True)
            _admission_atexit.register(_admission_handle["restore"])
            print("BIV150_ADMISSION_OBSERVER_CORE_HOOKED", flush=True)
        except Exception:
            if _admission_handle is not None:
                try:
                    _admission_handle["restore"]()
                except Exception:
                    pass
