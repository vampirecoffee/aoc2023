from __future__ import annotations

import argparse

from tqdm import tqdm  # type: ignore[import-untyped]


def read_input(filename: str) -> list[list[str]]:
    """Read the input, returning a list of columns."""
    with open(filename) as f:
        return [list(line.strip()) for line in f]


def tilt_north(platform: list[list[str]]) -> list[list[str]]:
    """Tilt the platform north."""
    for y, row in enumerate(platform):
        for x, char in enumerate(row):
            if char == "O":
                platform[y][x] = "."
                i = y - 1
                while i >= 0 and platform[i][x] == ".":
                    i -= 1
                platform[i + 1][x] = "O"
    return platform


def tilt_south(platform: list[list[str]]) -> list[list[str]]:
    platform.reverse()
    platform = tilt_north(platform)
    platform.reverse()
    return platform


def tilt_west(platform: list[list[str]]) -> list[list[str]]:
    """Tilt the platform west."""
    for x in range(len(platform[0])):
        for y in range(len(platform)):
            if platform[y][x] == "O":
                platform[y][x] = "."
                i = x - 1
                while i >= 0 and platform[y][i] == ".":
                    i -= 1
                platform[y][i + 1] = "O"
    return platform


def tilt_east(platform: list[list[str]]) -> list[list[str]]:
    """Tilt the platform east."""
    for i in range(len(platform)):
        platform[i].reverse()
    platform = tilt_west(platform)
    for i in range(len(platform)):
        platform[i].reverse()
    return platform


def score(platform: list[list[str]]) -> int:
    out = 0
    for y, row in enumerate(platform):
        for char in row:
            if char == "O":
                out += len(platform) - y
    return out


def make_state(platform: list[list[str]]) -> str:
    rows_are_strs = ["".join(row) for row in platform]
    return "\n".join(rows_are_strs)


def spin_once(platform: list[list[str]]) -> list[list[str]]:
    """Spin the platform once."""
    platform = tilt_north(platform)
    platform = tilt_west(platform)
    platform = tilt_south(platform)
    platform = tilt_east(platform)
    return platform


def spin(platform: list[list[str]], n=1000000000) -> int:
    """Spin the platform (tilt north, west, south, east) N times, then score."""

    spin_count: int = 0
    cycles_in: int = 0  # How long does it take for the platform to cycle?
    reaches_state_in: dict[str, int] = {}  # Reaches state `key` in `val` cycles

    with tqdm(total=n) as pbar:
        while spin_count < n:
            if not cycles_in:
                state = make_state(platform)
                if state in reaches_state_in:
                    cycles_in = spin_count - reaches_state_in[state]
                    steps_before_cycle = reaches_state_in[state]
                    n_minus_steps = n - steps_before_cycle
                    # Largest multiple of "number of steps it takes to cycle"
                    # that is strictly less than n_minus_steps
                    largest_mult = (n_minus_steps - 1) - (
                        (n_minus_steps - 1) % cycles_in
                    )
                    # Add back the number of "bonus" steps it takes to start cycling
                    new_spin_count = largest_mult + steps_before_cycle
                    pbar.update(new_spin_count - spin_count)
                    spin_count = new_spin_count
                else:
                    reaches_state_in[state] = spin_count
            platform = spin_once(platform)
            spin_count += 1
            pbar.update(1)

    return score(platform)


def parse_file(filename: str) -> int:
    platform = read_input(filename)
    return spin(platform)


def main():
    """Main function."""
    parser = argparse.ArgumentParser()
    parser.add_argument("filename")
    args = parser.parse_args()
    print(args.filename)
    print(parse_file(args.filename))


if __name__ == "__main__":
    main()
