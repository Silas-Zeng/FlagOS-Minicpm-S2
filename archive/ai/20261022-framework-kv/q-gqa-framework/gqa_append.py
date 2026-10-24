
# Dedicated GQA decode attention kernel. Installed after the mixed-decode split so
# it wraps the function reference the split already bound; the split and the w2s1
# launch policy stay in front of it and still serve every path this kernel declines.
if getattr(current_platform, "vendor_name", None) == "iluvatar":
    from vllm_fl.patches.biv150_gqa_decode import install as _install_gqa_decode

    print("BIV150_GQA_DECODE_INSTALL", _install_gqa_decode(), flush=True)
