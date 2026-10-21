"""Small real-SQLAlchemy CPU gate; temporary databases only, no GPU imports.

The full byte-guarded SQL source is executed as its two audited classes.
Only its Triton Config container and unrelated base/session scaffolding are
substituted; reflection, ORM mapping, queries and temporary DB writes are real.
"""

import ast
from concurrent.futures import ThreadPoolExecutor
import hashlib
import importlib.util
import inspect
from itertools import chain, count
import os
from pathlib import Path
import sys
import tempfile
import threading
import types
import typing
import unittest
from unittest import mock

import sqlalchemy as sa
import sqlalchemy.ext.automap
import sqlalchemy.orm


ROOT = Path(__file__).resolve().parents[1]
FIXTURE = ROOT / "tests/fixtures/flaggems_sql_audited.py"
SPEC = importlib.util.spec_from_file_location(
    "sql_reflection_candidate", ROOT / "patches/framework/biv150_sql_reflection.py")
candidate = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(candidate)
MODULE_IDS = count()


class Config:
    def __init__(self, kwargs, num_warps=4, num_stages=3, num_ctas=1):
        self.kwargs, self.num_warps, self.num_stages, self.num_ctas = kwargs, num_warps, num_stages, num_ctas

    def all_kwargs(self):
        return dict(self.kwargs, num_warps=self.num_warps, num_stages=self.num_stages, num_ctas=self.num_ctas)


class PersistantModel:
    def __init__(self, *args, **kwargs):
        self.lock = threading.RLock()
        self.signature = inspect.signature(Config)


def original_module():
    raw = FIXTURE.read_bytes()
    if hashlib.sha256(raw).hexdigest() != candidate.EXPECTED_SQL_SHA256:
        raise RuntimeError("audited SQL fixture bytes changed")
    tree = ast.parse(raw)
    classes = [node for node in tree.body if isinstance(node, ast.ClassDef)
               and node.name in ("Base", "SQLPersistantModel")]
    module = types.ModuleType("audited_sql_gate_" + str(next(MODULE_IDS)))
    module.__file__ = str(FIXTURE)
    module.__dict__.update({name: value for name, value in vars(typing).items()
                            if not name.startswith("__")})
    module.__dict__.update(sqlalchemy=sa, os=os, md5=__import__("hashlib").md5,
                           chain=chain, triton=types.SimpleNamespace(Config=Config),
                           PersistantModel=PersistantModel, RollbackSession=sa.orm.Session,
                           override=lambda fn: fn)
    sys.modules[module.__name__] = module
    exec(compile(ast.Module(body=classes, type_ignores=[]), str(FIXTURE), "exec"), module.__dict__)
    return module


def schema_signature(model):
    table = model.__table__
    return ([(column.name, str(column.type), column.nullable) for column in table.columns],
            [column.name for column in table.primary_key])


def read_row(engine, model, key):
    with sa.orm.Session(engine) as session:
        row = session.get(model, key)
        return None if row is None else {column.name: getattr(row, column.name) for column in model.__table__.columns}


