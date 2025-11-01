import sys, json, requests
data = json.load(sys.stdin)
r = requests.post("http://127.0.0.1:8000/v1/validate/eip712", json=data)
print(r.status_code, r.json())
