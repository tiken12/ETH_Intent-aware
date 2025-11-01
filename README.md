# Intent Guard — Cross-chain Correlation + Intent-Aware (EIP-712 / EIP-4337) Validation

## Quickstart
```bash
python -m venv .venv && source .venv/bin/activate    # (Windows: .venv\Scripts\activate)
pip install -r requirements.txt
cp .env.example .env
uvicorn main:app --reload
