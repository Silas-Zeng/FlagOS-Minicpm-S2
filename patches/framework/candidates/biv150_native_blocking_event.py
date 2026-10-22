"""独立SDK blocking Event薄适配；只显式构造时载桥，导入不触Torch/SDK。

不是服务补丁。owner须显式传实际stream，并强持所有异步资源到sync或失败
device settle。没有__del__隐式销毁；close只在已settled后由owner调用。
"""
import ctypes
import hashlib
from pathlib import Path

EXPECTED_CUDART = "d39d579627d19ddb903855ebc4859661579633a7ecc4d1ad51866d79296ba527"
_CONSTRUCTION_FAILURE_KEEPALIVE = []


class NativeEventError(RuntimeError):
    def __init__(self, operation, code, *, cleanup_code=None):
        self.operation, self.code, self.cleanup_code = operation, code, cleanup_code
        super().__init__(f"SDK Event {operation}失败code={code}, cleanup_code={cleanup_code}; 不降级/不重试")


class NativeEvent:
    def __init__(self, path, *, expected_sha256):
        path = Path(path)
        if (path.is_symlink() or not path.is_file() or type(expected_sha256) is not str
                or len(expected_sha256) != 64
                or hashlib.sha256(path.read_bytes()).hexdigest() != expected_sha256):
            raise RuntimeError("只加载外层已编译/固定SHA的普通Event桥")
        if ctypes.sizeof(ctypes.c_void_p) != 8:
            raise RuntimeError("需要已核64位Corex ABI")
        self.bridge_sha256 = expected_sha256
        self._library = ctypes.CDLL(str(path.resolve(strict=True)))
        abi = self._function("biv150_event_bridge_abi", [], ctypes.c_uint32)
        flags = self._function("biv150_event_creation_flags", [], ctypes.c_uint32)
        if abi() != 1:
            raise RuntimeError("Event桥ABI不符")
        self.creation_flags = int(flags())  # 只读已编译SDK常量，不执行设备probe。
        paths = set()
        for line in Path("/proc/self/maps").read_text(encoding="utf-8").splitlines():
            fields = line.split(None, 5)
            if len(fields) == 6 and "libcudart.so" in Path(fields[5]).name:
                paths.add(Path(fields[5]).resolve(strict=True))
        self.loaded_libcudart = {str(p): hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(paths)}
        if len(paths) != 1 or next(iter(self.loaded_libcudart.values())) != EXPECTED_CUDART:
            raise RuntimeError("实际已加载Corex libcudart身份不符，不另载其它runtime")
        self._create = self._function("biv150_event_create", [ctypes.POINTER(ctypes.c_void_p)])
        self._record = self._function("biv150_event_record", [ctypes.c_void_p, ctypes.c_void_p])
        self._query = self._function("biv150_event_query", [ctypes.c_void_p, ctypes.POINTER(ctypes.c_int)])
        self._synchronize = self._function("biv150_event_synchronize", [ctypes.c_void_p])
        self._destroy = self._function("biv150_event_destroy", [ctypes.c_void_p])
        self._handle = ctypes.c_void_p()
        self._settled, self._closed, self._keepalive = True, False, ()
        code = self._create(ctypes.byref(self._handle))
        if code or not self._handle.value:
            cleanup_code = self._destroy(self._handle) if self._handle.value else None
            if cleanup_code:
                # 构造阶段尚无record；清理失败也不丢handle/动态库，留owner退出清理。
                _CONSTRUCTION_FAILURE_KEEPALIVE.append(self)
            else:
                self._handle = ctypes.c_void_p()
                self._closed = True
            raise NativeEventError("create", code or -1002, cleanup_code=cleanup_code)

    def _function(self, name, args, result=ctypes.c_int):
        function = getattr(self._library, name)
        function.argtypes, function.restype = args, result
        return function

    def _require_open(self):
        if self._closed or not self._handle.value:
            raise RuntimeError("SDK Event已关闭或未构造")

    def record(self, *, stream_handle, keepalive=()):
        self._require_open()
        if (type(stream_handle) is not int or not 0 <= stream_handle < 1 << 64
                or type(keepalive) is not tuple):
            raise ValueError("需要实际原生stream整数与资源tuple")
        if not self._settled:
            raise RuntimeError("不覆盖仍pending/未知完成的SDK Event")
        self._keepalive = keepalive  # 首次可能提交前持资源；错误也不释放。
        self._settled = False
        code = self._record(self._handle, ctypes.c_void_p(stream_handle))
        if code:
            raise NativeEventError("record", code)

    def query(self):
        self._require_open()
        ready = ctypes.c_int()
        code = self._query(self._handle, ctypes.byref(ready))
        if code:
            self._settled = False
            raise NativeEventError("query", code)
        if ready.value not in (0, 1):
            self._settled = False
            raise NativeEventError("query_invalid_ready", -1003)
        self._settled = bool(ready.value)
        return self._settled

    def synchronize(self):
        self._require_open()
        code = self._synchronize(self._handle)
        if code:
            self._settled = False
            raise NativeEventError("synchronize", code)
        self._settled = True

    def close(self, *, owner_settled=False):
        """owner_settled仅可在owner真实device synchronize成功后使用，绝非假ACK。"""
        if self._closed:
            return
        self._require_open()
        if type(owner_settled) is not bool or not (self._settled or owner_settled):
            raise RuntimeError("禁止销毁未settled的SDK Event")
        code = self._destroy(self._handle)
        if code:
            raise NativeEventError("destroy", code)  # handle/keepalive仍留，禁止伪close。
        self._closed, self._settled = True, True
        self._handle = ctypes.c_void_p()
        self._keepalive = ()
