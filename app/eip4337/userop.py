from app.models.schemas import UserOperation
from eth_abi import abi
from typing import List

# Minimal helpers; extend with full ABI as needed.
APPROVAL_SELECTORS = {"0x095ea7b3", "0x2e1a7d4d"}  # approve(), withdraw(uint256), etc. (example)

def extract_selectors_from_calldata(calldata_hex: str) -> List[str]:
    ch = calldata_hex.lower().replace("0x","")
    if len(ch) < 8: return []
    return ["0x" + ch[:8]]

def has_suspicious_selectors(calldata_hex: str) -> bool:
    sels = set(extract_selectors_from_calldata(calldata_hex))
    return len(sels & APPROVAL_SELECTORS) > 0
