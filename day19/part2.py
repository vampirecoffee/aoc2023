"""Part 1 of the 'Aplenty' problem."""

from __future__ import annotations

import argparse
from collections import defaultdict
import itertools
from dataclasses import dataclass, asdict
import math
from enum import Enum
import re
from typing import Optional, Union

from tqdm import tqdm  # type: ignore[import-untyped]


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
class PartInterval:
    x: tuple[int, int]
    m: tuple[int, int]
    a: tuple[int, int]
    s: tuple[int, int]

    def change_interval(
        self, interval_name: str, new_interval: tuple[int, int]
    ) -> PartInterval:
        """Return a copy with the relevant interval changed."""
        if interval_name == "x":
            return PartInterval(new_interval, self.m, self.a, self.s)
        elif interval_name == "m":
            return PartInterval(self.x, new_interval, self.a, self.s)
        elif interval_name == "a":
            return PartInterval(self.x, self.m, new_interval, self.s)
        elif interval_name == "s":
            return PartInterval(self.x, self.m, self.a, new_interval)
        else:
            raise ValueError(f"Unrecognized interval name {interval_name}")

    @property
    def total(self) -> int:
        """How many combinations does this interval contain?"""
        return math.prod(
            high - low + 1 for low, high in [self.x, self.m, self.a, self.s]
        )


@dataclass(frozen=True)
class Condition:
    """Rule condition."""

    attr: str
    gt_lt: str
    val: int

    def matches(self, part: Part) -> bool:
        """Does this condition match this part?"""
        attr_val = asdict(part)[self.attr]

        if self.gt_lt == "<":
            return attr_val < self.val
        else:
            return attr_val > self.val

    def interval_matches(
        self, pi: PartInterval
    ) -> tuple[Optional[PartInterval], Optional[PartInterval]]:
        """For an interval, return the part that matches and the part that doesn't."""
        low, high = asdict(pi)[self.attr]
        # Case where no values match
        if (self.gt_lt == ">" and self.val >= high) or (
            self.gt_lt == "<" and self.val <= low
        ):
            return (None, pi)
        # Case where all values match
        if (self.gt_lt == ">" and self.val < low) or (
            self.gt_lt == "<" and self.val > high
        ):
            return (pi, None)

        match_interval: tuple[int, int]
        no_match_interval: tuple[int, int]
        if self.gt_lt == ">":
            match_interval = (self.val + 1, high)
            no_match_interval = (low, self.val)
        else:
            match_interval = (low, self.val - 1)
            no_match_interval = (self.val, high)
        mpi = pi.change_interval(self.attr, match_interval)
        nmpi = pi.change_interval(self.attr, no_match_interval)
        return mpi, nmpi


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

    def applies_to(self, part: Part) -> bool:
        """Does this rule apply to this part?"""
        if self.cond is None:
            return True
        return self.cond.matches(part)

    def interval_applies_to(
        self, pi: PartInterval
    ) -> tuple[Optional[PartInterval], Optional[PartInterval]]:
        """For an interval, return:
        - the part of the interval that this rule applies to
        - the part that doesn't
        """
        if self.cond is None:
            return (pi, None)
        return self.cond.interval_matches(pi)


_workflow_re = re.compile(r"(\w+)\{(.*)\}")


@dataclass(frozen=True)
class IntervalTarget:
    pi: PartInterval
    to: Union[str, Status]


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

    def interval_apply(self, pi: PartInterval) -> list[IntervalTarget]:
        """Apply this workflow to an interval."""
        tgts: list[IntervalTarget] = []
        for r in self.rules:
            applies_to, does_not_apply_to = r.interval_applies_to(pi)
            if applies_to is not None:
                tgts.append(IntervalTarget(pi=applies_to, to=r.send_to))
            if does_not_apply_to is None:
                return tgts
            pi = does_not_apply_to
        return tgts


def apply_workflows(workflows: dict[str, Workflow], part: Part) -> Status:
    """Apply a collection of workflows to this part."""
    cur: Union[str, Status] = "in"
    while not isinstance(cur, Status):
        cur = workflows[cur].apply(part)
    return cur


def interval_apply_workflows(workflows: dict[str, Workflow], pi: PartInterval) -> int:
    total_accepted = 0
    queue: list[IntervalTarget] = [IntervalTarget(pi, "in")]
    with tqdm(total=pi.total) as pbar:
        while queue:
            cur_step = queue.pop()
            if isinstance(cur_step.to, Status):
                if cur_step.to == Status.Accept:
                    total_accepted += cur_step.pi.total
                pbar.update(cur_step.pi.total)
                continue
            new_steps = workflows[cur_step.to].interval_apply(cur_step.pi)
            for step in new_steps:
                queue.append(step)
    return total_accepted


def score_parts(workflows: dict[str, Workflow], parts: list[Part]) -> int:
    """Score all accepted parts."""
    out = 0
    for p in parts:
        if apply_workflows(workflows, p) == Status.Accept:
            out += p.rating
    return out


def stupid_part_2_solution(workflows: dict[str, Workflow]) -> int:
    """A very, very stupid solution to part 2."""
    accepted = 0
    total = 4000 * 4000 * 4000 * 4000
    with tqdm(total=total) as pbar:
        for x, m, a, s in tqdm(itertools.product(range(1, 4001), repeat=4)):
            p = Part(x, m, a, s)
            if apply_workflows(workflows, p) == Status.Accept:
                accepted += 1
            pbar.update(1)
    return accepted


def less_stupid_part_2(workflows: dict[str, Workflow]) -> int:
    """Less stupid solution to part 2."""
    pi = PartInterval(
        x=(1, 4000),
        m=(1, 4000),
        a=(1, 4000),
        s=(1, 4000),
    )
    return interval_apply_workflows(workflows, pi)


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
    return less_stupid_part_2(workflows)


def main():
    """Main function."""
    parser = argparse.ArgumentParser()
    parser.add_argument("filename")
    args = parser.parse_args()
    print(args.filename)
    print(parse_file(args.filename))


if __name__ == "__main__":
    main()
