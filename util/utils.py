from __future__ import annotations
import logging
from typing import List, Optional
import requests
from bs4 import BeautifulSoup
import sys


__logs: List[logging.Logger] = []


class Settings:
    def __init__(self) -> None:
        self.__verbose = True
        self.__debug = True
        # self.__max_res = 100
        self.__max_res = sys.maxsize
        self.cache = True
        self.use_cache = True
        global __last
        __last = self

    @staticmethod
    def get_settings() -> Settings:
        return __last if __last else Settings()

    @property
    def max_res(self) -> int:
        return self.__max_res

    @max_res.setter
    def max_res(self, val: int) -> None:
        self.__max_res = val

    @property
    def verbose(self) -> bool:
        return self.__verbose

    @verbose.setter
    def verbose(self, val: bool) -> None:
        if val:
            set_log_level(verbose=True)
        else:
            self.debug = False
            set_log_level(verbose=False)
        self.__verbose = val

    @property
    def debug(self) -> bool:
        return self.__debug

    @debug.setter
    def debug(self, val: bool) -> None:
        if val:
            self.verbose = True
            set_log_level(debug=True)
        else:
            set_log_level(debug=False)
        self.__debug = val


__last: Optional[Settings] = None


def get_soup(url: str, parser: str = 'xml') -> BeautifulSoup:
    """Get a BeautifulSoup object from a URL

    Args:
        url (str): The URL
        parser (str, optional): Parser; for HTML, use 'lxml'. Defaults to 'xml'.

    Returns:
        BeautifulSoup: BeautifulSoup object representation of the HTML/XML page.
    """
    __log.debug(f'Requesting ({parser}): {url}')
    htm = requests.get(url).text
    soup = BeautifulSoup(htm, parser)
    return soup


def get_logger(name: str) -> logging.Logger:
    """
    returns a preconfigured logger
    """
    log = logging.getLogger(name)

    global __last
    if __last is None:
        __last = Settings()

    if __last.debug:
        log.setLevel(logging.DEBUG)
    elif __last.verbose:
        log.setLevel(logging.INFO)
    else:
        log.setLevel(logging.WARNING)

    format = logging.Formatter('%(asctime)s [ %(name)s ] - %(levelname)s:   %(message)s')

    f_handler = logging.FileHandler('warnings.log', mode='a')
    f_handler.setLevel(logging.WARNING)
    f_handler.setFormatter(format)
    log.addHandler(f_handler)

    f_handler2 = logging.FileHandler('log.log', mode='a')
    f_handler2.setLevel(logging.DEBUG)
    f_handler2.setFormatter(format)
    log.addHandler(f_handler2)

    c_h = logging.StreamHandler(sys.stdout)
    c_h.setLevel(logging.INFO)
    c_h.setFormatter(format)
    log.addHandler(c_h)

    __logs.append(log)

    return log


def set_log_level(debug: bool = False, verbose: bool = True) -> None:
    if debug:
        level = logging.DEBUG
    elif verbose:
        level = logging.INFO
    else:
        level = logging.WARNING

    __log.debug(f"Set log level to: {level}")
    for l in __logs:
        l.setLevel(level)


__log = get_logger(__name__)
