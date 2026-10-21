"""只在exact SQL+C3 runner末尾启用独立prefix-mask实现；无设备导入。"""
import hashlib

EXPECTED_RUNNER = "e155a16669e69b7eb7aff370dbcbcf225a4f593fa42b2399722e96999b53a1f1"
FOOTER = b'''
# _biv150_visible_prefix_service_v1
if getattr(current_platform, "vendor_name", None) == "iluvatar":
    from vllm_fl.patches.biv150_visible_prefix_service import install as _install_visible_prefix
    print("BIV150_VISIBLE_PREFIX_INSTALLED", _install_visible_prefix(ModelRunnerFL), flush=True)
'''


def transform_source(source: bytes) -> bytes:
    if hashlib.sha256(source).hexdigest() != EXPECTED_RUNNER:
        raise RuntimeError("prefix-mask service只接受exact SQL+C3 runner，不能叠CTA/mapped")
    return source + FOOTER
