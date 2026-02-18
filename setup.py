from setuptools import setup, Extension
import pybind11
import sys

if sys.platform == "win32":
    extra_args = ["/std:c++17", "/O2", "/EHsc"]
else:
    extra_args = ["-std=c++17", "-O2"]

ext = Extension(
    "math_engine",
    sources=["math_engine.cpp"],
    include_dirs=[pybind11.get_include()],
    language="c++",
    extra_compile_args=extra_args,
)

setup(
    name="math_engine",
    version="1.0",
    ext_modules=[ext],
)
