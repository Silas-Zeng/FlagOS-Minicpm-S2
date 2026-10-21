"""仅给 exact SQL+C3 runner 追加独立 gate-up CTA 实现入口；无设备导入。"""
import hashlib

EXPECTED_RUNNER = "e155a16669e69b7eb7aff370dbcbcf225a4f593fa42b2399722e96999b53a1f1"
EXPECTED_POLICY = "06c7cd9216907886e7d66a81d4fd5d9f78edef9daac2380ca263ce8c1770b8e1"
FOOTER = b'''
# _biv150_mm_cta_group_service_v1
if getattr(current_platform, "vendor_name", None) == "iluvatar":
    from vllm_fl.patches.biv150_mm_cta_group_service import install as _install_mm_cta_group
    print("BIV150_MM_CTA_GROUP_INSTALLED", _install_mm_cta_group(ModelRunnerFL), flush=True)
'''


def transform_source(source: bytes) -> bytes:
    if hashlib.sha256(source).hexdigest() != EXPECTED_RUNNER:
        raise RuntimeError("CTA service 只接受 exact SQL+C3 runner")
    return source + FOOTER
