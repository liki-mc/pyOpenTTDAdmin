# python setup.py build_ext --inplace

from setuptools import setup, Extension
from setuptools.command.build_ext import build_ext as _build_ext
import subprocess
import sys
from pathlib import Path
import pybind11

ext = Extension(
    "pymonocypher",
    sources=["pymonocypher.cpp", "monocypher.cpp"],
    include_dirs=[pybind11.get_include()],
    language="c++",
    extra_compile_args=["-std=c++17"],
)

class build_ext(_build_ext):
    def run(self):
        super().run()
        # find built extension file
        # self.get_ext_fullpath will return something like build/lib.../pymonocypher.cpython-39-x86_64-linux-gnu.so
        outpath = Path(self.get_ext_fullpath("pymonocypher"))
        outdir = outpath.parent
        # run pybind11-stubgen to emit pymonocypher.pyi in outdir
        try:
            subprocess.check_call([sys.executable, "-m", "pybind11_stubgen", "-o", str(outdir), "pymonocypher"])
        except FileNotFoundError:
            raise RuntimeError("pybind11_stubgen not found; install pybind11-stubgen to generate .pyi")

setup(
    name="pymonocypher",
    version="0.0.0",
    ext_modules=[ext],
    cmdclass={"build_ext": build_ext},
    # ensure pyi is included when building a wheel/sdist if packaging as a package:
    include_package_data=True,
)

