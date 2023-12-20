from __future__ import annotations

import argparse
from collections import defaultdict
from copy import deepcopy
from abc import ABC, abstractmethod
from functools import cache
from dataclasses import dataclass, field
from enum import Enum
from typing import Optional
import math
import re

from frozendict import frozendict


class Pulse(Enum):
    LOW = 0
    HIGH = 1


@dataclass(frozen=True)
class Signal:
    pulse: Pulse  # kind of pulse that was sent
    fr: str  # name of module that pulse is from
    to: str  # name of module to send to

    def __str__(self) -> str:
        """String (formatted like examples in the problem)."""
        hilo: str
        if self.pulse == Pulse.LOW:
            hilo = "low"
        else:
            hilo = "high"
        return f"{self.fr} -{hilo}-> {self.to}"


@dataclass
class Module(ABC):
    name: str
    send_to: list[str] = field(default_factory=list)

    @abstractmethod
    def handle_pulse(self, pulse: Pulse, from_module: str) -> list[Signal]:
        """Handle a pulse; return the signals sent out."""
        ...

    def _send_to_all(self, pulse: Pulse) -> list[Signal]:
        """Send the same pulse to all outputs."""
        return [
            Signal(pulse=pulse, fr=self.name, to=to_name) for to_name in self.send_to
        ]


@dataclass(frozen=True)
class FrozenModule:
    name: str
    send_to: tuple[str, ...]


@cache
def _frozen_send_to_all(fm: FrozenModule, pulse: Pulse) -> list[Signal]:
    return [Signal(pulse=pulse, fr=fm.name, to=to_name) for to_name in fm.send_to]


@dataclass(frozen=True)
class FrozenFlipFlop(FrozenModule):
    name: str
    send_to: tuple[str, ...]
    on: bool


@cache
def _handle_flip_flop_pulse(fm: FrozenFlipFlop, pulse: Pulse) -> list[Signal]:
    """Handle a flip-flop pulse."""
    if pulse == Pulse.HIGH:
        return []
    # these are in the opposite order from the problem statement
    pulse_out: Pulse
    if fm.on:
        return _frozen_send_to_all(fm, Pulse.LOW)
    else:  # module was off
        return _frozen_send_to_all(fm, Pulse.HIGH)


@dataclass
class FlipFlop(Module):
    on: bool = False

    def freeze(self) -> FrozenFlipFlop:
        """Return a frozen copy."""
        tst = tuple(s for s in self.send_to)
        return FrozenFlipFlop(self.name, tst, self.on)

    def handle_pulse(self, pulse: Pulse, _: str) -> list[Signal]:
        """Handle flip-flop pulse.

        Flip-flops do not care where their input came from.
        """
        fm = self.freeze()
        out = _handle_flip_flop_pulse(fm, pulse)
        if pulse == Pulse.LOW:
            self.on = not self.on
        return out


@dataclass(frozen=True)
class FrozenConjunction(FrozenModule):
    most_recent_signal: frozendict[str, Pulse]


@cache
def _handle_conjunction_pulse(
    fm: FrozenConjunction, pulse: Pulse, from_module: str
) -> list[Signal]:
    """Handle a conjunction pulse."""
    fd = fm.most_recent_signal.set(from_module, pulse)
    if all(p == Pulse.HIGH for p in fd.values()):
        return _frozen_send_to_all(fm, Pulse.LOW)
    else:
        return _frozen_send_to_all(fm, Pulse.HIGH)


@dataclass
class Conjunction(Module):
    most_recent_signal: dict[str, Pulse] = field(default_factory=dict)

    def freeze(self) -> FrozenConjunction:
        """Return a frozen copy."""
        tst = tuple(s for s in self.send_to)
        return FrozenConjunction(self.name, tst, frozendict(self.most_recent_signal))

    def handle_pulse(self, pulse: Pulse, from_module: str) -> list[Signal]:
        """Handle pulse for conjunction."""
        fm = self.freeze()
        self.most_recent_signal[from_module] = pulse
        return _handle_conjunction_pulse(fm, pulse, from_module)


class Broadcast(Module):
    """Broadcast module (just a repeater)."""

    name = "broadcaster"

    @cache
    def handle_pulse(self, pulse: Pulse, _: str) -> list[Signal]:
        return self._send_to_all(pulse)

    def __hash__(self) -> int:
        """Hash."""
        return hash(self.name) + hash(tuple(e for e in self.send_to))


_module_re = re.compile(r"(.)(\w+) -> ([\w ,]+)")


