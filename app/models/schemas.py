from pydantic import BaseModel, Field
from typing import List, Dict, Optional, Union

JSON = Dict[str, Union[str, int, float, bool, None, dict, list]]

class EIP712Domain(BaseModel):
    name: Optional[str] = None
    version: Optional[str] = None
    chainId: int
    verifyingContract: Optional[str] = None

class EIP712TypedData(BaseModel):
    types: Dict[str, List[Dict[str, str]]]
    primaryType: str
    domain: EIP712Domain
    message: Dict[str, Union[str, int]]

class UserOperation(BaseModel):
    sender: str
    nonce: str
    initCode: str
    callData: str
    callGasLimit: str
    verificationGasLimit: str
    preVerificationGas: str
    maxFeePerGas: str
    maxPriorityFeePerGas: str
    paymasterAndData: str
    signature: Optional[str] = None

class SimCallNode(BaseModel):
    target: str
    selector: str
    children: List["SimCallNode"] = []

SimCallNode.model_rebuild()

class Verdict(BaseModel):
    decision: str            # ALLOW | WARN | BLOCK
    rationale: List[str]
    attestation: Dict[str, str]
