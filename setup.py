from setuptools import setup, Extension
from setuptools.command.build_ext import build_ext as _build_ext
import subprocess, sys
from pathlib import Path
import pybind11

ext = Extension(
    "pyopenttdadmin.pymonocypher",                # put extension inside your package namespace
    sources = ["pyopenttdadmin/pymonocypher.cpp", "pyopenttdadmin/monocypher.cpp"],
    include_dirs = ["pyopenttdadmin", pybind11.get_include()],
    language = "c++",
    extra_compile_args = ["-std=c++17"],
)

setup(
    name = 'pyOpenTTDAdmin',
    version = '1.1.2',
    packages = ['pyopenttdadmin', 'aiopyopenttdadmin'],
    install_requires = [],  # Add any dependencies here
    author = 'liki-mc',
    description = 'Python library to communicate with OpenTTD Admin port',
    long_description = open('README.md').read(),
    long_description_content_type = 'text/markdown',
    url = 'https://github.com/liki-mc/pyOpenTTDAdmin/',
    license = 'MIT', 
    ext_modules = [ext],
    include_package_data = True,
    package_data = {
        "pyopenttdadmin": ["pymonocypher*.so", "pymonocypher*.pyd", "pymonocypher.pyi", "monocypher.h"],
    },
)
