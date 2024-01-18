"""Tools for dealing with iterables that python does not have."""
from collections.abc import Iterable
from typing import TypeVar

T = TypeVar("T")


def first(iterable: Iterable[T]) -> T:
    """Get first item in a list/iterable."""
    for e in iterable:
        return e
    raise RuntimeError(f"Can't get first item of empty iterable {iterable}")
