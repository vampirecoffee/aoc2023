"""Part 1 of Day 1 of 2023 Advent of Code."""
import argparse
import string
from copy import copy


def get_calibration_value(s: str) -> int:
    """Get the calibration value from a string.

    This is the first digit and the last digit in the string.

    Ex. a1b2c3d4e5f -> 15.
    """
    digit_map: dict[str, int] = {
        "one": 1,
        "two": 2,
        "three": 3,
        "four": 4,
        "five": 5,
        "six": 6,
        "seven": 7,
        "eight": 8,
        "nine": 9,
    }
    digit_map.update({str(i): int(i) for i in string.digits})
    reversed_digit_map: dict[str, int] = {}
    for key, val in digit_map.items():
        copy_key = copy(key)[::-1]
        reversed_digit_map[copy_key] = val
    first_digit_str = find_first_in_str(list(digit_map.keys()), s)
    reversed_str = copy(s)[::-1]
    last_digit_str = find_first_in_str(list(reversed_digit_map.keys()), reversed_str)
    first_digit = digit_map[first_digit_str]
    last_digit = reversed_digit_map[last_digit_str]
    value_as_str = f"{first_digit}{last_digit}"
    assert len(value_as_str) == 2
    return int(value_as_str)


def find_first_in_str(l: list[str], s: str) -> str:
    """Find the item in the list that appears first in s."""
    first = ""
    first_idx = len(s)
    for item in l:
        idx = s.find(item)
        if idx != -1 and idx < first_idx:
            first_idx = idx
            first = item
    return first


def sum_all_calibration_values(filename: str) -> int:
    """Sum all calibration values in a file."""
    the_sum = 0
    with open(filename, encoding="utf-8") as f:
        for line in f:
            the_sum += get_calibration_value(line)
    return the_sum


def main() -> None:
    """Main function."""
    parser = argparse.ArgumentParser()
    parser.add_argument("filename")
    args = parser.parse_args()
    the_sum = sum_all_calibration_values(args.filename)
    print(the_sum)


if __name__ == "__main__":
    main()
