import json, os, sys
from pathlib import Path
try:
    os.setsid()
except PermissionError:
    if os.getsid(0) != os.getpid():
        raise
pid = os.getpid()
if os.getpgrp() != pid or os.getsid(0) != pid:
    raise RuntimeError("service launcher must own its session and group")
fields = Path("/proc/self/stat").read_text().rsplit(")", 1)[1].split()
record = {"pid": pid, "pgid": os.getpgrp(), "sid": os.getsid(0),
          "start_ticks": int(fields[19]), "exec_command": sys.argv[2:]}
target = Path(sys.argv[1])
temporary = target.with_name(target.name + ".tmp")
temporary.write_text(json.dumps(record, indent=2))
temporary.replace(target)
os.environ.pop("BIV150_PROFILE_BOOTSTRAP", None)
os.execvpe(sys.argv[2], sys.argv[2:], os.environ)
