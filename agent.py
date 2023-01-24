from abc import abstractmethod
from dataclasses import dataclass
from typing import Optional, Protocol, runtime_checkable

from proposition import *

import numpy as np


@runtime_checkable
class NetworkMember(Protocol):
    id: int
    belief: Optional[Proposition]

    @abstractmethod
    def roll_atrophy(self) -> None:
        """Atrophy beliefs if not encountered competition."""
        raise NotImplementedError

    @abstractmethod
    def receive_signal(self, signal: Signal) -> None:
        """Send a message to network member."""
        raise NotImplementedError

    @abstractmethod
    def decide_communication(self, audience: list) -> None:
        """Ask network member to decide whether to send out any messages."""

    @abstractmethod
    def process_signals(self) -> None:
        """Ask audience member to process message."""
        raise NotImplementedError


@dataclass
class Agent(NetworkMember):
    id: int
    # Agent's epistemics
    mrb: int  # minimum rounds to belief
    bar: float  # base adoption rate (agent's trust in testimony)
    tw: float  # truth wins; % bonus in adoption rate for true propositions
    atrophy_p: float

    # output probability
    output_p: float

    # Incoming signals
    signals_to_process: list[Signal]
    signals_for_p: int = 0
    signals_for_q: int = 0

    belief: Optional[Proposition] = None

    broadcast_capability: int = 1
    rounds_out_of_competition: int = 0

    @property
    def ric(self) -> int:
        """Total rounds in competition"""
        return self.signals_for_p + self.signals_for_q

    def roll_atrophy(self) -> None:
        if not self.atrophy_p > 0:
            return

        if self.rounds_out_of_competition == 0:
            return

        if np.random.random() >= self.atrophy_p:
            return

        # Forget the belief along with the reasons for holding it
        self.belief = None
        self.signals_for_p = 0
        self.signals_for_q = 0

    def decide_communication(self, audience: list) -> None:
        if not self.belief:
            return

        if np.random.random() >= self.output_p:
            return

        targets = np.random.choice(audience, self.broadcast_capability)
        for t in targets:
            assert isinstance(t, NetworkMember)
            t.receive_signal(Signal(self.belief))

    def receive_signal(self, signal: Signal) -> None:
        self.signals_to_process.append(signal)

    def process_signals(self) -> None:
        if len(self.signals_to_process) == 0:
            self.rounds_out_of_competition += 1
            return

        self.rounds_out_of_competition = 0
        for signal in self.signals_to_process:
            self._process_signal(signal)

    def _process_signal(self, signal: Signal) -> None:
        p = self.bar
        if signal.truth_value == True:
            p += self.tw / p
        if p > 1:
            p = 1
        acknowledge_reason = np.random.binomial(1, p)
        if not acknowledge_reason:
            return

        if signal.proposition == Proposition.P:
            self.signals_for_p += 1
        elif signal.proposition == Proposition.Q:
            self.signals_for_q += 1
        if self.mrb > self.ric:
            return
        self._update_belief()

    def _update_belief(self) -> None:
        if self.signals_for_p > self.signals_for_q:
            self.belief = Proposition.P
        elif self.signals_for_p < self.signals_for_q:
            self.belief = Proposition.Q
