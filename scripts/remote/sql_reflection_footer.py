# Enable the submitted implementation without changing serving arguments.
from vllm_fl.patches.biv150_sql_reflection import install as _biv150_sql_install
_biv150_sql_install()
