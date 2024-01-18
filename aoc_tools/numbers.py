"""Helper functions for dealing with Numbers."""


def between(i: float, pair: tuple[float, float]) -> bool:
    """Return True if i is 'between' the two numbers in the provided pair.

    Note that while ``pair`` has the type signature ``Iterable[float]``,
    we're really just expecting a list
    """
    small = min(pair)
    big = max(pair)
    return small <= i <= big
