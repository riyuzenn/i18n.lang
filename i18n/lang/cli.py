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

import pathlib
from i18n.lang import (
    i18nLangBuilder
)
from i18n.lang.utils import print_banner
from hype import Hype

app = Hype()

@app.command()
@app.argument('folder')
def create(folder):
    """
    Create a new i18n.lang project.
    """
    if not folder:
        folder = '_lang'

    builder = i18nLangBuilder(
        lang_folder=folder
    )
    builder.createEnv()

@app.command()
@app.argument('folder')
def build(folder, output_dirname: str = None):
    """
    Build the given folder.
    """

    if not folder:
        _folder = pathlib.Path('_lang')
    else:
        _folder = pathlib.Path(folder)

    
    builder = i18nLangBuilder()
    builder.build(
        env_dir=str(_folder.absolute()),
        output_dirname=output_dirname
    )


@app.help()
def help():
    print_banner()


