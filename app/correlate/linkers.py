from typing import List, Tuple
from app.correlate.dag import IntentDAG, IntentEvent
from app.core.config import XCHAIN
from eth_abi import decode as abi_decode
from eth_utils import to_checksum_address

def deterministic_link(dag: IntentDAG, events: List[IntentEvent]) -> List[str]:
    """
    Link by shared messageId (out/in). This assumes events meta have 'messageId'.
    """
    by_id = {}
    logs = []
    for ev in events:
        dag.add(ev)
        mid = ev.meta.get("messageId")
        if not mid: continue
        if mid in by_id:
            # naive: first is out, second is in
            dag.link(by_id[mid], ev.eid, confidence=1.0)
            logs.append(f"link {by_id[mid]} -> {ev.eid}")
        else:
            by_id[mid] = ev.eid
    return logs

def probabilistic_link(dag: IntentDAG, events: List[IntentEvent]) -> List[str]:
    """
    If no messageId, match by (token, amount within tol, time window).
    """
    tol_bps = XCHAIN["probabilistic"]["amount_tol_bps"]
    logs = []
    evs = events[:]
    for i in range(len(evs)):
        for j in range(i+1, len(evs)):
            a, b = evs[i], evs[j]
            if a.token != b.token: continue
            if a.chain == b.chain: continue
            base = max(abs(a.amount), 1e-12)
            if abs(a.amount - b.amount) <= (tol_bps/10000)*base:
                dag.link(a.eid, b.eid, confidence=0.7)
                logs.append(f"p-link {a.eid} -> {b.eid} (0.7)")
    return logs


from dataclasses import dataclass
from typing import Dict, Any
from web3 import Web3
from eth_abi import abi
from app.core.utils import stable_hash
from app.correlate.dag import IntentEvent

@dataclass
class BridgeAdapter:
    name: str
    src_chain: int
    dst_chain: int
    src_address: str                 # L1 (or src) bridge contract
    event_signature: str             # e.g., "ERC20DepositInitiated(address,address,address,address,uint256,bytes)"
    fields: Dict[str, Any]           # mapping (see config)
    from_block: str = "latest-5000"  # supports "latest-N"
    to_block: str   = "latest"

    @property
    def topic0(self) -> str:
        return Web3.keccak(text=self.event_signature).hex()

def _resolve_block(w3: Web3, expr: str) -> int:
    latest = w3.eth.block_number
    if expr == "latest": return latest
    if expr.startswith("latest-"): return max(0, latest - int(expr.split("-",1)[1]))
    if expr.startswith("0x"): return int(expr, 16)
    return int(expr)

def _addr_from_topic(topic_hex: str) -> str:
    # topics are 32 bytes; address is right-most 20 bytes
    b = bytes.fromhex(topic_hex[2:] if topic_hex.startswith("0x") else topic_hex)
    return to_checksum_address("0x" + b[-20:].hex())

def _decode_erc20_deposit_try_abi(data_names: list[str], data_hex: str) -> dict:
    """
    ABI path for data-only fields: ["to","amount","extraData"] -> (address,uint256,bytes)
    """
    type_map = {"to":"address","amount":"uint256","extraData":"bytes"}
    data_types = [type_map[n] for n in data_names]
    data_bytes = bytes.fromhex(data_hex[2:] if isinstance(data_hex, str) and data_hex.startswith("0x") else data_hex)
    vals = abi_decode(data_types, data_bytes)
    out = {}
    for n, v in zip(data_names, vals):
        if hasattr(v, "hex"):
            out[n] = v.hex()
        elif isinstance(v, bytes):
            out[n] = "0x" + v.hex()
        elif isinstance(v, int):
            out[n] = int(v)
        else:
            out[n] = v
    if "to" in out and isinstance(out["to"], str) and out["to"].startswith("0x"):
        out["to"] = to_checksum_address(out["to"])
    return out

def _decode_erc20_deposit_fallback(data_names: list[str], data_hex: str) -> dict:
    """
    Manual parse fallback (no ABI lib), assuming (address,uint256,bytes) in the data section.
    """
    raw = bytes.fromhex(data_hex[2:] if isinstance(data_hex, str) and data_hex.startswith("0x") else data_hex)
    out = {}
    if "to" in data_names and len(raw) >= 32:
        out["to"] = to_checksum_address("0x" + raw[12:32].hex())
    if "amount" in data_names and len(raw) >= 64:
        out["amount"] = int.from_bytes(raw[32:64], byteorder="big", signed=False)
    if "extraData" in data_names:
        out["extraData"] = "0x" + raw[64:].hex() if len(raw) > 64 else "0x"
    return out



def _decode_event_data(event_sig: str, log, indexed_names: list[str], data_names: list[str]) -> Dict[str, Any]:
    # 1) indexed from topics (all three are addresses for ERC20DepositInitiated)
    out: Dict[str, Any] = {}
    topics = [t.hex() if hasattr(t, "hex") else t for t in log["topics"]]
    for i, name in enumerate(indexed_names, start=1):
        if i >= len(topics):
            raise ValueError(f"missing topic {i} for indexed field {name}")
        out[name] = _addr_from_topic(topics[i])

    # 2) data section (try ABI first, then manual fallback)
    try:
        dec = _decode_erc20_deposit_try_abi(data_names, log["data"])
    except Exception:
        dec = _decode_erc20_deposit_fallback(data_names, log["data"])
    out.update(dec)

    # normalize address shapes
    for k in ("l1Token","l2Token","from","to"):
        if k in out and isinstance(out[k], str) and out[k].startswith("0x"):
            out[k] = to_checksum_address(out[k])
    return out


def _message_id(components: list[str], decoded: Dict[str, Any]) -> str:
    material = {k: decoded.get(k) for k in components}
    return stable_hash(material)

def fetch_bridge_src_events(w3: Web3, adapter: BridgeAdapter) -> list[IntentEvent]:
    from_b = _resolve_block(w3, adapter.from_block)
    to_b   = _resolve_block(w3, adapter.to_block)
    logs = w3.eth.get_logs({
        "address": Web3.to_checksum_address(adapter.src_address),
        "fromBlock": from_b,
        "toBlock": to_b,
        "topics": [adapter.topic0]
    })

    indexed = adapter.fields.get("indexed", ["l1Token","l2Token","from"])
    data    = adapter.fields.get("data",    ["to","amount","extraData"])

    evs: list[IntentEvent] = []
    ok, fail = 0, 0

    for lg in logs:
        try:
            decoded = _decode_event_data(adapter.event_signature, lg, indexed, data)
            mid = _message_id(adapter.fields["message_id_components"], decoded)
            token = decoded.get(adapter.fields["token"])
            amt_raw = decoded.get(adapter.fields["amount"])
            try:
                amt = float(amt_raw)
            except Exception:
                amt = float(int(str(amt_raw), 0)) if isinstance(amt_raw, str) and str(amt_raw).startswith("0x") else float(amt_raw)

            evs.append(IntentEvent(
                eid = lg["transactionHash"].hex() + ":" + str(lg["logIndex"]),
                chain = adapter.src_chain,
                kind = "bridge_out",
                token = token,
                amount = amt,
                meta = {
                    "messageId": mid,
                    "adapter": adapter.name,
                    "from": decoded.get("from"),
                    "to": decoded.get("to")
                }
            ))
            ok += 1
        except Exception:
            fail += 1
            continue

    if evs:
        evs[0].meta["decode_stats"] = {"decoded": ok, "skipped": fail, "total_logs": len(logs)}
    return evs