#! /usr/bin/env python

from setuptools import setup, Extension, find_packages
from distutils import sysconfig
if sysconfig.get_config_var("LIBM") == "-lm":
    libraries = ["m"]
else:
    libraries = []

install_requires = []
execfile('mwlib/_extversion.py')  # adds 'version' to local namespace

ext_modules = []
ext_modules.append(Extension("mwlib.ext._rl_accel",
                             ['upstream-src/src/rl_addons/rl_accel/_rl_accel.c'],
                             libraries=libraries))

packages = ["mwlib.ext." + x for x in find_packages("upstream-src/src")] + find_packages(".")

setup(
    name="mwlib.ext",
    version=str(version),
    install_requires=install_requires,
    packages=packages,
    package_dir={"mwlib.ext.reportlab": "upstream-src/src/reportlab",
                 "mwlib.ext.rl_addons": "upstream-src/src/rl_addons"},
    ext_modules=ext_modules,
    namespace_packages=['mwlib'],
    include_package_data=True,
    zip_safe=False,
    url="http://code.pediapress.com/",
    description="provide dependencies for mwlib",
    license="BSD License",
    maintainer="pediapress.com",
    maintainer_email="info@pediapress.com",
    long_description=open("README.txt").read())
