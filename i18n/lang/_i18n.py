
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


import os
import time
import shutil
import pathlib
import locale
import configparser

from ._sidle import Sidle
from .errors import (
    ConfigError,
    LanguageError,
    ERROR_CODES,
    MetaDataError,
    PluginError,
    throw
)
from typing import (
    Any,
    Optional,
    Sequence
)

from .constants import (
    BASE_DIR,
    COUNTRIES_TO_LANG,
    TRANSLATOR
)
from .utils import (
    clear_screen,
    generate_password,
    create_hidden_folder,
    hide_file,
    print_banner
)
from .logs import logger

import hype.ui as ui
import hype

class i18nLang:
    """
    
    `i18nLang` is a wrapper for getting value from
    the compiled, build output of a `i18nLangBuilder`
    This class handles all build data using `Sidle`.

    Parameter:
    ---
        lang_folder (str):
            The path for the compiled lang folder.

        lang (Optional[str]):
            The default lang to be used

        key (Optional[str]):
            The key for the compiled lang pack.
            This is available @ .build.ini file

    Example:
    ---
        >>> from i18n.lang import i18nLang
        >>> ...
        >>> lang = i18nLang(lang_folder='lang')
        >>> welcome = lang.getLanguage('welcome')
        >>> welcome
        >>> 'Hello, Welcome!'

    """

    #: Set the ignored files for the build output.
    __ignore__files: list = [
        '.build.ini', '.i18n',
        'cache', 'config.ini'
    ]

    #: Initialize sidle object
    #: used for getting data and value
    #: on a compiled language pack.
    sidle: Sidle 

    
    def __init__(
        self,
        lang_folder: str,
        lang: Optional[str] = None,
        key: Optional[str] = None
    ):
        """
        Initialize i18nLang folder.

        Parameter:

            `lang_folder` (str):
                The path for the compiled lang folder.

            `default_lang` (Optional[str]):
                The default lang to be used

            `key` (Optional[str]):
                The key for the compiled lang pack.
                This is available @ .build.ini file

        """

        self.lang: str = lang
        self.key:  str = key
        self.version: str = __import__('i18n').lang.__version__
        self.lang_folder = pathlib.Path(lang_folder)

        if not self.key:
            self.key = self.__get_key_from_build_env()
            
        if not self.lang:
            self.lang = self.__get_default_from_build_env()
        else:
            try:
                self.lang = COUNTRIES_TO_LANG[self.lang]
            except KeyError:
                self.lang = self.lang


    def __getitem__(self, key: str):
        """
        Get the lang value of the 
        default language. It can be
        the language or the language code.
        """

        return self.getLanguage(
            key=key
        )

    @logger.catch
    def get(
        self, 
        lang: str,
        key: str,
        error: Optional[bool] = False
    ):

        """
        Get the value of a language either the language
        or the language code from the compiled language
        pack.

        Parameter:
            `lang` (str):
                The language code to be get
            
            `key` (str):
                The key of the language not the key found
                on .build.ini.

        """

        try:
            _lang = COUNTRIES_TO_LANG[lang]
        except KeyError:
            _lang = lang
        
    
        value = self.getLanguage(
            lang=_lang,
            key=key
        )

        if error and not value:
            throw (
                error_cls=KeyError,
                message="Key: '%s' doesnt exist on the language pack" % (key),
                code=ERROR_CODES['not_found']
            )

        return value
    
    @logger.catch
    def getLanguage(
        self,
        key: str
    ) -> str:
        """
        Get the value of a language code from the compiled
        language pack given the lang and the key.

        Parameter:
       
            `key` (str):
                The key of the language not the key found
                on .build.ini.

        """
        files = []

        for file in self.lang_folder.glob('*'):
            if file.name not in self.__ignore__files:
                # TODO: All language file
                files.append(
                    (file.name, str(
                        file.absolute()
                    )
                ))


                if file.name.lower() == self.lang.lower():
                    #: Match the name of the language file
                    #: and the given name
                    self.sidle = Sidle(
                        filename=str(file.absolute()),
                        password=self.key
                    )
                    return self.sidle.__getitem__(
                        key=key
                    )

        
        if self.lang not in files:
            # TODO: No language file registered
            throw(
                error_cls=LanguageError,
                message="Language Code: '%s' not found, You may create a new one and build it" % (self.lang),
                code=ERROR_CODES['not_found']
            )

        return None

    @logger.catch
    def convert_lang(self, lang: str):
        """
        Convert the given language code 
        into the language name. For example:
        `convert_lang('en') -> 'English'`
        """
        
        keys = list(COUNTRIES_TO_LANG.keys())
        values = list(COUNTRIES_TO_LANG.values())
        
        position = values.index(lang)
        return str(keys[position]).capitalize()

    @logger.catch
    def __get_key_from_build_env(self):
        """
        Get the key to access Sidle data on a
        build environment which is `.build.ini`
        File that can be found on a build output 
        folder.
        """

        build_file = self.lang_folder / '.build.ini'

        if not build_file.exists():
            throw(
                error_cls=LanguageError,
                message="Build Config: '.build.ini' not found. You can rebuild if you lost it",
                code=ERROR_CODES['not_found']
            )

        conf = configparser.ConfigParser()
        conf.read(build_file.absolute(), encoding='utf-8')

        return conf.get('i18n', 'key')

    @logger.catch
    def __get_default_from_build_env(self):
        """
        Get the default language registered on a
        build environment which is `.build.ini`
        File that can be found on a build output 
        folder.
        """

        build_file = self.lang_folder / '.build.ini'

        if not build_file.exists():
            throw(
                error_cls=LanguageError,
                message="Build Config: '.build.ini' not found. You can rebuild if you lost it",
                code=ERROR_CODES['not_found']
            )

        conf = configparser.ConfigParser()
        conf.read(build_file.absolute(), encoding='utf-8')
        
        return conf.get('i18n', 'default')


    def __repr__(self):
        """
        The representation of `:class:` i18nLang

        """

        return "%s(version=%s, lang_folder=%s, lang=%s, key=%s)" % (
            type(self).__name__,
            self.version,
            self.lang_folder,
            self.lang, self.key
        ) 

