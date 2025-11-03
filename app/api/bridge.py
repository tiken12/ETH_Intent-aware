# app/api/bridge.py
from fastapi import APIRouter, HTTPException
from web3 import Web3
import os, yaml

from app.correlate.linkers import BridgeAdapter, fetch_bridge_src_events

router = APIRouter(prefix="/v1/bridge", tags=["bridge"])

def _env(name: str) -> str | None:
    v = os.getenv(name)
    return v if v and v.strip() else None

def _rpc_for_chain(chain_id: int) -> str | None:
    # Read RPCs straight from environment (.env is loaded at process start by your app)
    return {
        1:  _env("RPC_MAINNET"),
        10: _env("RPC_OPTIMISM"),
        42161: _env("RPC_ARBITRUM"),
        8453: _env("RPC_BASE"),
    }.get(chain_id)

def _load_cfg() -> dict:
    cfg_path = os.getenv("INTENT_GUARD_CONFIG", "config.yaml")
    with open(cfg_path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f) or {}

@router.get("/fetch/src/{adapter_name}")
def fetch_src(adapter_name: str):
    cfg = _load_cfg()
    adapters = cfg.get("bridges", [])
    found = next((a for a in adapters if a.get("name") == adapter_name), None)
    if not found:
        raise HTTPException(404, f"adapter {adapter_name} not found in config.yaml")

    rpc = _rpc_for_chain(int(found["src_chain"]))
    if not rpc:
        raise HTTPException(500, f"No RPC configured for chain {found['src_chain']}")

    w3 = Web3(Web3.HTTPProvider(rpc, request_kwargs={"timeout": 20}))

    adapter = BridgeAdapter(
        name=found["name"],
        src_chain=int(found["src_chain"]),
        dst_chain=int(found["dst_chain"]),
        src_address=found["src_address"],
        event_signature=found["event_signature"],
        fields=found["fields"],
        from_block=found.get("from_block", "latest-5000"),
        to_block=found.get("to_block", "latest"),
    )

    events = fetch_bridge_src_events(w3, adapter)
    return [e.__dict__ for e in events]


@router.get("/fetch/debug/{adapter_name}")
def fetch_debug(adapter_name: str, span: int = 200000):
    cfg = _load_cfg()
    adapters = cfg.get("bridges", [])
    found = next((a for a in adapters if a.get("name")==adapter_name), None)
    if not found:
        raise HTTPException(404, f"adapter {adapter_name} not found in config.yaml")
    rpc = _rpc_for_chain(int(found["src_chain"]))
    if not rpc:
        raise HTTPException(500, f"No RPC configured for chain {found['src_chain']}")
    w3 = Web3(Web3.HTTPProvider(rpc, request_kwargs={"timeout": 20}))
    latest = w3.eth.block_number
    from_b = max(0, latest - span)
    topic0 = Web3.keccak(text=found["event_signature"]).hex()
    logs = w3.eth.get_logs({
        "address": Web3.to_checksum_address(found["src_address"]),
        "fromBlock": from_b,
        "toBlock": latest,
        "topics": [topic0]
    })
    return {
        "adapter": adapter_name,
        "rpc_chain": int(found["src_chain"]),
        "address": Web3.to_checksum_address(found["src_address"]),
        "event_signature": found["event_signature"],
        "topic0": topic0,
        "from_block": from_b,
        "to_block": latest,
        "log_count": len(logs),
        "sample_tx": logs[0]["transactionHash"].hex() if logs else None
    }
