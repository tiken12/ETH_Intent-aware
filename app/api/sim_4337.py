from typing import Optional
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
import os, requests

router = APIRouter()
BUNDLER_RPC = os.getenv("BUNDLER_RPC", "").strip()
DEFAULT_EP = os.getenv("ENTRY_POINT", "").strip()

class UserOperation(BaseModel):
    sender: str
    nonce: str | int
    initCode: str
    callData: str
    callGasLimit: str | int | None = None
    verificationGasLimit: str | int | None = None
    preVerificationGas: str | int | None = None
    maxFeePerGas: str | int | None = None
    maxPriorityFeePerGas: str | int | None = None
    paymasterAndData: str
    signature: str | None = None

class SimRequest(BaseModel):
    userop: UserOperation
    entryPoint: Optional[str] = None  # allow override

def bundler_rpc(method: str, params: list):
    r = requests.post(BUNDLER_RPC, json={"jsonrpc":"2.0","id":1,"method":method,"params":params}, timeout=20)
    j = r.json()
    if "error" in j: raise HTTPException(status_code=400, detail=j["error"])
    return j["result"]

@router.post("/v1/simulate/4337")
def simulate_userop(req: SimRequest):
    ep = req.entryPoint or DEFAULT_EP
    return {
        "validation_ok": True,
        "gas": bundler_rpc("eth_estimateUserOperationGas", [req.userop.dict(exclude_none=True), ep, "latest"]),
        "entryPoint_used": ep
    }
