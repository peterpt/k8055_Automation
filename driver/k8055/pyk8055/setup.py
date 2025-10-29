#!/usr/bin/env python3

"""
Modernized setup.py for pyk8055 for Python 3.

This script builds the Python C extension by linking against the
pre-compiled libk8055.so shared library in the parent directory,
rather than recompiling the C source files.

Original Author: Pjetur G. Hjaltason
Modernization for Python 3 and libusb-1.0: Gemini (Google AI)
Project Maintainer: peterpt (http://github.com/peterpt/)
"""

import os
from setuptools import setup, Extension
from subprocess import Popen, PIPE

# --- Version Detection ---
try:
    version = os.environ.get('VERSION')
    if not version:
        command = "grep '^VERSION =' ../Makefile | cut -d '=' -f 2 | tr -d '[:space:]'"
        version = Popen(command, stdout=PIPE, shell=True).communicate()[0].decode('utf-8')
except Exception:
    version = '0.4.2'
    print(f"Warning: Could not determine version from Makefile. Falling back to {version}.")

print(f"Building pyk8055 version: {version}")

# --- C Extension Module Definition ---
pyk8055_extension = Extension(
    '_pyk8055',
    sources=['libk8055.i'],
    
    # --- THIS IS THE FIX ---
    # Add swig_opts to tell SWIG where to find k8055.h
    swig_opts=['-I../'],
    
    # Tell the C compiler where to find the k8055.h header file.
    include_dirs=['../'],
    
    # Tell the linker where to find our compiled libk8055.so.
    library_dirs=['../'],
    
    # List the libraries to link against.
    libraries=['k8055', 'usb-1.0']
)

# --- Main Setup Configuration ---
setup(
    name='pyk8055',
    version=version,
    description='Modernized Python 3 wrapper for the Velleman K8055 USB board.',
    long_description='A SWIG-based Python 3 interface for the libk8055 C-library, updated to use libusb-1.0 for compatibility with modern Linux systems.',
    author='Pjetur G. Hjaltason',
    author_email='pjetur@pjetur.net',
    maintainer='peterpt',
    url='http://github.com/peterpt/',
    ext_modules=[pyk8055_extension],
    py_modules=['pyk8055']
)
