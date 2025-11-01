from app.models.schemas import EIP712TypedData
from .parser import infer_permit_like, numeric_field, expiry_field

def render_plain(typed: EIP712TypedData) -> str:
    d = typed.domain
    summary = [f"Primary: {typed.primaryType}", f"ChainId: {d.chainId}"]
    if d.verifyingContract:
        summary.append(f"VerifyingContract: {d.verifyingContract}")
    msg = typed.message
    if infer_permit_like(typed):
        spender = msg.get("spender", "")
        amt = numeric_field(typed)
        exp = expiry_field(typed)
        extra = []
        if amt is not None: extra.append(f"amount={amt}")
        if exp is not None: extra.append(f"expiry={exp}s")
        summary.append(f"Permit-like: spender={spender} {' '.join(extra)}")
    return " | ".join(summary)
