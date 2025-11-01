from app.models.schemas import SimCallNode, UserOperation
from app.policies.eip4337 import lint_userop

def test_delegatecall_block():
    tree = SimCallNode(target="0xS", selector="0x", children=[
        SimCallNode(target="0xT", selector="delegatecall", children=[])
    ])
    op = UserOperation(sender="0xS",nonce="0x1",initCode="0x",callData="0x",callGasLimit="0x0",
        verificationGasLimit="0x0",preVerificationGas="0x0",maxFeePerGas="0x0",
        maxPriorityFeePerGas="0x0",paymasterAndData="0x")
    issues = lint_userop(tree, op)
    assert any(i.code=="AA-DEL" and i.sev=="error" for i in issues)
