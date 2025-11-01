from app.models.schemas import SimCallNode, UserOperation
from app.core.config import BUNDLER_RPC
import requests

def simulate_validation(userop: UserOperation) -> SimCallNode:
    """
    Adapter to a bundler/EntryPoint simulateValidation.
    MVP: return a tiny fabricated call-tree (replace with real call-tree parsing).
    """
    # If you have a bundler RPC, call it here. Else stub a tree:
    return SimCallNode(
        target=userop.sender,
        selector="0x",
        children=[
            SimCallNode(target="0xFactory", selector="create()", children=[
                # Use "delegatecall" to test policy blocking
                SimCallNode(target="0xTarget", selector="delegatecall", children=[])
            ])
        ]
    )
