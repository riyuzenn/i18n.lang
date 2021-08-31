#               Copyright (c) 2021 Zenqi.

# Permission is hereby granted, free of charge, to any person obtaining
# a copy of this software and associated documentation files (the
# "Software"), to deal in the Software without restriction, including
# without limitation the rights to use, copy, modify, merge, publish,
# distribute, sublicense, and/or sell copies of the Software, and to
# permit persons to whom the Software is furnished to do so, subject to
# the following conditions:

# The above copyright notice and this permission notice shall be
# included in all copies or substantial portions of the Software.

# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
# EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
# MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND
# NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE
# LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION
# OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION
# WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

from setuptools import setup
from setuptools import find_packages
from i18n.lang import __version__

BASE_URL = 'https://github.com/znqi/i18n.lang'

def get_long_description():

    with open("README.md", encoding="utf-8") as f:
        readme = f.read()

    return readme

def get_requirements():
    
    with open('requirements.txt', 'r') as f:
        requirements = f.read().split('\n')
    
    return requirements

extras_require = {
    'translator': 'googletrans==4.0.0rc1'
}

setup(
    
    name="i18n.lang", 
    description="A module used for building and translating data to create application internationally",
    long_description=get_long_description(),
    long_description_content_type='text/markdown',
    project_urls={
        'Source': BASE_URL,
    },
    author = 'Zenqi',
    license = 'MIT',
    version = __version__,
    install_requires=[
        "colorama>=0.3.4 ; sys_platform=='win32'",
        "aiocontextvars>=0.2.0 ; python_version<'3.7'",
        "win32-setctime>=1.0.0 ; sys_platform=='win32'",
        "pycryptodome>=3.10.1",
        "hypecli>=0.0.6"
    ],
    packages = [p for p in find_packages() if 'test' not in p],
    extras_require = extras_require
)
