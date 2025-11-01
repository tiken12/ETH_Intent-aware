from typing import Dict, Any
from app.core.utils import stable_hash

def attestation(payload: Dict[str, Any]) -> Dict[str, str]:
    # Hash nested structures into short fields for logs
    out = {}
    for k,v in payload.items():
        if isinstance(v, (dict, list)):
            out[k] = stable_hash(v)
        else:
            out[k] = str(v)
    return out
