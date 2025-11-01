from typing import List
from app.policies.eip712 import Issue as I712
from app.policies.eip4337 import Issue as I4337
from app.policies.crosschain import Issue as IX

def from_issues(issues: List[object]) -> List[str]:
    out = []
    for it in issues:
        code = getattr(it, "code", "POL")
        msg  = getattr(it, "msg", "")
        out.append(f"{code}: {msg}")
    return out
