from typing import List, Tuple
from app.correlate.dag import IntentDAG
from app.core.config import XCHAIN

class Issue:
    def __init__(self, code, msg, sev="warn"): self.code, self.msg, self.sev = code, msg, sev

def conservation_check(dag: IntentDAG, start_eid: str) -> List[Issue]:
    issues: List[Issue] = []
    amounts = dag.path_amounts(start_eid)
    # naive: require that the token's net flow is near zero (toy example)
    for tkn, amt in amounts.items():
        # In practice you'd separate in/out signs; keeping MVP simple:
        if abs(amt) > 1e-9:
            issues.append(Issue("XCC-CONS", f"Conservation off for {tkn} (sum={amt})", "warn"))
    return issues
