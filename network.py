from dataclasses import dataclass
import numpy as np

from agent import NetworkMember, Agent

@dataclass
class Network:
    agents: list[NetworkMember]
    disinfo_agents: list[NetworkMember]

    def play_round(self):
        for agent in self.agents:
            agent.roll_atrophy()
            
        for agent in self.agents:
            # Everybody but self is a potential audience
            audience = [a for a in self.agents if a.id != agent.id]
            agent.decide_communication(audience)

        for disinfo_agent in self.disinfo_agents:
            audience = [a for a in self.agents]
            disinfo_agent.decide_communication(audience)

        # We atrophy, then send messages, above. 
        # Then everyone updates their beliefs (except disinfo agents)
        for agent in self.agents:
            agent.process_signals()


