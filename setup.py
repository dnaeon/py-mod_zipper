import re
import ast

from setuptools import setup, find_packages


_version_re = re.compile(r'__version__\s+=\s+(.*)')

with open('src/mod_zipper/__init__.py', 'rb') as f:
    version = str(ast.literal_eval(_version_re.search(
        f.read().decode('utf-8')).group(1))
    )

setup(
    name='mod_zipper',
    version=version,
    description='Apache module for browsing of Zip archives',
    long_description=open('README.md').read(),
    author='Marin Atanasov Nikolov',
    author_email='dnaeon@gmail.com',
    license='BSD',
    url='https://github.com/dnaeon/py-mod_zipper',
    download_url='https://github.com/dnaeon/py-mod_zipper',
    package_dir={'': 'src'},
    packages=find_packages('src'),
)
