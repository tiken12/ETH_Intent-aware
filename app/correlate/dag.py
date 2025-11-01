from dataclasses import dataclass, field
from typing import Dict, List, Tuple
import networkx as nx

@dataclass
class IntentEvent:
    eid: str
    chain: int
    kind: str   # swap | bridge_out | bridge_in | claim | settle
    token: str
    amount: float
    meta: Dict

class IntentDAG:
    def __init__(self):
        self.g = nx.DiGraph()
    def add(self, ev: IntentEvent):
        self.g.add_node(ev.eid, ev=ev)
    def link(self, src: str, dst: str, confidence: float = 1.0):
        self.g.add_edge(src, dst, confidence=confidence)
    def path_amounts(self, start: str) -> Dict[str, float]:
        # toy aggregation along reachable nodes
        out = {}
        for nid in nx.descendants(self.g, start) | {start}:
            ev: IntentEvent = self.g.nodes[nid]["ev"]
            out[ev.token] = out.get(ev.token, 0.0) + ev.amount
        return out
    def edges(self):
        return self.g.edges(data=True)
