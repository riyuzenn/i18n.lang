#   Copyright (c) 2021, Zenqi

# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:

# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.

# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.

from typing import Optional


class i18nError(Exception):
    pass

class LanguageError(i18nError):
    pass

class ConfigError(i18nError):
    pass

class MetaDataError(i18nError):
    pass

class PluginError(i18nError):
    pass


def throw(
    error_cls: i18nError, 
    message: str, 
    code: str, 
    line: Optional[str] = '─',
):

    """
    A error throwing with format given the error class,
    message and the code.
    """

    raise error_cls("\n\n%s\n\t[ERROR: %s] %s\n%s\n\n"
    %(
        line*70,
        code,
        message,
        line*70
    ))


ERROR_CODES = {
    'unknown_error': '0000',
    'not_found': '0001',
    'installation_error': '0002',
    'internal_error': '0003',
    'external_error': '0004',
    'package_error': '0005',
    'deprecation_error': '0006' 
}
