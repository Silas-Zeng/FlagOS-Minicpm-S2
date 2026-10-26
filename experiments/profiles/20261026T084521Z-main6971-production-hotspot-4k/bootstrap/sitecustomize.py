import importlib.abc, importlib.machinery, os, sys
if os.environ.get("BIV150_PROFILE_DIR") and not os.environ.get("BIV150_PROFILE_BOOTSTRAP"):
    _WORKER_MODULE = "vllm_fl.worker.worker"

    def _wrap_worker(module):
        import functools
        original_init = module.WorkerFL.__init__
        if getattr(original_init, "_biv150_deferred_install", False):
            return

        @functools.wraps(original_init)
        def initialize_worker(self, *args, **kwargs):
            # Executed only when a real WorkerFL is constructed, before its
            # initialization, device/model loading, capture, and step_fn binding.
            import json
            from pathlib import Path
            import biv150_profile_service
            biv150_profile_service.install()
            package = sys.modules["vllm_fl"]
            record = {"pid": os.getpid(), "python": sys.executable,
                      "bootstrap_kind": "worker_init",
                      "instrumentation": biv150_profile_service.__file__,
                      "vllm_fl_origin": getattr(package, "__file__", None),
                      "worker_origin": module.__file__,
                      "native_library": os.environ.get("BIV150_NATIVE_W8A8_LIBRARY")}
            target = Path(os.environ["BIV150_PROFILE_DIR"]) / ("bootstrap-%d.json" % os.getpid())
            temporary = target.with_name(target.name + ".tmp")
            temporary.write_text(json.dumps(record, indent=2))
            temporary.replace(target)
            return original_init(self, *args, **kwargs)

        initialize_worker._biv150_deferred_install = True
        module.WorkerFL.__init__ = initialize_worker

    class _WorkerLoader(importlib.abc.Loader):
        def __init__(self, loader):
            self.loader = loader

        def create_module(self, spec):
            create = getattr(self.loader, "create_module", None)
            return None if create is None else create(spec)

        def exec_module(self, module):
            self.loader.exec_module(module)
            _wrap_worker(module)

        def __getattr__(self, name):
            return getattr(self.loader, name)

    class _WorkerFinder(importlib.abc.MetaPathFinder):
        _biv150_worker_bootstrap = True

        def find_spec(self, fullname, path=None, target=None):
            if fullname != _WORKER_MODULE:
                return None
            spec = importlib.machinery.PathFinder.find_spec(fullname, path, target)
            if spec is not None and spec.loader is not None:
                spec.loader = _WorkerLoader(spec.loader)
            return spec

    if not any(getattr(finder, "_biv150_worker_bootstrap", False) for finder in sys.meta_path):
        sys.meta_path.insert(0, _WorkerFinder())
