
    # _biv150_finite_growth_admission_opt_in
    import os as _finite_os
    if _finite_os.environ.get("BIV150_FINITE_GROWTH_ADMISSION") == "1":
        try:
            from vllm_fl.patches.biv150_finite_growth_admission import install as _finite_install
            _finite_result = _finite_install(enabled=True)
            if _finite_result.get("installed") is not True:
                raise RuntimeError("finite growth scope rejected")
        except Exception:
            try:
                print("BIV150_FINITE_GROWTH_ADMISSION_REJECTED", flush=True)
            except Exception:
                pass