class i18nLangBuilder:
    """

    A i18n Language Builder class that handle different task
    including building and creating i18n environments. This
    class can be used when creating i18n. If you want to use
    the i18n lang compiled project, refer to `:class: i18nLang`.

    Parameters:
    ---
        `lang_folder` (Optional[str]): 
            The name of the environment folder used 
            to store languages
        
        `i18n_env` (Optional[str]):
            Set the name of i18n environment. 
            By default, .i18n is the value.

        `auto_translate` (Optional[bool]):
            Used for generating auto-translated languages
            `generateLang`. By default the value is True

        **options (Keyword Arguments: Dict):
            not yet used. 

    Example:
    ---

        >>> from i18n.lang import i18nLangBuilder
        >>> builder = i18nLangBuilder(...)
        >>> builder.generateLang(lang=['french', 'spanish']) #: For generating
        >>> builder.build() #: For building


    """

    #: The default language code by the system default.
    default_lang = locale.getdefaultlocale()[0]

    #: Set the variable to boolean (True or false)
    #: For defining if the function is reloaded so that
    #: printing banner wont be reloaded as well
    _func_reload: bool = False

    #: Set the build version
    build_version: tuple = (0, 0, 1)

    def __init__(
        self,
        lang_folder: Optional[str] = '_lang',
        i18n_env: Optional[str] = '.i18n',
        auto_translate: Optional[bool] = True,
        **options
    ):

        """
        Initialize `i18nLangBuilder` class.

        Parameters:
    
            `lang_folder` (Optional[str]): 
                The name of the environment folder used 
                to store languages
            
            `i18n_env` (Optional[str]):
                Set the name of i18n environment. 
                By default, .i18n is the value.

            `auto_translate` (Optional[bool]):
                Used for generating auto-translated languages
                `generateLang`. By default the value is True

            **options (Keyword Arguments: Dict):
                not yet used. 
        
        """

        self.lang_folder: str = lang_folder
        self.i18n_env: str = i18n_env
        self._translate: bool = auto_translate
        self.options = options

        if not self.__check_for_lang_folder():
            logger.debug('No i18n environment found, creating new one')
            self.createEnv(self.lang_folder)

    def build(
        self, 
        env_dir: Optional[str] = None, 
        output_dirname: Optional[str] = None,
        clear_cache: Optional[bool] = True
    ):
        """
        Build the _lang folder using Sidle. 
        Make sure the .i18n environment is 
        available. If not then create a new one.

        Parameter:
            `env_dir(Optional[str])`:
                The environment directory. 
                The default value is '_lang'
            
            `output_dirname (Optional[str])`:
                The output directory name after
                building the languages. The default
                value is 'lang'

        """

        if not self._func_reload:
            clear_screen()
            print_banner()
        

        if not env_dir:
            env_dir = pathlib.Path(self.lang_folder)
        else:
            env_dir = pathlib.Path(env_dir)
        
        if not env_dir.exists():
            self.createEnv(
                dir=self.lang_folder
            )

        if not self._func_reload:
            # TODO: Avoid repeating on recursion
            logger.info('Building Folder: %s' % (env_dir))
            print('\n')

        self.__build(
            env_dir=env_dir,
            output_dirname=output_dirname,
            clear_cache=clear_cache
        )

        if not self._func_reload:
            logger.success('Building folder, environment success!')
            logger.success('Enjoy using `i18n.lang`')
            print('')


    def __build(
        self, 
        env_dir: Optional[str] = None, 
        output_dirname: Optional[str] = None,
        clear_cache: Optional[bool] = True
    ):
        """
        A base function for building without
        any progress or any printing output.


        Build the _lang folder using Sidle. 
        Make sure the .i18n environment is 
        available. If not then create a new one.

        Parameter:
            `env_dir(Optional[str])`:
                The environment directory. 
                The default value is '_lang'
            
            `output_dirname (Optional[str])`:
                The output directory name after
                building the languages. The default
                value is 'lang'

        """

        if not self._func_reload:
            # TODO: Avoid repeating on recursion
            logger.info('Reading environment configuration')
        
        i18n_env = (env_dir / self.i18n_env)

        _config = self.read_config(
            path=(i18n_env / 'config.ini')
        )
        
        if not output_dirname:
            _output_dirname = self.__get_config_option(
                config_class=_config,
                section='build',
                option='dirname'
            )
            if _output_dirname:
                output_dirname = _output_dirname
            else:
                output_dirname = 'lang'
        
        key = self.__get_config_option(
            config_class=_config,
            section='build',
            option='key'
        )

        if not key:
            throw(
                error_cls=KeyError,
                message="Build Config: 'key' is not define, kindly create a key option",
                code=ERROR_CODES['not_found']
            )
        
        if not (i18n_env / 'cache').exists():
            # TODO: Create a cache folder for i18n env

            os.mkdir(
                path=(i18n_env / 'cache').absolute()
            )

        for file in env_dir.glob('*'):
            if not file.name == self.i18n_env:
                _parser = self.read_config(
                    path=file.absolute()
                )
                name = self.__get_config_option(
                    config_class=_parser,
                    section='lang',
                    option='name'
                )
                code = self.__get_config_option(
                    config_class=_parser,
                    section='lang',
                    option='code'
                )
                try:
                    metadata = _parser.items('metadata')
               
                except configparser.NoSectionError:
                    throw(
                        error_cls=MetaDataError,
                        message="Config: 'metadata' is not found Please read how to create metadata",
                        code=ERROR_CODES['not_found']
                    )

                # TODO: Encrypt the data using the Sidle with the key given
                try:
                    if not self._func_reload:
                        # TODO: Avoid repeating on recursion
                        logger.info('Building %s -> %s' %(
                                file.name,
                                (i18n_env / 'cache' / file.name).absolute()
                            )
                        )
                    sidle = Sidle(
                        filename=str(
                            (i18n_env / 'cache' / file.name).absolute()
                        ),
                        password=key
                    )

                    if not self._func_reload:
                        # TODO: Avoid repeating on recursion
                        logger.success('Saving %s -> %s' %(
                                file.name,
                                (i18n_env / 'cache' / file.name).absolute()
                            )
                        )
                    if not self._func_reload:
                        # TODO: Avoid repeating on recursion
                        print('')

                except FileNotFoundError:
                    pass

                try:
                    for (k, v) in metadata:
                        
                        sidle['_lang_name'] = name
                        sidle['_lang_code'] = code

                        sidle[k] = v

                        
                except Exception:
                    try:
                        shutil.rmtree(
                            path=str(
                                (i18n_env / 'cache').absolute()
                            )
                        )
                    except FileNotFoundError:
                        pass

                    self._func_reload = True
                    self.build(
                        env_dir=env_dir,
                        output_dirname=output_dirname
                    )


        OUTPUT_DIR = (BASE_DIR / output_dirname)

        if not OUTPUT_DIR.exists():
            if not self._func_reload:
                # TODO: Avoid repeating on recursion
                logger.info('Output Directory: %s doesn\'t exist. Creating a new one')
            
            os.mkdir(
                path = str(
                    OUTPUT_DIR.absolute()
                )
            )
            if not self._func_reload:
                # TODO: Avoid repeating on recursion
                logger.success('Output Directory successfully created')

        cache_folder = (i18n_env / 'cache') 
    
        if not self._func_reload:
            # TODO: Avoid repeating on recursion
            print('')

        for file in cache_folder.glob('*'):
            
            if not self._func_reload:
                # TODO: Avoid repeating on recursion
                logger.info('Moving compiled language: %s to -> %s' % 
                    (
                    file.name, (OUTPUT_DIR / file.name).absolute()
                    )
                )

            shutil.move(
                src=str(file.absolute()),
                dst=str(
                    (OUTPUT_DIR / file.name).absolute()
                )
            )

        if not self._func_reload:
            # TODO: Avoid repeating on recursion
            logger.success('Files moved successfully')

        if not self._func_reload:
            # TODO: Avoid repeating on recursion
            print('')        
        
        if cache_folder.exists() and clear_cache:
            # TODO: Clean cache folder.
            if not self._func_reload:
                # TODO: Avoid repeating on recursion
                logger.info('Cleaning all cache folder..')
                time.sleep(3)

            shutil.rmtree(
                path=str(cache_folder.absolute())
            )

        if not self._func_reload:
            # TODO: Avoid repeating on recursion
            logger.success('Cleaning all cache folder success')


        # TODO: Create build environment.
        if not self._func_reload:
            # TODO: Avoid repeating on recursion

            print('')
            logger.info('Creating build (.build.ini) environment')
            self.__create_build_env(
                path=OUTPUT_DIR.absolute()
            )

            print('')
            print('─'*50)
            logger.success('Building all done!')

    @logger.catch
    def createEnv(
        self, 
        dir: Optional[str] = None, 
        key: Optional[str] = None 
    ):
        """
        Create a i18n environment folder as well as
        create a started `en` lang file.
        """
        if not self._func_reload:
            clear_screen()
            print_banner()
    
        logger.info('Creating a new environment @ %s' % (dir))
        with ui.Spinner('Building configs...', color='cyan') as spin:
            if not dir:
                dir = pathlib.Path(self.lang_folder)
            else:
                dir = pathlib.Path(dir)

            i18n_folder = dir / self.i18n_env

            if not dir.exists():
                os.mkdir(dir.absolute())

            if not (dir / self.i18n_env).exists():
                create_hidden_folder(i18n_folder.absolute())


            if not key:
                key = generate_password()

            _config = configparser.ConfigParser()
            _config['i18n'] = {
                'default': self.default_lang,
                'default_name': self.convert_lang(
                    lang=self.default_lang
                )
            }
            _config['build'] = {
                'dirname': 'lang',
                'key': key
            }

            _config.write(
                open(
                    (i18n_folder / 'config.ini').absolute(),
                    'w',
                    encoding='utf-8'
                )
            )

            _default = configparser.ConfigParser()
            _default['lang'] = {
                'code': self.default_lang,
                'name': self.convert_lang(
                    lang=self.default_lang
                )
            }

            if TRANSLATOR and self._translate:
                _default['metadata'] = {
                    'welcome': TRANSLATOR.translate(
                        text='Hello, Welcome',
                        dest='en_US',
                    ).text
                }

            elif self._translate and not TRANSLATOR:
                # TODO: `googletrans==4.0.0` is not installed
                throw(
                    error_cls=PluginError,
                    message="Plugin: 'googletrans' is not installed, please install googletrans==4.0.0",
                    code=ERROR_CODES['installation_error']
                )


            _default.write(
                open((dir / self.default_lang).absolute(), 'w', encoding='utf-8')
            )

            time.sleep(3)
            spin.stop()
        
        logger.success('Building folder, environment success!')
        logger.success('Check the folder <yellow>.i18n </yellow> to change some configs. Enjoy!`')


    @logger.catch
    def generateLang(self, lang: Any):
        """
        This function is used for generating auto-translated
        language based on `en` lang. You can define the auto-
        translated languages @ `lang` parameter when initializing
        the `:class:` i18Lang.
        """
        if not self._func_reload:
            clear_screen()
            print_banner()
        
        
        _lang = []

        if not self._translate:
            raise LanguageError('You should define `auto_translate` param to True')

        if isinstance(lang, (tuple, list)):
            _lang = lang

        elif isinstance(lang, str):
            _lang.append(lang)
        
        logger.info("Generating Language: '%s'" % (', '.join(_lang)))
        with ui.progressbar(
            total=len(_lang), 
            title='Building Languges ' % (),

        ) as bar:

            for i in _lang:
                i = self.__parse_lang(i)
                self.create_lang(i)
                time.sleep(.005)
                bar()

        hype.print('')
    
    @logger.catch
    def updateLang(self):
        """
        This function update all languages.
        This differ to `generateLang` since `generateLang` 
        create a new one, while this one just update it.
        """

        print_banner()

        path = pathlib.Path(self.lang_folder)
        parser = configparser.ConfigParser()
        new = configparser.ConfigParser()
        _ = []

        for file in path.glob('*'):
            # TODO: Get all files from the lang folder
            if not file.is_dir():
                parser.read(file.absolute(), encoding='utf-8')
                name = self.convert_lang(file.name)
                code = file.name

                try:
                    metadata = parser.items('metadata')
                except configparser.NoSectionError:
                    throw(
                        error_cls=MetaDataError,
                        message="Config: 'metadata' is not found Please read how to create metadata",
                        code=ERROR_CODES['not_found']
                    )
                new['lang'] = {
                    'code': code,
                    'name': name
                }

                for k,v in metadata:
                    if file.name != self.default_lang:
                        try:
                            translated = TRANSLATOR.translate(
                                text=v,
                                dest=file.name,
                                src=self.default_lang
                            )
                        except ValueError:
                            translated = TRANSLATOR.translate(
                                text=v,
                                dest=file.name.replace('_', '-'),
                                src=self.default_lang
                            )

                        _.append((k, translated.text))
                        # print(translated)

                if file.name != self.default_lang:
                    new['metadata'] = {k:v for k,v in _}
                    with open(file.absolute(), 'w', encoding='utf-8') as f:
                        new.write(f)
    
    @logger.catch
    def create_lang(
        self, 
        lang: str, 
        folder: Optional[str] = None
    ):
        """
        Create a lang file with auto translated text. Make sure 
        `.i18n` File exist.
        """


        if not folder:
            folder = self.lang_folder

        path = pathlib.Path(folder)
        i18n_env = path / '.i18n'
        config = i18n_env / 'config.ini'

        if i18n_env.is_file():
            throw(
                error_cls=ConfigError,
                message='Config: %s is a file, please make sure it \n\tis a directory or read how to create .i18n config' % (str(config.name)),
                code=ERROR_CODES['internal_error']
            )

        i18n_config = configparser.ConfigParser()
        i18n_config.read(config.absolute(), encoding='utf-8')
        
        default_lang = self.__get_config_option(
            config_class=i18n_config,
            section='i18n', 
            option='default'
        )

        default_name = self.__get_config_option(
            config_class=i18n_config,
            section='i18n', 
            option='default_nmae'
        )

        default_config = configparser.ConfigParser()
        default_config.read((path / default_lang).absolute())

        lang_config = configparser.ConfigParser()

        metadata = default_config.items('metadata')
        country = self.convert_lang(lang)
        lang_config['lang'] = {'name': country, 'code': lang}
        
        _ = []

    
        for k,v in metadata:

            # TODO: Translate all value from the metadata
            #: For example:
            #:...
            #: [metadata]
            #: greet = Hello
            #:...

            #: Translated
            #: [metadata]
            #: greet = Hola
            try:
                translated = TRANSLATOR.translate(
                    text=v,
                    dest=lang,
                    src=default_lang
                )
            except ValueError:
                translated = TRANSLATOR.translate(
                    text=v,
                    dest=lang.replace('_', '-'),
                    src=default_lang
                )

            _.append((k, translated.text))
            

        lang_config['metadata'] = {k:v for k,v in _}
        lang_config.write(
            open((path / lang).absolute(), 'w', encoding='utf-8')
        )

    @logger.catch
    def read_config(
        self, 
        path: Optional[pathlib.Path],
        allow_no_value: Optional[bool] = False,
        comment_prefixes: Sequence[str] = ('#', ';', '#;')
    ) -> configparser.ConfigParser:

        """
        Read the given config and return -> ConfigParser
        class.
        """

        if not path.exists():
            throw(
                error_cls=FileNotFoundError,
                message="Path: '%s' is not found. Please be specific." % (path),
                code=ERROR_CODES['not_found']
            )

        config = configparser.ConfigParser(
            allow_no_value=allow_no_value,
            comment_prefixes=comment_prefixes
        )

        config.read(path.absolute(), encoding='utf-8')
        
        return config

    def convert_lang(self, lang: str):
        """
        Convert the given language code 
        into the language name. For example:
        `convert_lang('en') -> 'English'`
        """
        
        keys = list(COUNTRIES_TO_LANG.keys())
        values = list(COUNTRIES_TO_LANG.values())
        
        position = values.index(lang)
        return str(keys[position]).capitalize()


    def __check_for_lang_folder(self):
        """
        Check if the lang folder exist or not
        """
        if pathlib.Path(self.lang_folder).exists():
            return True
        else:
            return False
        
    def __parse_lang(self, lang: str):
        """
        Parse the given string to a language code.
        If the value given is country, then it will
        return the language code for the country
        """

        lang = lang.lower()
        
        if len(lang) <= 2:
            # TODO: Language code
            return lang
        
        if lang not in COUNTRIES_TO_LANG.keys():
            # TODO: Check if the given lang exist on the
            #: Dictionary, if not then throw `languageError`

            throw(
                error_cls=LanguageError, 
                message='Language: %s not found, Please be more specific' % (lang.capitalize()),
                code=ERROR_CODES['not_found']
            )
            
        code = COUNTRIES_TO_LANG[lang]
        return code


    def __get_config_option(
        self, 
        config_class: configparser.ConfigParser, 
        section: str, 
        option: str
    ):

        """
        Get the option from the given `ConfigParser` class 
        """

        try:
            data = config_class.get(section, option)
        except Exception:
            data = None

        return data

    def __create_build_env(
        self, 
        path: pathlib.Path
    ):
        """
        Create a build env after building. 
        This will produce .build.ini file
        """

        i18n_build_env = path / '.build.ini'
        i18n_cache = (pathlib.Path(self.lang_folder) / self.i18n_env / 'config.ini')

        i18n_config = self.read_config(
            path=(i18n_cache).absolute()
        )

        
        default_lang = self.__get_config_option(
            config_class=i18n_config,
            section='i18n',
            option='default'
        )

        key = self.__get_config_option(
            config_class=i18n_config,
            section='build',
            option='key'
        )


        _config = configparser.ConfigParser(
            allow_no_value=True,
            comment_prefixes=('#', ';', '#;')
        )
        
        _config['i18n'] = {
            
            #: Add some comments.
            '': None,
            '#; Build Configuration for i18n.lang.': None,
            '#; Please take note that if you want to': None,
            '#; Delete this, make sure to add the key.': None,
            '#; Keys are important. If you accidentally removed,': None,
            '#; Kindly rebuild the i18n language pack.': None,
            '#; Build version: %s' % (''.join(str(self.build_version))): None,
            '': None,
            
            #: Add the key and default lang
            'default': default_lang,
            'key': key
        }

        if i18n_build_env.exists():
            # TODO: If the .build.ini exist, remove all attribute
            hide_file(str(i18n_build_env.absolute()), 0x80)
        
        _config.write(
            open(i18n_build_env.absolute(), 'w', encoding='utf-8')
        )
        

        # TODO: After writting, set the file attribute to
        #: hidden

        hide_file(str(i18n_build_env.absolute()))
    
    def __repr__(self):
        """
        Representation for i18nLangBuilder that display
        its version and some attributes
        """
        return "%s(build_version=%s, i18n_env=%s, lang_folder=%s)" % (
            type(self).__name__, self.build_version, 
            self.i18n_env, self.lang_folder
        )
