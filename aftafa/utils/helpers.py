"""
Utils module.
"""
from itertools import islice
from functools import wraps
from collections.abc import MutableMapping
from typing import Any
import string
import random
import base64
import time

from colorama import Fore


class bcolors:
    """This class is going to be used for print statements (logging purposes)"""
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

def to_lower(string: str) -> str:
    indices = []
    ct: int = 0

    if set(map(lambda char: char.islower(), string)) == {True}:
        return string

    for i, char in enumerate(string):
        if not char.islower():
            k: int = 1
            while (i + k) < len(string):
                if ct == 0:
                        indices.append(string[:i])
                if not string[(k + i)].islower():
                    indices.append(string[i:(k + i)])
                    break
                if (i + k + 1) == len(string):
                    indices.append(string[i:(i + k + 1)])
                k += 1
                ct += 1

    return '_'.join([ind.lower() for ind in indices])

def to_camel(string: str) -> str:
    word_tokens: list[str] = []
    abbrev_checker: bool = False
    for i, word in enumerate(string.split('_')):
        if all([char.isupper() for char in word]):
            if i == 0:
                abbrev_checker = True
            word_tokens.append(word)
            continue
        word_tokens.append(word.capitalize())
    string = ''.join(word_tokens)
    if abbrev_checker:
        return (string[0] + string[1:])
    return (string[0].lower() + string[1:])


def to_pascal(string: str) -> str:
    word_tokens: list[str] = []
    abbrev_checker: bool = False
    for i, word in enumerate(string.split('_')):
        if all([char.isupper() for char in word]):
            if i == 0:
                abbrev_checker = True
            word_tokens.append(word)
            continue
        word_tokens.append(word.capitalize())
    string = ''.join(word_tokens)
    if abbrev_checker:
        return (string[0] + string[1:])
    return (string[0].upper() + string[1:])

def flatten_dict(d: MutableMapping, parent_key: str = '', sep: str = '.') -> MutableMapping[Any, Any]:
    items = []
    for k, v in d.items():
        new_key = parent_key + sep + k if parent_key else k
        if isinstance(v, MutableMapping):
            items.extend(flatten_dict(v, new_key, sep=sep).items())
        else:
            items.append((new_key, v))
    return dict(items)

def escape_b64(encoded_: str) -> str:
    try:
        r = base64.b64decode(encoded_.lstrip('=?UTF-8?B?').rstrip('?=') + '=').decode('utf-8')
    except UnicodeDecodeError:
        r = base64.b64decode(encoded_.lstrip('=?utf-8?B?').rstrip('?=') + '==').decode('utf-8')
    return r

def strip_chars(string_: str) -> str:
    new_string = []
    for char in string_:
        if char not in list(string.digits):
            continue
        new_string.append(char)
    return ''.join(new_string)

def split_into_chunks(it, size):
    it = iter(it)
    return list(iter(lambda: tuple(islice(it, size)), ()))

def generate_random_hash(n: int = 10) -> str:
    """Generates random string of given `n` length.
    Args:
        n (int, optional): number of characters. Defaults to 10.

    Returns:
        str: random hash
    """
    temp_hash: str = ''.join(random.choices(string.ascii_letters + string.digits, k=n))
    return temp_hash


def timeit(func):
    @wraps(func)
    def timeit_wrapper(*args, **kwargs):
        start_time = time.perf_counter()
        result = func(*args, **kwargs)
        end_time = time.perf_counter()
        total_time = end_time - start_time
        print(f"Function {func.__name__}{args} {kwargs} Took {total_time:.4f} seconds")
        return result
    return timeit_wrapper

def color_fmt(func, color: str):
    mapping = {
        'black': Fore.BLACK,
        'red': Fore.RED,
        'green': Fore.GREEN,
        'yellow': Fore.YELLOW,
        'blue': Fore.BLUE,
        'magenta': Fore.MAGENTA,
        'cyan': Fore.CYAN,
        'white': Fore.WHITE,
        'reset': Fore.RESET
    }
    @wraps(func)
    def print_wrapper(*args, **kwargs):
        print(mapping.get(color), ''.join(map(str, args)), **kwargs)


def sizeof_fmt(num, suffix="B"):
    """Copyright: https://stackoverflow.com/questions/1094841/get-a-human-readable-version-of-a-file-size"""
    for unit in ("", "Ki", "Mi", "Gi", "Ti", "Pi", "Ei", "Zi"):
        if abs(num) < 1024.0:
            return f"{num:3.1f}{unit}{suffix}"
        num /= 1024.0
    return f"{num:.1f}Yi{suffix}"

def parse_jsonpath(jsonpath: str, data: dict[str, Any]) -> dict[str, Any]:
    pass
#     jsonpath_expr: jsonpath_ng.jsonpath.Child = jsonpath_ng.parse(jsonpath)
#     jsonpath_result: list[dict[str, Any]] = [match.value for match in jsonpath_expr.find(data)]
#     if len(jsonpath_result) == 1:
#         jsonpath_result = jsonpath_result[0]
#     return jsonpath_result
