
# BIV150_MIXED_TOKEN_BUCKET_OPT_IN_V1
# Append these exact bytes only to a NEW copy of the frozen 080656 runner.
if getattr(current_platform, "vendor_name", None) == "iluvatar":
    from vllm_fl.patches.biv150_mixed_token_bucket import install as _install_mixed_token_bucket
    print("BIV150_MIXED_TOKEN_BUCKET_INSTALLED",
          _install_mixed_token_bucket(ModelRunnerFL), flush=True)
