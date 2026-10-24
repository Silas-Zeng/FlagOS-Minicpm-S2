
    # _biv150_mixed_coverage_only_v1：只诊断实例，保原runner/protocol文件。
    from vllm_fl.patches.biv150_puredecode_native import install as _install_puredecode_native
    _install_puredecode_native(enabled=True, mode='mixed_coverage_only')
