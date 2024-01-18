"""Basic hashable types for Python."""
from __future__ import annotations

from collections.abc import (
    Iterable,
    Iterator,
    Mapping,
    MutableMapping,
    MutableSequence,
)
from typing import Optional, TypeVar, Union, cast, overload

from typing_extensions import SupportsIndex

T = TypeVar("T")

_ListArg = Union[list[T], Iterable[T]]


class HashList(MutableSequence[T]):
    """A hashable list."""

    _items: list[T]

    def __init__(self, items: Optional[_ListArg[T]]) -> None:
        """Constructor."""
        if items is None:
            self._items = []
        else:
            self._items = list(items)

    def __hash__(self) -> int:
        """Implement hash."""
        return hash(e for e in self)

    @overload
    def __getitem__(self, index: int) -> T:
        ...

    @overload
    def __getitem__(self, index: slice) -> HashList[T]:
        ...

    def __getitem__(self, key: Union[int, slice]) -> Union[T, MutableSequence[T]]:
        """Get item from this list."""
        if isinstance(key, int):
            return self._items[key]
        return HashList(self._items[key])

    @overload
    def __setitem__(self, key: SupportsIndex, value: T) -> None:
        ...

    @overload
    def __setitem__(self, key: slice, value: Iterable[T]) -> None:
        ...

    def __setitem__(
        self, key: Union[SupportsIndex, slice], value: Union[T, Iterable[T]]
    ) -> None:
        """Set item in this list."""
        if isinstance(key, SupportsIndex):
            value = cast(T, value)
            self._items[key] = value
        else:
            value = cast(Iterable[T], value)
            self._items[key] = value

    def __delitem__(self, key: Union[SupportsIndex, slice]) -> None:
        """Delete an item from the list."""
        del self._items[key]

    def __len__(self) -> int:
        """Length."""
        return len(self._items)

    def insert(self, index: SupportsIndex, value: T) -> None:
        """Insert x at index i."""
        self._items.insert(index, value)


K = TypeVar("K")
V = TypeVar("V")
_MapArg = Union[dict[K, V], Mapping[K, V], Iterable[tuple[K, V]]]


class HashDict(MutableMapping[K, V]):
    """A hashable dictionary."""

    _items: dict[K, V]

    def __init__(self, items: Optional[_MapArg[K, V]]):
        """Constructor."""
        if items is None:
            self._items = {}
            return
        if isinstance(items, Mapping):
            self._items = dict(items.items())
        elif isinstance(items, Iterable):
            self._items = dict(items)
        else:
            raise ValueError(f"items {items} has bad type {type(items)}")

    def __hash__(self) -> int:
        return hash((k, v) for k, v in self._items.items())

    def __getitem__(self, key: K) -> V:
        """Get item."""
        return self._items[key]

    def __setitem__(self, k: K, v: V) -> None:
        self._items[k] = v

    def __delitem__(self, k: K) -> None:
        del self._items[k]

    def __iter__(self) -> Iterator[K]:
        return iter(self._items)

    def __len__(self) -> int:
        return len(self._items)

    def set(self, key: K, value: V) -> HashDict:
        """Return a new HashDict where key is set to value."""
        new = HashDict(self._items)
        new[key] = value
        return new
