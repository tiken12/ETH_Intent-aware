import hashlib, json

def keccak_hex(data: bytes) -> str:
    # web3 has Web3.keccak; keeping a local helper for attestation hashing
    try:
        from eth_utils import keccak
        return "0x" + keccak(data).hex()
    except Exception:
        # fallback sha256 (not keccak) if eth_utils missing (shouldn't happen)
        return "0x" + hashlib.sha256(data).hexdigest()

def stable_hash(obj) -> str:
    s = json.dumps(obj, sort_keys=True, separators=(",", ":")).encode()
    return keccak_hex(s)
