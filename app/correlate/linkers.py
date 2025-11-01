from typing import List, Tuple
from app.correlate.dag import IntentDAG, IntentEvent
from app.core.config import XCHAIN

def deterministic_link(dag: IntentDAG, events: List[IntentEvent]) -> List[str]:
    """
    Link by shared messageId (out/in). This assumes events meta have 'messageId'.
    """
    by_id = {}
    logs = []
    for ev in events:
        dag.add(ev)
        mid = ev.meta.get("messageId")
        if not mid: continue
        if mid in by_id:
            # naive: first is out, second is in
            dag.link(by_id[mid], ev.eid, confidence=1.0)
            logs.append(f"link {by_id[mid]} -> {ev.eid}")
        else:
            by_id[mid] = ev.eid
    return logs

def probabilistic_link(dag: IntentDAG, events: List[IntentEvent]) -> List[str]:
    """
    If no messageId, match by (token, amount within tol, time window).
    """
    tol_bps = XCHAIN["probabilistic"]["amount_tol_bps"]
    logs = []
    evs = events[:]
    for i in range(len(evs)):
        for j in range(i+1, len(evs)):
            a, b = evs[i], evs[j]
            if a.token != b.token: continue
            if a.chain == b.chain: continue
            base = max(abs(a.amount), 1e-12)
            if abs(a.amount - b.amount) <= (tol_bps/10000)*base:
                dag.link(a.eid, b.eid, confidence=0.7)
                logs.append(f"p-link {a.eid} -> {b.eid} (0.7)")
    return logs
