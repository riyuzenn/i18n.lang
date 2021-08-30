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

import secrets
import string
import os
import sys
from typing import Optional
import hype

def generate_password(
    ascii_letters: string.ascii_letters = None,
    digits: string.digits = None,
    length: int = 16
):
    """
    Generate a random and cryptographically safe password
    based on `secrets` module.

    """

    if not ascii_letters:
        ascii_letters = string.ascii_letters
    if not digits:
        digits = string.digits

    chars = ascii_letters + digits

    return ''.join(
        secrets.choice(chars)
        for i in range(length)
    )

def create_hidden_folder(
    folder: str,
    attribute: int = 0x02
):
    """
    Create a hidden folder for Win32.
    On Unix machines, we just need to add '.'
    infront of the folder.
    """
    
    folder = str(folder)
    FILE_ATTRIBUTE_HIDDEN = attribute
    
    if sys.platform == 'linux' or sys.platform == 'darwin':
        if not folder.startswith('.'):
            os.mkdir('.%s' % (folder))
        else:
            os.mkdir(folder)

    elif sys.platform == 'win32':
        import ctypes

        os.mkdir(folder)
        ret = ctypes.windll.kernel32.SetFileAttributesW(
            folder,
            FILE_ATTRIBUTE_HIDDEN
        )

        if not ret:
            raise ctypes.WinError()

def hide_file(
    file: str,
    attribute: int = 0x02
):
    """
    Create a hidden file for Win32.
    On Unix machines, we just need to add '.'
    infront of the file.
    """
    
    file = str(file)

    if attribute == 0x80:
        HIDE = False
        FILE_ATTRIBUTE = attribute
    else:
        HIDE = True
        FILE_ATTRIBUTE = attribute
    
    if sys.platform == 'linux' or sys.platform == 'darwin':
        if not file.startswith('.') and not HIDE:
            os.rename('.%s' % (file))
        else:
            os.rename(file)

    elif sys.platform == 'win32':
        import ctypes

        ret = ctypes.windll.kernel32.SetFileAttributesW(
            file,
            FILE_ATTRIBUTE
        )

        if not ret:
            raise ctypes.WinError()
    
def print_banner(color: Optional[str] = 'magenta'):
    hype.print("""\n[%s] o8o    .o   .ooooo.                   oooo                                   \n `"'  o888  d88'   `8.                 `888                                   \noooo   888  Y88..  .8' ooo. .oo.        888   .oooo.   ooo. .oo.    .oooooooo \n`888   888   `88888b.  `888P"Y88b       888  `P  )88b  `888P"Y88b  888' `88b  \n 888   888  .8'  ``88b  888   888       888   .oP"888   888   888  888   888  \n 888   888  `8.   .88P  888   888  .o.  888  d8(  888   888   888  `88bod8P'  \no888o o888o  `boood8'  o888o o888o Y8P o888o `Y888""8o o888o o888o `8oooooo.  \n                                                                   d"     YD  \n                                                                   "Y88888P'\n                [blue]- Build app internationally![/blue]\n                [green]- Made with [red]<3[/red][green] by Zenqi (https://github.com/znqi)[/green]\n\n[/%s]""" % (color, color))

def clear_screen():
    
    if sys.platform == 'win32':
        os.system('cls')
    elif sys.platform == 'linux' or sys.platform == 'linux2':
        os.system('clear')
    elif sys.platform == 'darwin':
        os.system('clear')
