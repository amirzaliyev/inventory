# import functools
# import time
#
#
# def timer(func):
#     @functools.wraps(func)
#     def wrapper_timer(*args, **kwargs):
#         start = time.perf_counter()
#
#         value = func(*args, **kwargs)
#
#         end = time.perf_counter()
#         run_time = end - start
#         print(f"Finished {func.__name__} in {run_time:.4f}")
#
#         return value
#
#     return wrapper_timer
#
#
# def debug(func):
#     @functools.wraps(func)
#     def wrapper_debug(*args, **kwargs):
#         args_repr = [repr(arg) for arg in args]
#         kwargs_repr = [f"{key}={value}" for key, value in kwargs]
#         signature = ", ".join(args_repr + kwargs_repr)
#         print(f"Calling {func.__name__} ({signature})")
#         value = func(*args, **kwargs)
#         print(f"{func.__name__} returned {repr(value)}")
#
#         return value
#
#     return wrapper_debug
#
#
# def slow_down(func):
#     @functools.wraps(func)
#     def wrapper_slow_down(*args, **kwargs):
#         time.sleep(1)
#         value = func(*args, **kwargs)
#
#         return value
#
#     return wrapper_slow_down
#
#
# PLUGINS = {}
#
#
# def register(func):
#     """Registers functions to PLUGIN map"""
#     PLUGINS[func.__name__] = func
#
#     return func
#
#
# @register
# def hello(name):
#     return f"hello, {name}"


# from typing import Any, Dict
#
# d1: Dict[str, Any] = {"name": "Hello", "age": 23, "marital_status": "single", "type":"psychopath"}
#
# l = ["name", "type"]
#
#
# print({k:d1[k] for k in l if k in d1})

import inspect


def hello(a, b):
    pass


print()
print(inspect.getfullargspec(hello).args.__class__.__name__)
