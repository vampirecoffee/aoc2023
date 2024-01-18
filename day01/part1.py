"""Part 1 of Day 1 of 2023 Advent of Code."""
import argparse
import string


def get_calibration_value(s: str) -> int:
    """Get the calibration value from a string.

    This is the first digit and the last digit in the string.

    Ex. a1b2c3d4e5f -> 15.
    """
    digits = [char for char in s if char in string.digits]
    first_digit = digits[0]
    last_digit = digits[-1]
    value_as_str = f"{first_digit}{last_digit}"
    return int(value_as_str)


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
