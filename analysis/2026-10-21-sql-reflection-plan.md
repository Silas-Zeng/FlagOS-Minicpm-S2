> 后续真卡更新（08:11Z）：SQL独立两次43.199/43.091s对匹配B0 120.471s；SQL+C2 41.154s且官方Level3已101/105通过。本文保留原方案建立时的验证状态；最新证据见 `CURRENT_WORK.md` 与 framework-experiments 报告。以上短测不是官方吞吐成绩。

# SQL 配置模型按表反射：框架候选

日期：2026-10-21。状态：候选代码、真实SQLAlchemy CPU门及另一owner交叉审已完成，尚无本候选的服务性能或accuracy结论。本 agent没有操作远端/GPU，也没有改写设备安装源码、实际调优数据库或其配置行。

## 问题与最小改动

有效host诊断 `experiments/profiles/20261021T061506Z-host-gap/` 的8步窗口为约13.947 s；`_prepare_input_ids`约13.446 s，SQL get_config路径约13.405 s，其中4次get_sql_model/build_sql_model_by_db约10.780 s。它们是嵌套inclusive时间，不能相加。新的index wrapper反复触发SQL配置模型构建；实际 `AutoBase.prepare(engine)` 每次反射并映射整库约479表。问题已定位到host SQL模型工作，不能继续笼统称为GPU采样慢或JIT编译器慢。

候选 `patches/framework/biv150_sql_reflection.py` 只替换实际 `SQLPersistantModel.build_sql_model_by_db` 静态方法的实现：

```python
base = sqlalchemy.ext.automap.automap_base()
base.prepare(engine, reflection_options={
    "only": lambda table_name, metadata: table_name == name,
})
return base.classes.get(name)
```

每次仍创建fresh AutoBase，只收集当前请求的SQLite表及SQLAlchemy默认追踪的外键依赖，减少无关表的schema reflection和class映射。它改变了实际反射实现，没有把调用切到另一个现成后端。

不新增全局、跨engine或negative模型缓存，不改变现有`sql_model_pool`、table name/key hash、get_config/put_config、get_benchmark/put_benchmark、配置选择、调优或数据库行。非Iluvatar平台不安装；非SQLite engine调用保存的原函数。

## 为什么使用 callable only

