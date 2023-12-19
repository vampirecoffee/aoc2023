"""Part 1 of the 'Aplenty' problem."""

from __future__ import annotations

import argparse
from collections import defaultdict
from dataclasses import dataclass
from enum import Enum
import re
from typing import Optional, Union


class Status(Enum):
    Reject = 0
    Accept = 1


_part_re = re.compile(r"\{x=(\d+),m=(\d+),a=(\d+),s=(\d+)\}")


@dataclass(frozen=True)
class Part:
    x: int
    m: int
    a: int
    s: int

    @classmethod
    def from_str(cls, s_in: str) -> Part:
        """Create a part from a string."""
        match = _part_re.search(s_in)
        if not match:
            raise RuntimeError(f"could not get {s_in} to match part regex")
        x = int(match.group(1))
        m = int(match.group(2))
        a = int(match.group(3))
        s = int(match.group(4))
        return cls(x, m, a, s)

    @property
    def rating(self) -> int:
        return self.x + self.m + self.a + self.s


@dataclass(frozen=True)
class Condition:
    """Rule condition."""

    attr: str
    gt_lt: str
    val: int

    def matches(self, part) -> bool:
        """Does this condition match this part?"""
        attr_val: int = 0
        if self.attr == "x":
            attr_val = part.x
        elif self.attr == "m":
            attr_val = part.m
        elif self.attr == "a":
            attr_val = part.a
        elif self.attr == "s":
            attr_val = part.s
        else:
            raise RuntimeError(f"attr should be x/m/a/s, not {self.attr}")

        if self.gt_lt == "<":
            return attr_val < self.val
        else:
            return attr_val > self.val


_rule_re = re.compile(r"(x|m|a|s)(<|>)(\d+):(\w+)")


@dataclass(frozen=True)
class Rule:
    cond: Optional[Condition]
    _send_to: str  # workflow to send matching parts to

    @property
    def send_to(self) -> Union[Status, str]:
        """Where to send this."""
        if self._send_to == "R":
            return Status.Reject
        elif self._send_to == "A":
            return Status.Accept
        else:
            return self._send_to

    @classmethod
    def from_str(cls, s_in: str) -> Rule:
        """Create a rule from a string."""
        if "<" in s_in or ">" in s_in:
            match = _rule_re.search(s_in)
            if not match:
                raise RuntimeError(f"could not get {s_in} to match rule regex")
            attr = match.group(1)
            gt_lt = match.group(2)
            val = int(match.group(3))
            cond = Condition(attr, gt_lt, val)
            send_to = match.group(4)
            return cls(cond, send_to)
        else:
            s_in = s_in.strip()
            return cls(cond=None, _send_to=s_in)

    def applies_to(self, part) -> bool:
        """Does this rule apply to this part?"""
        if self.cond is None:
            return True
        return self.cond.matches(part)


_workflow_re = re.compile(r"(\w+)\{(.*)\}")


@dataclass(frozen=True)
class Workflow:
    name: str
    rules: list[Rule]

    @classmethod
    def from_str(cls, s_in: str) -> Workflow:
        """Create a workflow from a string."""
        match = _workflow_re.search(s_in)
        assert match is not None
        name = match.group(1)
        rule_str = match.group(2)
        rules = [Rule.from_str(r) for r in rule_str.split(",")]
        return cls(name, rules)

    def apply(self, part) -> Union[Status, str]:
        """Apply a workflow to a part."""
        for r in self.rules:
            if r.applies_to(part):
                return r.send_to
        raise RuntimeError("No rules applied :(")


def apply_workflows(workflows: dict[str, Workflow], part: Part) -> Status:
    """Apply a collection of workflows to this part."""
    print("part:", part)
    cur: Union[str, Status] = "in"
    while not isinstance(cur, Status):
        print("applying workflow named:", cur)
        cur = workflows[cur].apply(part)
    return cur


def score_parts(workflows: dict[str, Workflow], parts: list[Part]) -> int:
    """Score all accepted parts."""
    out = 0
    for p in parts:
        if apply_workflows(workflows, p) == Status.Accept:
            print("accepting part", p)
            out += p.rating
        else:
            print("rejecting part", p)
    return out


def parse_file(filename: str) -> int:
    """Parse file, do thing."""
    workflow_strs: list[str] = []
    part_strs: list[str] = []
    with open(filename) as f:
        for line in f:
            line = line.strip()
            if not line:
                break
            workflow_strs.append(line)
        for line in f:
            line = line.strip()
            if line:
                part_strs.append(line)
    workflows: dict[str, Workflow] = {}
    for s in workflow_strs:
        w = Workflow.from_str(s)
        workflows[w.name] = w
    parts = [Part.from_str(s) for s in part_strs]
    return score_parts(workflows, parts)


def main():
    """Main function."""
    parser = argparse.ArgumentParser()
    parser.add_argument("filename")
    args = parser.parse_args()
    print(args.filename)
    print(parse_file(args.filename))


if __name__ == "__main__":
    main()
