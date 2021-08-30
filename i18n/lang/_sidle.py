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

#: Convert https://github.com/znqi/sidle into a single python file
#: With some changes

from Crypto.Cipher import AES
from Crypto.Hash import SHA256
from Crypto import Random

from typing import (
    Any,
    List,
    Optional,
    Iterable,
    AnyStr,
    TextIO,
    Tuple
)
import ast
import os


class Sidle:
    """
    Sidle is a secure data storing with password and 
    simple encryption. This class handles all sidle 
    operation that can be storing sidle data on a 
    filename and more..
    Parameters:
        filename (str):
            The filename to be used for storing data
        password (Any):
            The password for the file in order to do 
            Sidle operation
        **options (Keyword Arguments):
            Additional option for the operation.
    """

    def __init__(
        self,
        filename: str,
        password: Any,
        **options
    ):

        #: The filename to be used for storing data
        self.filename = filename

        #: The password for the file in order to do 
        #: Sidle operation
        self.password = password
        
        #: A sidle data instance for handling data storing.
        self.sidle: SidleData = SidleData(
            password=self.password
        )

        #: Additional option for the operation.
        self.options = options

        self.__check_for_filename()

    def __getitem__(self, key: Any):
        """
        Get the item from the filename given.
        """

        raw = self.read_raw(self.filename, True)
        
        if len(raw) == 0:
            return None

        data = self.sidle.load(raw)
        return data.__getitem__(
            key=key
        )

    def __setitem__(self, key: Any, value: Any):
        """
        Set the item from the filename given
        """

        self.insert(
            key=key,
            value=value
        )


    def __check_for_filename(self):
        """
        Check if the given filename is already existed.
        If not then create a new one.
        """


        if not os.path.isfile(self.filename):
            with open(self.filename, 'wb') as f:
                pass
    
    def read_raw(
        self, 
        filename: str, 
        writable: Optional[bool] = False
    ) -> TextIO:
        
        """
        Read the raw file and return a TextIO object
        """

        if writable:
            mode = 'rb+'
        else:
            mode = 'rb'

        with open(filename, mode) as f:
            return f.read()


    def write_raw(self, filename: str, data: bytes) -> TextIO:
        """
        Write a raw data to the file
        """

        with open(filename, 'wb') as f:
            f.write(data)

    
    def read(self):
        """
        Return the representation of the
        SidleData.
        """

        return repr(self.sidle)

    def insert(
        self, 
        key: str, 
        value: Any
    ):
        """
        Insert the key and a value to the file.    
        """

        raw = self.read_raw(
            filename=self.filename
        )

        if len(raw) == 0:

            self.sidle.set(
                key=key,
                value=value
            )

            self.sidle.save(self.filename)

        else:
            data = self.sidle.load(raw)
            data.set(
                key=key,
                value=value
            )
                
            data.save(
                filename=self.filename
            )


    def __repr__(self):
        return self._get_repr_value()

    def _get_repr_value(self):
        raw = self.read_raw(
            filename=self.filename
        )
        

        if len(raw) == 0:
            _data = None
        else:
            _data = self.sidle.load(raw)
  
        
        name = type(self).__name__
        filename = self.filename
        password = password_with_asterisk(
            password=self.password
        )
        
        if _data:
            _len = len(_data)
            keys = [
                self.sidle._enc.decrypt(k)
                for k in _data.keys()
            ]
            

        else:
            _len = 0
            keys = None

        return "%s(filename=%s, password=%s, length=%s, keys=%s)" % (
            name,
            filename,
            password,
            _len,
            keys

        )

class SidleEncryption:
    """
    Simple Encrypting and Decrypting strings
    with password
    
    Parameter:
        password (Any):
            The password that can be used for both
            encryption and decryption
    """

    def __init__(self, password: Any):
        """
        Initialize SidleEncryption
        """
        self.password = convert_bytes(password)

    def encrypt(self, string: str):
        """
        Encrypt the given string and return
        encrypted bytes that can be decrypted with the
        given password.
        """

        string = convert_bytes(string)
        
        key = self.__password_to_key(self.password)
        IV = self.make_initialization_vector()
        encryptor = AES.new(key, AES.MODE_CBC, IV)

        # store the IV at the beginning and encrypt
        return IV + encryptor.encrypt(self.pad_string(string))

    def decrypt(self, encrypted_string: bytes):
        """
        Decrypt the given encrypted string
        """

        key = self.__password_to_key(self.password)
        
        # extract the IV from the beginning
        IV = encrypted_string[:AES.block_size]  
        decryptor = AES.new(key, AES.MODE_CBC, IV)

        _str = decryptor.decrypt(encrypted_string[AES.block_size:])
        
        try:
            string = convert_string(
                self.unpad_string(_str)
            )
        except UnicodeDecodeError:
            raise PasswordError('Password: %s is not a valid password' % (self.password))


        return string


    def make_initialization_vector(self):
        """
        An initialization vector (IV) is a fixed-size input to a cryptographic
        primitive that is typically required to be random or pseudorandom.
        Randomization is crucial for encryption schemes to achieve semantic 
        security, a property whereby repeated usage of the scheme under the 
        same key does not allow an attacker to infer relationships 
        between segments of the encrypted message.
        """
        return Random.new().read(AES.block_size)
    
    
    def unpad_string(self, string: str):
        """
        Unpad the given string
        """
        
        to_pad = string[0]
        if to_pad == 0:
            return string

        return string[1:-to_pad]

    def pad_string(self, string, chunk_size=AES.block_size):
        """
        Pad string the peculirarity that uses the first byte
        is used to store how much padding is applied
        """
        assert chunk_size  <= 256, 'We are using one byte to represent padding'
        to_pad = (chunk_size - (len(string) + 1)) % chunk_size
        return bytes([to_pad]) + string + bytes([0] * to_pad)

    def __password_to_key(self, password: Any):
        """
        Use SHA-256 over the password to get a proper-sized AES key.
        This hashes the password into a 256 bit string. 
        """

        return SHA256.new(password).digest()

