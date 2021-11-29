from functools import wraps
from collections import namedtuple

_CacheInfo = namedtuple("CacheInfo", ["hits", "misses", "currsize"])

def makeHash(name, args, kwargs):
    """takes function name and args and creates a unique key

    Must be a string representation of all args and kwargs
    """
    id_str = (str(name)
              + "_".join([str(x) for x in args])
              + "_".join([str(x) for x in kwargs]))

    return hash(id_str)

def mut_cache(user_function):
    """Decorator to cache a function call

    Takes string representation of inputs (prepended by function name)
    and converts to hash. Then looks up in `cache` dictionary

    Mainly a modification of lru_cache implementation but allows for
    usage with mutable objects/dataframes
    https://github.com/python/cpython/blob/main/Lib/functools.py#L479

    Notes
    -----
    * unsure of performance as dictionary grows (maybe incorporate a size max)
    * might want to look up different/faster ways to generate key
    """
    cache = {}
    hits = misses = 0
    cache_get = cache.get
    cache_len = cache.__len__

    @wraps(user_function)
    def wrapper_mut_cache(*args, **kwargs):
        nonlocal hits, misses
        key = makeHash(user_function.__name__, args, kwargs)
        result = cache_get(key)

        if result is not None:
            hits += 1
            return result

        misses += 1
        result = user_function(*args, **kwargs)
        cache[key] = result
        return result

    def cache_info():
        return _CacheInfo(hits, misses, cache_len())

    wrapper_mut_cache.cache_info = cache_info
    return wrapper_mut_cache
