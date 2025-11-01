from typing import List
from app.models.schemas import EIP712TypedData
from app.core.config import POLICY
from app.eip712.parser import infer_permit_like, numeric_field, expiry_field

class Issue:  # tiny struct
    def __init__(self, code, msg, sev="warn"): self.code, self.msg, self.sev = code, msg, sev
    def __repr__(self): return f"{self.sev}:{self.code}:{self.msg}"

def lint_eip712(typed: EIP712TypedData) -> List[Issue]:
    issues: List[Issue] = []
    p = POLICY["eip712"]
    trusted_chain_ids = set(p.get("trusted_chain_ids", []))
    trusted_vc = set(a.lower() for a in p.get("trusted_verifying_contracts", []))
    max_allowance = int(p.get("max_allowance", 10**21))
    max_expiry = int(p.get("max_expiry_seconds", 7*24*3600))

    if trusted_chain_ids and typed.domain.chainId not in trusted_chain_ids:
        issues.append(Issue("P712-CHAIN", f"Untrusted chainId {typed.domain.chainId}", "warn"))

    vc = (typed.domain.verifyingContract or "").lower()
    if trusted_vc and vc and vc not in trusted_vc:
        issues.append(Issue("P712-VERIFY", f"Untrusted verifyingContract {vc}", "warn"))

    if infer_permit_like(typed):
        v = numeric_field(typed)
        if v is not None and v > max_allowance:
            issues.append(Issue("P712-ALLOW", f"Allowance {v} > cap {max_allowance}", "error"))
        exp = expiry_field(typed)
        if exp is not None and exp > max_expiry and exp < 10**12:
            issues.append(Issue("P712-EXP", f"Long expiry ~{exp}s > {max_expiry}s", "warn"))
    return issues
