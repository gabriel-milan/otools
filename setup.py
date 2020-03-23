from setuptools import setup, find_packages
from setuptools.extension import Extension
import subprocess
import sys

def install(package):
  subprocess.check_call([sys.executable, "-m", "pip", "install", package])

try:
  from Cython.Build import cythonize
except:
  install('cython')
  from Cython.Build import cythonize

with open("README.md", "r") as fh:
  long_description = fh.read()

extensions = [
  Extension(
    "otools.*",
    ["otools/*.py"],
  ),
  Extension(
    "otools.core.*",
    ["otools/core/*.py"],
  ),
  Extension(
    "otools.exceptions.*",
    ["otools/exceptions/*.py"],
  ),
  Extension(
    "otools.logging.*",
    ["otools/logging/*.py"],
  ),
  Extension(
    "otools.status.*",
    ["otools/status/*.py"],
  ),
]

setup(
  name = 'otools',
  version = '0.0.3',
  license='GPL-3.0',
  description = 'OTools stands for Online Tools, which is a Python/Cython framework for developing multithread online systems in a simple way.',
  long_description = long_description,
  long_description_content_type="text/markdown",
  packages=find_packages(),
  author = 'Gabriel Gazola Milan',
  author_email = 'gabriel.gazola@poli.ufrj.br',
  url = 'https://github.com/gabriel-milan/otools',
  keywords = ['framework', 'threading', 'shared resources', 'flexibility', 'python', 'online'],
  install_requires=[
    'cython'
  ],
  classifiers=[
    'Development Status :: 4 - Beta',
    'Intended Audience :: Developers',
    'Topic :: Software Development :: Libraries :: Python Modules',
    'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
    'Programming Language :: Python :: 3',
    'Programming Language :: Python :: 3.4',
    'Programming Language :: Python :: 3.5',
    'Programming Language :: Python :: 3.6',
    'Programming Language :: Python :: 3.7',
    'Programming Language :: Python :: 3.8',
  ],
  ext_modules = cythonize(extensions)
)