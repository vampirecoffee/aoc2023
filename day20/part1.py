from __future__ import annotations

import argparse
from collections import defaultdict
from copy import deepcopy
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from enum import Enum
from typing import Optional
import re


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


@dataclass
class FlipFlop(Module):
    on: bool = False

    def handle_pulse(self, pulse: Pulse, _: str) -> list[Signal]:
        """Handle flip-flop pulse.

        Flip-flops do not care where their input came from.
        """
        if pulse == Pulse.HIGH:
            return []
        # these are in the opposite order from the problem statement
        pulse_out: Pulse
        if self.on:
            self.on = False
            return self._send_to_all(Pulse.LOW)
        else:  # module was off
            self.on = True
            return self._send_to_all(Pulse.HIGH)


@dataclass
class Conjunction(Module):
    most_recent_signal: dict[str, Pulse] = field(default_factory=dict)

    def handle_pulse(self, pulse: Pulse, from_module: str) -> list[Signal]:
        """Handle pulse for conjunction."""
        self.most_recent_signal[from_module] = pulse
        pulse_out: Pulse
        if all(p == Pulse.HIGH for p in self.most_recent_signal.values()):
            return self._send_to_all(Pulse.LOW)
        else:
            return self._send_to_all(Pulse.HIGH)


@dataclass
class Broadcast(Module):
    """Broadcast module (just a repeater)."""

    name = "broadcaster"

    def handle_pulse(self, pulse: Pulse, _: str) -> list[Signal]:
        return self._send_to_all(pulse)


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

    def push_button(self) -> None:
        """Push the button."""
        signals_to_send: list[Signal] = [
            Signal(pulse=Pulse.LOW, fr="xx_button_xx", to="broadcaster")
        ]

        while signals_to_send:
            sig = signals_to_send[0]
            self.pulses_sent[sig.pulse] += 1
            signals_to_send = signals_to_send[1:]
            if not sig.to in self.modules:
                print("No module named", sig.to, ", skipping...")
                continue
            new_signals = self.modules[sig.to].handle_pulse(sig.pulse, sig.fr)
            for new_sig in new_signals:
                signals_to_send.append(new_sig)

    def count_pulses_sent(self, push_n_times=1000) -> int:
        """Count pulses sent by pushing the button N times."""

        for _ in range(push_n_times):
            self.push_button()

        print(self.pulses_sent)

        return self.pulses_sent[Pulse.LOW] * self.pulses_sent[Pulse.HIGH]


def parse_file(filename: str) -> int:
    """Parse file, solve problem."""
    network = Network()
    with open(filename) as f:
        for line in f:
            line = line.strip()
            if line:
                network.add_module(line)
    # network.push_button()
    return network.count_pulses_sent()


def main():
    """Main function."""
    parser = argparse.ArgumentParser()
    parser.add_argument("filename")
    args = parser.parse_args()
    print(args.filename)
    print(parse_file(args.filename))


if __name__ == "__main__":
    main()
