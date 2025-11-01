from typing import List
from app.models.schemas import SimCallNode, UserOperation
from app.core.config import POLICY
from app.eip4337.userop import has_suspicious_selectors

class Issue:
    def __init__(self, code, msg, sev="warn"): self.code, self.msg, self.sev = code, msg, sev

def _scan_delegatecall(node: SimCallNode, out: List[Issue]):
    if node.selector.lower().startswith("delegatecall"):
        out.append(Issue("AA-DEL", f"delegatecall at {node.target}", "error"))
    for ch in node.children:
        _scan_delegatecall(ch, out)

def lint_userop(call_tree: SimCallNode, userop: UserOperation) -> List[Issue]:
    issues: List[Issue] = []
    pol = POLICY["eip4337"]
    vetted_factories = set(a.lower() for a in pol.get("vetted_factories", []))
    vetted_pm = set(a.lower() for a in pol.get("vetted_paymasters", []))
    block_delegatecall = pol.get("block_delegatecall", True)

    # delegatecall
    tmp: List[Issue] = []
    _scan_delegatecall(call_tree, tmp)
    if block_delegatecall:
        issues.extend(tmp)

    # factory/paymaster allowlists (trivial parsing from userop)
    if userop.paymasterAndData and len(userop.paymasterAndData) >= 42:
        pm = "0x" + userop.paymasterAndData[2:42].lower()
        if vetted_pm and pm not in vetted_pm:
            issues.append(Issue("AA-PM", f"unvetted paymaster {pm}", "warn"))

    # suspicious selectors
    if has_suspicious_selectors(userop.callData):
        issues.append(Issue("AA-APR", f"approval/permit-like selector in callData", "warn"))
    return issues
