from app.correlate.dag import IntentDAG, IntentEvent
from app.policies.crosschain import conservation_check

def test_conservation_warn():
    dag = IntentDAG()
    a = IntentEvent("a", 1, "bridge_out", "USDC", 1000.0, {"messageId":"m1"})
    b = IntentEvent("b", 10, "bridge_in",  "USDC",  999.0, {"messageId":"m1"})
    dag.add(a); dag.add(b); dag.link("a","b",1.0)
    issues = conservation_check(dag, "a")
    assert any(i.code=="XCC-CONS" for i in issues)