SQLAlchemy官方说明，`AutomapBase.prepare` 的 `reflection_options`会传给`MetaData.reflect`。[Automap API](https://docs.sqlalchemy.org/en/20/orm/extensions/automap.html#sqlalchemy.ext.automap.AutomapBase.prepare)

`only=[name]`在表不存在时抛异常；callable形式对已发现的候选表做过滤。使用相等谓词后，缺表不会被请求反射，最后仍由原接口的`classes.get(name)`得到None。CPU门实际验证了这个差异，避免破坏原get_sql_model随后建表的路径。[MetaData.reflect API](https://docs.sqlalchemy.org/en/20/core/metadata.html#sqlalchemy.schema.MetaData.reflect)

没有将`resolve_fks`改成False，目标表引用的外部表仍按官方默认反射。FlagGems实际`build_sql_model_by_py`不生成外键；本候选承诺其配置表的列、PK和标量配置读写契约。测试额外验证了外向FK闭包，但不宣称任意数据库的全部双向ORM关系图与全库automap完全一样。

## 源码身份与安装

实际源码快照为 `experiments/profiles/20261021T061506Z-host-gap/source/sql.py`，旁有`sql.sha256`；完整字节SHA256：

```text
6dc19cb581d70154f14b95ed9112d682c6b5919b6cf3f8dea01a78a75ec0efd7
```

安装模块是`flag_gems.utils.models.sql`，对应设备`/usr/local/lib/python3.12/site-packages/flag_gems/utils/models/sql.py`。`install()`在替换方法之前验证该文件完整hash；不匹配直接抛错，不吞错。方法带独立marker，重复安装不叠加包装。

保留到可提交fixture的 `tests/fixtures/flaggems_sql_audited.py` 与上述文件字节完全相同，完整版权保留；fixture `.gitattributes` 设置`-text`，不依赖ignored tmp路径或换行归一化才能复现。

候选源码SHA256为 `ad84c9affe0c3f4b9a4432dd2cbb3861306726f07d53328e129af41c74ea8e8e`。在新的isolated插件源码中放置为`vllm_fl/patches/biv150_sql_reflection.py`；主负责人可在该副本runner footer加：

```python
from vllm_fl.patches.biv150_sql_reflection import install as _install_sql_reflection
_install_sql_reflection()
```

不需要修改官方SERVER或benchmark参数，也没有默认关闭的实验环境变量。符合目标vendor时默认安装并输出 `BIV150_SQL_REFLECTION_INSTALLED sqlite_targeted_only=1`，可作为driver的安装日志门。此处是集成片段，本 agent没有将其写入已运行的原source。

## 最短真实CPU门

测试 `tests/test_biv150_sql_reflection.py`，SHA256 `8f10a7d10885cc290a0aa7fab5fa1889471bcd2967ace7af3e452b60daccedec`。本机SQLAlchemy2.0.43，命令：

```text
python -m unittest discover -s tests -p test_biv150_sql_reflection.py -v
```

6项通过，agent本地1.349 s；另一owner独立执行1.118 s全部通过。测试只使用临时文件SQLite数据库，不连接实际调优库，不导入torch/Triton/vLLM或初始化设备。

- 13表数据库：原版metadata含13表，候选只含目标1表；目标列类型、nullable、PK和查询行一致，反射期间未发出DML/DDL。
- 缺表：原版与候选都返回None；随后新增同名表，再次调用能看到，不存在negative cache。另实证sequence-only缺表会异常。
- 两个engine的同名表：配置值分别128和256，4线程8次交错反射/读取保持隔离，每次只含该库目标表。
- 执行审计源真实`get_config`/`put_config`方法：已有配置读回一致；重复put不覆盖原值；候选创建的新配置可由原版读回。
- 引号/连字符表名正常；child→parent外键的默认反射闭包和目标列/PK一致，不反射无关表。
- vendor/engine回退、重复安装及源码漂移拒绝。

测试执行完整审计源中的Base/SQLPersistantModel类，使用真实SQLAlchemy反射、ORM映射、Session与SQL查询。仅Triton Config数据容器和无关父类/Session脚手架被CPU替身代替，不构造大型伪GPU环境。首轮测试命名空间注入错误覆盖了fixture的`__file__`，被hash门拒绝；修正为不注入typing dunder后通过，runtime实现没有因此修改。

## 语义与并发边界

fresh AutoBase保证每次反射从传入engine读取当前schema，不缓存缺表结果，不用table name跨库复用类。已有模型实例内锁和原缓存保持不变，新增表、同名表隔离和并发只读无需额外全局锁。原函数也以数据库当前可见schema为准；本补丁没有增加表创建/删除的跨事务承诺。

返回的仍是SQLAlchemy automapped类或None，配置列和值完全由原SQL读写逻辑处理。没有为了避免反射而伪造默认Config、删除调优DB、强制重新调优或切换缓存键。运行期没有新GPU同步、H2D、tensor操作或RNG消耗。

## 交叉审与下一步

Kernel/KV owner已只读审查候选及CPU门并独立复跑，未发现阻断项。先由唯一设备负责人用新isolated源码进行单一4K、64请求、128输出服务screen，保持官方SERVER/seed/负载；不叠加C2/C3或异步token融合，避免归因混淆。必须保存源/hash、原始结果、失败和postflight。当前没有新增GPU微测或服务收益数字。

SQL框架候选优先，因为它直接减少已定位的通用host工作；整数token融合候选仍保留为独立方案，不默认叠加。若服务确认明显收益，再用原协议完成精度及复现门；CPU配置等价门不能替代最终服务验证。
