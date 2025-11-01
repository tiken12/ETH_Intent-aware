from app.models.schemas import EIP712TypedData, EIP712Domain
from app.policies.eip712 import lint_eip712

def test_allowance_block():
    td = EIP712TypedData(
        types={"Permit":[{"name":"spender","type":"address"},{"name":"value","type":"uint256"}]},
        primaryType="Permit",
        domain=EIP712Domain(chainId=1, verifyingContract="0xabc"),
        message={"spender":"0xdead","value":10**30}
    )
    issues = lint_eip712(td)
    assert any(i.code=="P712-ALLOW" and i.sev=="error" for i in issues)
