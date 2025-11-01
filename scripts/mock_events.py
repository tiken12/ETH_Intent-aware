import requests

events = [
  {"eid":"e1","chain":1,"kind":"bridge_out","token":"USDC","amount":1000.0,"meta":{"messageId":"m1"}},
  {"eid":"e2","chain":10,"kind":"bridge_in","token":"USDC","amount":999.0,"meta":{"messageId":"m1"}}
]
r = requests.post("http://127.0.0.1:8000/v1/validate/crosschain", json=events)
print(r.status_code, r.json())
