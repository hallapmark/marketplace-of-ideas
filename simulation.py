from dataclasses import dataclass
from typing import NamedTuple, Optional
import numpy as np
from agent import Agent, NetworkMember
from network import Network

from proposition import *


class SimulationConfiguration(NamedTuple):
    agents_n: int
    # Proportion of agents who start with some belief on the matter
    p_start_belief: float
    # Total rounds of play
    rounds_of_play: int
    # Minimum rounds to belief – an approximation of Time to Belief, Mill
    mrb: int
    # Bonus to agent's base adoption rate for truth (bar_truth = bar + tw/mrb) 
    # – an approximation of Truth Wins, Mill
    tw: float
    # Chance each round that belief along with reasons is forgotten
    # – an approximation of Atrophy, Mill
    atrophy_p: float = 0.2 
    # Minimum base adoption rate (one's trust in testimony)
    # Uniformly distributed between min and max
    min_bar: float = 0.1
    # Maximum base adoption rate
    max_bar: float = 0.90
    # Probability that agent will output signal
    output_p: float = 0.8
    disinfo_agents_n: int = 0
    disinfo_broadcast_capability: int = 1

class SimulationResult(NamedTuple):
    config: SimulationConfiguration
    p_n: int
    q_n: int
    no_belief_n: int

    @property
    def proportion_true_beliefs(self) -> Optional[float]:
        # Nobody has any beliefs. Avoid division by 0
        if self.p_n + self.q_n == 0:
            return None
        return round(self.p_n / (self.p_n + self.q_n), 4)


@dataclass
class Simulation:
    config: SimulationConfiguration

    def __post_init__(self):
        config = self.config
        network_members: list[NetworkMember] = []
        for i in range(config.agents_n):
            start_with_belief = np.random.binomial(1, config.p_start_belief)
            belief = None
            if start_with_belief:
                belief = [Proposition.P, Proposition.Q][np.random.choice((0, 1))]
            network_members.append(
                Agent(
                    id=i,
                    mrb=config.mrb,
                    bar=np.random.uniform(config.min_bar, config.max_bar),
                    tw=config.tw,
                    atrophy_p=config.atrophy_p,
                    output_p=config.output_p,
                    signals_to_process=[],
                    belief=belief,
                    broadcast_capability=config.disinfo_broadcast_capability
                )
            )
        disinfo_agents: list[NetworkMember] = []
        for i in range(config.disinfo_agents_n):
            disinfo_agents.append(
                Agent(
                    id=len(network_members)+i,
                    mrb=0,
                    bar=0,
                    tw=0,
                    atrophy_p=0,
                    output_p=1,
                    signals_to_process=[],
                    belief=Proposition.Q 
                    # not really belief, just what they will broadcast
                )
            )

        starting_beliefs = [a.belief for a in network_members if a.belief]
        # At least one person will have a starting belief
        if len(starting_beliefs) == 0:
            belief = [Proposition.P, Proposition.Q][np.random.choice((0, 1))]
            network_members[0].belief = belief

        self.network = Network(network_members, disinfo_agents)

    def run_sim(self) -> SimulationResult:
        beliefs = [a.belief for a in self.network.agents]
        for i in range(self.config.rounds_of_play):
            self.network.play_round()
        beliefs = [a.belief for a in self.network.agents]
        p_n = beliefs.count(Proposition.P)
        q_n = beliefs.count(Proposition.Q)
        no_belief = beliefs.count(None)
        return SimulationResult(self.config, p_n, q_n, no_belief)
        