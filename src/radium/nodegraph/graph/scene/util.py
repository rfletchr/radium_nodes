import sys
import typing


def get_unique_name(prefix, names: typing.Iterable[str]):
    names = {n for n in names if n.startswith(prefix)}
    if not names:
        return prefix

    for i in range(1, sys.maxsize):
        name = f"{prefix}_{i:03d}"
        if name not in names:
            return name
