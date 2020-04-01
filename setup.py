import os
import os.path
import platform

from distutils.version import LooseVersion
from distutils.sysconfig import get_config_vars
from setuptools import setup, find_packages, Extension


root = os.path.abspath(os.path.dirname(__file__))
with open(os.path.join(root, 'README.md'), 'rb') as readme:
    long_description = readme.read().decode('utf-8')


class DelayedInclude:
    """We don't know where pybind will get installed, and we can't call it
    until *after* our dependencies are installed (which includes pybind)"""
    def __str__(self):
        import pybind11
        return pybind11.get_include()


extra_compile_args = [
    # Safely ignored on VS2013+.
    '-std=c++11'
]

# A trick picked up from a PyTorch ticket. On OS X 10.9, the C++ stdlib was
# changed. distutils will try to use the same one that CPython was compiled
# for, which won't build at all with a recent XCode. We set
# MACOSX_DEPLOYMENT_TARGET ourselves to force it to use the right stdlib.
if platform.system() == 'Darwin':
    if 'MACOSX_DEPLOYMENT_TARGET' not in os.environ:
        current_version = platform.mac_ver()[0]
        target_version = get_config_vars().get(
            'MACOSX_DEPLOYMENT_TARGET',
            current_version
        )
        if (LooseVersion(target_version) < '10.9'
                and LooseVersion(current_version) >= '10.9'):
            os.environ['MACOSX_DEPLOYMENT_TARGET'] = '10.9'


setup(
    name='pysimdjson',
    packages=find_packages(),
    version='2.0.0',
    description='simdjson bindings for python',
    long_description=long_description,
    long_description_content_type='text/markdown',
    author='Tyler Kennedy',
    author_email='tk@tkte.ch',
    url='http://github.com/TkTech/pysimdjson',
    keywords=['json', 'simdjson', 'simd'],
    zip_safe=False,
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
    ],
    python_requires='>3.4',
    extras_require={
        'build': [
            'pybind11'
        ],
        'dev': [
            'm2r',
            'sphinx',
            'ghp-import',
            'bumpversion',
            'pytest',
            'pytest-benchmark'
        ],
        'benchmark': [
            'orjson',
            'python-rapidjson',
            'simplejson',
        ]
    },
    ext_modules=[
        Extension(
            'csimdjson',
            [
                'simdjson/binding.cpp',
                'simdjson/simdjson.cpp'
            ],
            include_dirs=[
                DelayedInclude()
            ],
            language='c++',
            extra_compile_args=extra_compile_args
        )
    ]
)