@dataclass
class Network:
    """Class representing the whole network of button + modules."""

    modules: dict[str, Module] = field(default_factory=dict)
    pulses_sent: dict[Pulse, int] = field(
        default_factory=lambda: {Pulse.LOW: 0, Pulse.HIGH: 0}
    )
    _missing_paths: list[tuple[str, str]] = field(default_factory=list)

    def _handle_missing_paths(self) -> None:
        """Handle missing paths.

        If the path exists now:
        - ensure that receiving conjunctions have memory set
        - remove it from the list of missing paths
        """
        if not self._missing_paths:
            return
        handled: list[tuple[str, str]] = []
        for from_module, to_module in self._missing_paths:
            if not to_module in self.modules:
                continue
            m = self.modules[to_module]
            if not isinstance(m, Conjunction):
                handled.append((from_module, to_module))
                continue
            m.most_recent_signal[from_module] = Pulse.LOW
            self.modules[to_module] = m
            handled.append((from_module, to_module))

        self._missing_paths = [e for e in self._missing_paths if not e in handled]

    def add_module(self, s: str) -> None:
        """Add a module to this network."""
        self_needs_memset = True  # Might need to re-set conjunction memory later
        module: Module
        s = s.strip()
        if s.startswith("broadcaster"):
            arrow_idx = s.index(">")
            send_to_str = s[arrow_idx + 1 :]
            send_to = [s.strip() for s in send_to_str.split(",")]
            module = Broadcast(name="broadcaster", send_to=send_to)
        else:
            match = _module_re.search(s)
            if not match:
                raise RuntimeError(f"could not get {s} to match module regex")
            module_type = match.group(1)
            module_name = match.group(2)
            send_to = [s.strip() for s in match.group(3).split(",")]
            if module_type == "%":
                module = FlipFlop(name=module_name, send_to=send_to)
            elif module_type == "&":
                module = Conjunction(name=module_name, send_to=send_to)

        print("adding module", module)
        self.modules[module.name] = module
        for to_name in module.send_to:
            self._missing_paths.append((module.name, to_name))

        self._handle_missing_paths()

    def push_button(self) -> list[Signal]:
        """Push the button.

        Returns a list of all signals sent.
        """
        signals_to_send: list[Signal] = [
            Signal(pulse=Pulse.LOW, fr="xx_button_xx", to="broadcaster")
        ]
        signals_sent: list[Signal] = []

        sent_low_to_rx = False
        while signals_to_send:
            sig = signals_to_send[0]
            signals_sent.append(sig)
            signals_to_send = signals_to_send[1:]
            if sig.to == "rx" and sig.pulse == Pulse.LOW:
                sent_low_to_rx = True
            new_signals = self._send_signal(sig)
            for new_sig in new_signals:
                signals_to_send.append(new_sig)

        return signals_sent

    def _send_signal(self, sig: Signal) -> list[Signal]:
        """Send one signal.

        Returns the list of new signals.
        """
        self.pulses_sent[sig.pulse] += 1
        if not sig.to in self.modules:
            return []
        return self.modules[sig.to].handle_pulse(sig.pulse, sig.fr)

    def count_pulses_sent(self, push_n_times=1000) -> int:
        """Count pulses sent by pushing the button N times."""

        for _ in range(push_n_times):
            self.push_button()

        print(self.pulses_sent)

        return self.pulses_sent[Pulse.LOW] * self.pulses_sent[Pulse.HIGH]

    def push_until_rx_low(self) -> int:
        """How many times must we push the button until we send LOW to rx?"""
        button_pushes = 0
        sent_low_to_rx = False
        while not sent_low_to_rx:
            sent_signals = self.push_button()
            sent_low_to_rx = any(
                sig.to == "rx" and sig.pulse == Pulse.LOW for sig in sent_signals
            )
            button_pushes += 1
            if (button_pushes % 10000) == 0:
                tpushes = int(button_pushes / 1000)
                print("sent", tpushes, "thousand pushes")
            if (button_pushes % 1000000) == 0:
                mpushes = int(button_pushes / 1000000)
                print("sent", mpushes, "million pushes")
        return button_pushes

    def lcm_rx_low(self) -> int:
        """Use least common multiple to find how to send LOW to rx.

        This only works on the specific input file :eyeroll: .
        """
        rx_sources: set[str] = set()  # set of module names that send to rx
        for k, v in self.modules.items():
            if "rx" in v.send_to:
                assert isinstance(v, Conjunction)
                rx_sources.add(v.name)

        assert len(rx_sources) == 1
        rx_source_name: str = list(rx_sources)[0]

        # Signals that might cause rx_source to send low to rx
        sends_to_rx_source: set[str] = set()
        for k, v in self.modules.items():
            if any(to_name == rx_source_name for to_name in v.send_to):
                assert isinstance(v, Conjunction)
                sends_to_rx_source.add(k)

        # We eventually want all signals sent to rx_source to be HIGH
        want_signals = set(
            Signal(pulse=Pulse.HIGH, fr=from_name, to=rx_source_name)
            for from_name in sends_to_rx_source
        )
        print(want_signals)

        cycles_in: dict[Signal, int] = {}
        button_pushes = 0
        while want_signals:
            signals_sent = self.push_button()
            button_pushes += 1

            for sig in signals_sent:
                if sig in want_signals:
                    want_signals.remove(sig)
                    cycles_in[sig] = button_pushes
                    print(cycles_in)

        return math.lcm(*list(cycles_in.values()))


def parse_file(filename: str) -> int:
    """Parse file, solve problem."""
    network = Network()
    with open(filename) as f:
        for line in f:
            line = line.strip()
            if line:
                network.add_module(line)
    # network.push_button()
    # return network.count_pulses_sent()
    # return network.push_until_rx_low()
    return network.lcm_rx_low()


def main():
    """Main function."""
    parser = argparse.ArgumentParser()
    parser.add_argument("filename")
    args = parser.parse_args()
    print(args.filename)
    print(parse_file(args.filename))


if __name__ == "__main__":
    main()