class SidleData:
    """
    A data structure for handling Sidle data
    with encryption: `SidleEncryption.`
    Parameters:
        password (Any):
            The password that can be used for encryption.
    """

    _enc: SidleEncryption
    _list: list

    def __init__(
        self, 
        password: Any, 
        data: List[Tuple[Any]] = None
    ):
        
        self.password = password
        
        if data:
            self._list = data
        else:
            self._list = []

        self._enc = SidleEncryption(
            password=self.password
        )
        
    @property
    def raw(self) -> bytes:
        """
        Return the encrypted raw string of the data.
        """
        return self._enc.encrypt(str(self._list))

    def __getitem__(self, key: str, error: Optional[bool]=False):
        """
        Get the value of the key given. 
        Parameter:
            key (str):
                The key for the value to get
            error (Optional[bool]):
                Set if the function throws `KeyError`
        """
        encrypted_data = [
            (self._enc.decrypt(k), self._enc.decrypt(v))
            for k,v in self._list 
        ]

        if not error:
            if isinstance(key, int):
                return encrypted_data[key]
            
            elif isinstance(key, slice):
                return self.__class__(encrypted_data[key])
            
        _: str = key.lower()
        for k, v in encrypted_data:
            if k.lower() == _:
                return v

        #: If the error is true, raise `KeyError`
        #: exception if the key doesn't exitst
        
        if error:
            raise KeyError(key)

    def __setitem__(self, key: str, value: Any):
        """
        Set the value of the item. This magic method
        can be used on:
        
        >>> sidle = SidleData('password')
        >>> sidle['username'] = 'zenqi'
        """

        if isinstance(key, (slice, int)):
            if isinstance(key, int):
                value = [value]

            value = [
                (k, v)
                for k,v in value
            ]

            if isinstance(key, int):
                self._list[key] = value[0]
            else:
                self._list[key] = value

        else:
            self.set(
                key=key, 
                value=value
            )

    def __delitem__(self, key: str, index: Optional[bool] = True):
        """
        Delete the key and its value from the list
        of header.
        Parameter:
            key (str):
                The key to be deleted
            index (Optional[bool]):
                Set if the slicing can be index.
        """

        encrypted_data = [
            (self._enc.decrypt(k), self._enc.decrypt(v))
            for k,v in self._list 
        ]

        if index and isinstance(key, (int, slice)):
            del encrypted_data[key]
            return 

        _: str = key.lower()
        _new: list = []
        for k, v in encrypted_data:
            if k.lower() != _:
                _new.append((k,v))

        encrypted_data[:] = _new

        self._list = encrypted_data

    def __eq__(self, other):
        def lowered(item):
            return (item[0].lower(),) + item[1:]

        return other.__class__ is self.__class__ and set(
            map(lowered, other.__list)
        ) == set(map(lowered, self._list))

    def __iter__(self):
        return iter(self._list)

    def __len__(self):
        return len(self._list)

    def __copy__(self):
        return self.copy()
    
    def __contains__(self, key):
        """
        Check if a key is present.
        
        Example:
            
        """
        
        try:
            self.__getitem__(key)
        except KeyError:
            return False
        return True

    def get(
        self, 
        key: str, 
        default: Optional[Any] = None, 
        type: Optional[Any] = None, 
        bytes: Optional[bool]=False
    ):
        """
        Get the given key and return. If the type is defined
        then return the given type.
        Parameter:
            key (str):
                The key for the value to get.
            default (Optional[any]):
                Set the default value if the key doesn't exist
            
            type (Optional[any]):
                Set the type of the given value.
            bytes (Optional[bool]):
                Set if the value will be converted as bytes or no
        
        Example:
            
        
        """
        try:
            _value = self.__getitem__(key)
        except KeyError:
            return default

        if bytes:
            _value = convert_bytes(_value)

        if type != None:
            try:
                return type(_value)
            except ValueError:
                return default

        return _value

    def set(
        self,
        key: str,
        value: Any
    ):

        _key = self._enc.encrypt(key)
        _value = self._enc.encrypt(value)

        if self._list == None:
            self._list.append(
                (_key, _value)
            )

            return

        _iter = iter(self._list)
        _k = key.lower()

        for i, (o_key, o_value) in enumerate(_iter):
            if self._enc.decrypt(o_key).lower() == _k:                
                self._list[i] = (_key, _value)
                break

        else:
            self._list.append((_key, _value))
            return

        self._list[i + 1:] = [x for x in _iter if x[0].lower() != _k]


    def add(self, 
        key: AnyStr, 
        value: Any
    ):
        """
        Add a new tuple of header to the list of headers.
        Parameters:
            key (str):
                The key to be added
            value (Any):
                The value for the key to be added
            **kwargs(Dict[str, Any]):
                A keyword arguments for additional 
                option for the headers.
        """

        self._list.append((key, value))

    def remove(self, key: str):
        """
        Remove the key and its value from the list
        of header.
        Parameter:
            key (str):
                The key to be removed.
        """

        return self.__delitem__(key, False)

    def copy(self):
        return self.__class__(self._list)

    def clear(self):
        """
        Clear all data from the list.
        """

        del self._list[:]

    def pop(self, key: Optional[str] = None, default: Optional[Any] = None):
        """
        Remove the key and return the index of the key.
        Parameter:
            key (Optional[str]):
                The key to be popped. 
            default (Optional[None]):
                The default value if the key is `None`
        """

        if not key:
            self._list.pop()
        
        if isinstance(key, int):
            return self._list.pop(key)
        
        try:
            _value = self[key]
            self.remove(key)
        except KeyError:
            if default == None:
                return default
            else:
                default(_value)
        
        return _value

    def setlist(self, key: str, values: Iterable):
        """
        Remove any existing values for the header and add new one.
        Similar  to `set`
        
        Parameters:
            key (str):
                The key for the header.
            values(Iterable):
                Any value that can be iterate. For ex: list, tuple, etc
        """

        if values:
            _iter = iter(values)
            self.set(
                key=key, 
                value=next(_iter)
            )

            for value in _iter:
                self.add(
                    key=key,
                    value=value
                )
        
        else:
            self.remove(
                key=key
            )

    def keys(self):
        """
        Return all keys from the list of data.
        """
        _keys = []
        for k, _ in self:
            _keys.append(k)

        return _keys

    def load(self, data: bytes):
        """
        Load the the given data and return 
        A SileData class for the data given.
        """
        
        _ = self._enc.decrypt(data)
        if not _:
            try:
                self.load(data)
            except RecursionError:
                pass
        
        if isinstance(_, bytes):
            raise PasswordError('Password: %s is not a valid password' % (self.password))


        raw = ast.literal_eval(_)
        self.clear()
        self._list = raw

        return self

    def save(
        self, 
        filename: str, 
        data: Optional[bytes] = None
    ):

        """
        Save the sidle data on the given file io and
        closes it. Please take note that the File IO
        should be a writable bytes instead of string.
        This encrypt the data into bytes and store 
        in a file.
        """

        if data:
            data = data
        else:
            data = self.raw

        with open(filename, 'wb') as f:
            f.write(data)

    def __repr__(self):
        return self._get_repr_value(
            name=type(self).__name__
        )

    def _get_repr_value(self, name: str):
        length = len(self)
        keys = [self._enc.decrypt(x) for x in self.keys()]
        pwd = password_with_asterisk(
            password=self.password
        )

        return "%s(password=%s, length=%s, keys=%s)" % (
            name,
            pwd,
            length,
            keys
        )


def convert_string(
    value: Any, 
    encoding: str='utf-8'
) -> str:

    """
    Convert the given value of bytes to string.
    """

    if isinstance(value, bytes):
        value = value.decode(
            encoding=encoding
        )

    else:
        value = str(value)

    return value

def convert_bytes(
    value: Any, 
    encoding: str='utf-8'
) -> bytes:

    """
    Convert the given value of bytes to string.
    """
    if isinstance(value, str):
        value = value.encode(
            encoding=encoding
        )

    else:
        value = bytes(
            value,
            encoding=encoding
        )

    return value

def password_with_asterisk(
    password: str, 
    percentage: Optional[float] = 40
):
    
    if len(password) <= 2:
        return "*" * len(password)
  
    percent = int(
        (percentage * len(password)) / 100.0
    )
        
    _ = "*" * (len(password) - percent)
    return "%s%s" % (_, password[-percent:])

class SidleError(Exception):
    pass

class PasswordError(SidleError):
    pass
