# Isolated MiniCPM decode launch candidate; install before graph capture.
if getattr(current_platform, "vendor_name", None) == "iluvatar":
    from vllm_fl.patches.biv150_decode_launch_runtime import install as _install_decode_launch
    print("BIV150_DECODE_LAUNCH_INSTALLED", _install_decode_launch(), flush=True)
