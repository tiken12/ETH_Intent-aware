from web3 import Web3
from app.core.config import rpc_for_chain, DEFAULT_BLOCK_TAG
from typing import Any, Dict, Optional

def get_w3(chain_id: int) -> Web3:
    url = rpc_for_chain(chain_id)
    if not url:
        raise RuntimeError(f"No RPC configured for chain {chain_id}")
    return Web3(Web3.HTTPProvider(url, request_kwargs={"timeout": 20}))

def eth_call(chain_id: int, tx: Dict[str, Any], block_tag: str | int = DEFAULT_BLOCK_TAG) -> str:
    w3 = get_w3(chain_id)
    return w3.eth.call(tx, block_identifier=block_tag).hex()

def create_access_list(chain_id: int, tx: Dict[str, Any], block_tag: str | int = DEFAULT_BLOCK_TAG):
    w3 = get_w3(chain_id)
    try:
        return w3.provider.make_request("eth_createAccessList", [tx, block_tag])
    except Exception as e:
        return {"error": str(e)}

def trace_call(chain_id: int, tx: Dict[str, Any], block_tag: str | int = DEFAULT_BLOCK_TAG):
    # requires trace_call support; not all nodes enable
    w3 = get_w3(chain_id)
    try:
        return w3.provider.make_request("trace_call", [tx, ["trace"], block_tag])
    except Exception as e:
        return {"error": str(e)}