class SqlReflectionGate(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.ref, self.patched = original_module(), original_module()
        candidate.install(module=self.patched, vendor_name="iluvatar")
        self.engines = []

    def engine(self, name):
        engine = sa.create_engine("sqlite:///" + str(Path(self.temp.name) / (name + ".db")))
        self.engines.append(engine)
        self.addCleanup(engine.dispose)
        return engine

    def database(self, name, value=128, table_name="wanted"):
        engine = self.engine(name)
        metadata = sa.MetaData()
        target = sa.Table(table_name, metadata,
                          sa.Column("key_0", sa.BigInteger, primary_key=True),
                          sa.Column("BLOCK_SIZE", sa.BigInteger),
                          sa.Column("num_warps", sa.BigInteger),
                          sa.Column("num_stages", sa.BigInteger))
        for index in range(12):
            sa.Table("other_" + str(index), metadata, sa.Column("key", sa.Integer, primary_key=True))
        metadata.create_all(engine)
        with engine.begin() as connection:
            connection.execute(target.insert().values(key_0=64, BLOCK_SIZE=value, num_warps=2, num_stages=1))
        return engine

    def test_multi_table_columns_pk_rows_and_only_target_reflected(self):
        engine = self.database("multi")
        original = self.ref.SQLPersistantModel.build_sql_model_by_db("wanted", engine)
        statements = []
        def record(conn, cursor, statement, parameters, context, executemany):
            statements.append(statement)
        sa.event.listen(engine, "before_cursor_execute", record)
        try:
            changed = self.patched.SQLPersistantModel.build_sql_model_by_db("wanted", engine)
        finally:
            sa.event.remove(engine, "before_cursor_execute", record)
        self.assertEqual(schema_signature(original), schema_signature(changed))
        self.assertEqual(read_row(engine, original, 64), read_row(engine, changed, 64))
        self.assertEqual(len(original.metadata.tables), 13)
        self.assertEqual(set(changed.metadata.tables), {"wanted"})
        self.assertFalse(any(statement.lstrip().upper().startswith(("INSERT", "UPDATE", "DELETE", "CREATE", "DROP")) for statement in statements))

    def test_missing_table_none_then_new_table_is_visible(self):
        engine = self.database("late")
        for cls in (self.ref.SQLPersistantModel, self.patched.SQLPersistantModel):
            self.assertIsNone(cls.build_sql_model_by_db("late_table", engine))
        # SQLAlchemy's sequence-only form raises for a missing table; the
        # candidate's callable was already proved to preserve original None.
        with self.assertRaises(sa.exc.InvalidRequestError):
            sa.ext.automap.automap_base().prepare(engine, reflection_options={"only": ["absent"]})
        metadata = sa.MetaData()
        table = sa.Table("late_table", metadata, sa.Column("id", sa.Integer, primary_key=True))
        table.create(engine)
        for cls in (self.ref.SQLPersistantModel, self.patched.SQLPersistantModel):
            self.assertIsNotNone(cls.build_sql_model_by_db("late_table", engine))

    def test_two_engines_same_name_are_isolated_under_concurrent_reads(self):
        engines = [self.database("first", 128), self.database("second", 256)]
        def query(index):
            engine = engines[index % 2]
            model = self.patched.SQLPersistantModel.build_sql_model_by_db("wanted", engine)
            return read_row(engine, model, 64)["BLOCK_SIZE"], set(model.metadata.tables)
        with ThreadPoolExecutor(max_workers=4) as pool:
            answers = list(pool.map(query, range(8)))
        self.assertEqual([value for value, tables in answers], [128, 256] * 4)
        self.assertTrue(all(tables == {"wanted"} for value, tables in answers))

    def test_actual_get_put_config_values_and_no_overwrite(self):
        engine = self.database("config")
        original = self.ref.SQLPersistantModel(str(engine.url))
        changed = self.patched.SQLPersistantModel(str(engine.url))
        self.addCleanup(original.engine.dispose)
        self.addCleanup(changed.engine.dispose)
        self.assertIsNone(changed.get_config("kernel", [17]))
        original.put_config("kernel", [17], {"BLOCK_SIZE": 128, "num_warps": 2, "num_stages": 1})
        self.assertEqual(original.get_config("kernel", [17]).all_kwargs(), changed.get_config("kernel", [17]).all_kwargs())
        changed.put_config("kernel", [17], {"BLOCK_SIZE": 256, "num_warps": 4, "num_stages": 3})
        self.assertEqual(changed.get_config("kernel", [17]).kwargs["BLOCK_SIZE"], 128)
        changed.put_config("new_kernel", [23], {"BLOCK_SIZE": 64, "num_warps": 2, "num_stages": 1})
        self.assertEqual(original.get_config("new_kernel", [23]).all_kwargs(), changed.get_config("new_kernel", [23]).all_kwargs())

    def test_quoted_name_and_default_foreign_key_closure(self):
        engine = self.database("quoted", table_name='quoted"-table')
        old = self.ref.SQLPersistantModel.build_sql_model_by_db('quoted"-table', engine)
        new = self.patched.SQLPersistantModel.build_sql_model_by_db('quoted"-table', engine)
        self.assertEqual(read_row(engine, old, 64), read_row(engine, new, 64))
        metadata = sa.MetaData()
        sa.Table("parent", metadata, sa.Column("id", sa.Integer, primary_key=True))
        sa.Table("child", metadata, sa.Column("id", sa.Integer, primary_key=True),
                 sa.Column("parent_id", sa.ForeignKey("parent.id")))
        metadata.create_all(engine)
        old = self.ref.SQLPersistantModel.build_sql_model_by_db("child", engine)
        new = self.patched.SQLPersistantModel.build_sql_model_by_db("child", engine)
        self.assertEqual(schema_signature(old), schema_signature(new))
        self.assertEqual(set(new.metadata.tables), {"child", "parent"})
        self.assertEqual({fk.target_fullname for fk in old.__table__.foreign_keys},
                         {fk.target_fullname for fk in new.__table__.foreign_keys})

    def test_backend_fallback_idempotence_and_hash_guard(self):
        before = self.patched.SQLPersistantModel.build_sql_model_by_db
        candidate.install(module=self.patched, vendor_name="iluvatar")
        self.assertIs(before, self.patched.SQLPersistantModel.build_sql_model_by_db)
        untouched = original_module()
        old = untouched.SQLPersistantModel.build_sql_model_by_db
        self.assertFalse(candidate.install(module=untouched, vendor_name="other")["installed"])
        self.assertIs(old, untouched.SQLPersistantModel.build_sql_model_by_db)
        with mock.patch.object(untouched, "__file__", __file__):
            with self.assertRaisesRegex(RuntimeError, "unaudited FlagGems SQL source"):
                candidate.install(module=untouched, vendor_name="iluvatar")
        fake_engine = types.SimpleNamespace(dialect=types.SimpleNamespace(name="postgresql"))
        name, result = object(), object()
        fallback = mock.Mock(return_value=result)
        self.assertIs(candidate._targeted_builder(fallback)(name, fake_engine), result)
        fallback.assert_called_once_with(name, fake_engine)


if __name__ == "__main__":
    unittest.main()
