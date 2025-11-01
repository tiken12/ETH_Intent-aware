from fastapi import APIRouter, Query
from app.models.schemas import EIP712TypedData, UserOperation, Verdict, SimCallNode
from app.eip712.parser import eip712_hash
from app.eip712.renderer import render_plain
from app.policies.eip712 import lint_eip712
from app.simulate.aa import simulate_validation
from app.policies.eip4337 import lint_userop
from app.explain.rationale import from_issues
from app.explain.attestation import attestation
from app.correlate.dag import IntentDAG, IntentEvent
from app.correlate.linkers import deterministic_link, probabilistic_link
from app.policies.crosschain import conservation_check

router = APIRouter(prefix="/v1")

def decide(issues):
    # Any error → BLOCK; any warn → WARN; else ALLOW
    sev = [i.sev for i in issues]
    if "error" in sev: return "BLOCK"
    if "warn" in sev: return "WARN"
    return "ALLOW"

@router.post("/validate/eip712", response_model=Verdict)
def validate_eip712(body: EIP712TypedData, blockTag: str = Query("latest")):
    issues = lint_eip712(body)
    decision = decide(issues)
    rationale = from_issues(issues)
    att = attestation({
        "type": "eip712",
        "hash": eip712_hash(body),
        "render": render_plain(body),
        "blockTag": blockTag
    })
    return Verdict(decision=decision, rationale=rationale, attestation=att)

@router.post("/validate/4337", response_model=Verdict)
def validate_4337(body: UserOperation, blockTag: str = Query("latest")):
    tree: SimCallNode = simulate_validation(body)
    issues = lint_userop(tree, body)
    # Cross-chain (optional): if client passes events later, stitch and check conservation.
    decision = decide(issues)
    rationale = from_issues(issues)
    att = attestation({
        "type": "4337",
        "sender": body.sender,
        "callTree": tree.model_dump(),
        "blockTag": blockTag
    })
    return Verdict(decision=decision, rationale=rationale, attestation=att)

@router.post("/validate/crosschain", response_model=Verdict)
def validate_crosschain(events: list[dict]):
    dag = IntentDAG()
    evobjs = [IntentEvent(**e) for e in events]
    logs = []
    logs += deterministic_link(dag, evobjs)
    logs += probabilistic_link(dag, evobjs)
    issues = []
    if evobjs:
        issues += conservation_check(dag, evobjs[0].eid)
    decision = decide(issues)
    rationale = from_issues(issues) + [f"link:{m}" for m in logs]
    att = attestation({"type": "xchain", "edges": list(dag.edges())})
    return Verdict(decision=decision, rationale=rationale, attestation=att)
