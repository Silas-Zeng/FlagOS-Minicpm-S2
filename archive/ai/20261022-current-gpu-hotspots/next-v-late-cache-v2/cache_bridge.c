#define PY_SSIZE_T_CLEAN
#include <Python.h>
#include <stdint.h>
#include "cuda.h"

/* 只使用现场 SDK 的函数句柄/枚举。没有 context cache API 或 dynamic setter。 */
static PyObject *attributes(PyObject *self, PyObject *args) {
  unsigned long long raw;
  if (!PyArg_ParseTuple(args, "K", &raw)) return NULL;
  CUfunction fun = (CUfunction)(uintptr_t)raw;
  int shared = -1, dynamic = -1, carveout = -1;
  CUresult r1 = cuFuncGetAttribute(&shared, CU_FUNC_ATTRIBUTE_SHARED_SIZE_BYTES, fun);
  CUresult r2 = cuFuncGetAttribute(&dynamic, CU_FUNC_ATTRIBUTE_MAX_DYNAMIC_SHARED_SIZE_BYTES, fun);
  CUresult r3 = cuFuncGetAttribute(&carveout, CU_FUNC_ATTRIBUTE_PREFERRED_SHARED_MEMORY_CARVEOUT, fun);
  return Py_BuildValue("{s:(ii),s:(ii),s:(ii)}", "static_shared", (int)r1, shared,
      "max_dynamic_shared", (int)r2, dynamic, "preferred_carveout", (int)r3, carveout);
}

static PyObject *prefer_shared(PyObject *self, PyObject *args) {
  unsigned long long raw;
  if (!PyArg_ParseTuple(args, "K", &raw)) return NULL;
  CUfunction fun = (CUfunction)(uintptr_t)raw;
  CUresult result = cuFuncSetCacheConfig(fun, CU_FUNC_CACHE_PREFER_SHARED);
  return Py_BuildValue("{s:i,s:i,s:i}", "return_code", (int)result,
      "success_code", (int)CUDA_SUCCESS, "preference_enum", (int)CU_FUNC_CACHE_PREFER_SHARED);
}

static PyMethodDef methods[] = {
    {"attributes", attributes, METH_VARARGS, "函数属性 rc/value；不是 cache getter。"},
    {"prefer_shared", prefer_shared, METH_VARARGS, "只设置隔离函数的 PREFER_SHARED。"},
    {NULL, NULL, 0, NULL}};
static struct PyModuleDef definition = {
    PyModuleDef_HEAD_INIT, "biv150_cache_preference_probe", NULL, -1, methods};
PyMODINIT_FUNC PyInit_biv150_cache_preference_probe(void) { return PyModule_Create(&definition); }
