import os, yaml
from dataclasses import dataclass
from dotenv import load_dotenv

load_dotenv()

def _load_yaml(path: str):
    with open(path, "r") as f:
        return yaml.safe_load(f)

CFG = _load_yaml(os.getenv("INTENT_GUARD_CONFIG", "config.yaml"))

def rpc_for_chain(chain_id: int) -> str | None:
    m = {
        1: os.getenv("RPC_MAINNET"),
        10: os.getenv("RPC_OPTIMISM"),
        42161: os.getenv("RPC_ARBITRUM"),
        8453: os.getenv("RPC_BASE"),
    }
    return m.get(chain_id)

BUNDLER_RPC = os.getenv("BUNDLER_RPC")
DEFAULT_BLOCK_TAG = CFG["global"].get("default_block_tag", "latest")
PROFILE = CFG["global"].get("decision_profile", "conservative")
POLICY = CFG["policies"]
XCHAIN = CFG["crosschain"]
