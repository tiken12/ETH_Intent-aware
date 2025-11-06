from fastapi import APIRouter
from web3 import Web3
router = APIRouter()

@router.post("/v1/simulate/eoa")
def simulate_eoa(payload: dict):
    to = payload["to"]; data = payload.get("data","0x"); frm = payload.get("from")
    value = int(payload.get("value","0"), 0) if isinstance(payload.get("value"), str) else payload.get("value",0)
    gas = payload.get("gas")  # optional
    try:
        # dry-run
        res = w3.eth.call({"to": to, "from": frm, "data": data, "value": value, "gas": gas or 1_000_000}, block_identifier="latest")
        return {"will_succeed": True, "result": res.hex()}
    except Exception as e:
        # decode revert if present
        reason = decode_revert(str(e))
        return {"will_succeed": False, "error": reason}
