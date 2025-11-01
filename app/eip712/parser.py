from app.models.schemas import EIP712TypedData
from eth_account.messages import encode_structured_data
from app.core.utils import stable_hash

def eip712_hash(typed: EIP712TypedData) -> str:
    # Convert to dict for encode_structured_data
    data = {
        "types": typed.types,
        "primaryType": typed.primaryType,
        "domain": typed.domain.model_dump(),
        "message": typed.message
    }
    msg = encode_structured_data(primitive=data)
    return "0x" + msg.hash.hex()

def infer_permit_like(typed: EIP712TypedData) -> bool:
    fields = set(k.lower() for k in typed.message.keys())
    return ("spender" in fields) and ({"value","amount","allowance"} & fields)

def numeric_field(typed: EIP712TypedData, names=("value","amount","allowance")) -> int | None:
    for k in names:
        if k in typed.message:
            try:
                return int(typed.message[k])  # may be decimal string
            except Exception:
                pass
    return None

def expiry_field(typed: EIP712TypedData) -> int | None:
    for k in ("deadline","expiry","expiration"):
        if k in typed.message:
            try:
                return int(typed.message[k])
            except Exception:
                pass
    return None
