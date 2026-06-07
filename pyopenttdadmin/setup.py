from setuptools import setup, Extension
import pybind11
from pathlib import Path

ext = Extension(
	"pymonocypher",
	sources = ["pymonocypher.cpp", "monocypher.cpp"],
	include_dirs = [pybind11.get_include()],
	language = "c++",
	extra_compile_args = ["-std=c++17"],
)

setup(
	name = "pymonocypher",
	version = "0.0.0",
	ext_modules = [ext],
)
