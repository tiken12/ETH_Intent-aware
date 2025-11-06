# scripts/detect_smart_account.py
from web3 import Web3
import os, sys, json

RPC = os.getenv("RPC_MAINNET") or os.getenv("RPC_BASE") or os.getenv("RPC_OPTIMISM")
if not RPC:
    print("Set RPC_MAINNET (or RPC_BASE/OPTIMISM) in .env")
    sys.exit(1)

if len(sys.argv) < 2:
    print("Usage: python scripts/detect_smart_account.py 0xYourAccount")
    sys.exit(1)

acct = Web3.to_checksum_address(sys.argv[1])
w3 = Web3(Web3.HTTPProvider(RPC))

# 1) Is it deployed?
code = w3.eth.get_code(acct).hex()
if code == "0x":
    print("Result: This address has NO code (not deployed). If it's your counterfactual, you'll need initCode.")
    sys.exit(0)
print(f"Bytecode length: {len(code)//2} bytes")

# 2) Try SimpleAccount/Kernel-like ABIs (entryPoint(), owner())
sa_abi = [
    {"type":"function","name":"entryPoint","stateMutability":"view","inputs":[],"outputs":[{"name":"","type":"address"}]},
    {"type":"function","name":"owner","stateMutability":"view","inputs":[],"outputs":[{"name":"","type":"address"}]},
]
sa = w3.eth.contract(address=acct, abi=sa_abi)
is_sa = False
try:
    ep = sa.functions.entryPoint().call()
    is_sa = True
    print(f"entryPoint(): {ep}")
except Exception:
    pass
if is_sa:
    try:
        ow = sa.functions.owner().call()
        print(f"owner(): {ow}")
    except Exception:
        pass
    print("Likely stack: SimpleAccount/Kernel-style (4337). Use the EntryPoint returned above (v0.6 or v0.7).")
    sys.exit(0)

# 3) Try Safe (Gnosis Safe) ABI fragment: getOwners()
safe_abi = [
    {"type":"function","name":"getOwners","stateMutability":"view","inputs":[],"outputs":[{"name":"","type":"address[]"}]}
]
safe = w3.eth.contract(address=acct, abi=safe_abi)
try:
    owners = safe.functions.getOwners().call()
    print(f"getOwners(): {owners}")
    print("Likely stack: Safe + AA module (check your wallet/provider docs for its EntryPoint version).")
    sys.exit(0)
except Exception:
    pass

# 4) Check if it’s a proxy (EIP-1967) and point to implementation for clues
slot = Web3.to_hex(int("0x360894A13BA1A3210667C828492DB98DCA3E2076CC3735A920A3CA505D382BBC",16))
try:
    impl_raw = w3.eth.get_storage_at(acct, slot)
    if impl_raw and impl_raw != b"\x00"*32:
        impl_addr = Web3.to_checksum_address("0x"+impl_raw[-20:].hex())
        print(f"EIP-1967 implementation at: {impl_addr} (inspect this contract in a block explorer for its name)")
except Exception:
    pass

print("Could not positively identify. It may be another AA implementation. If you know the factory, that determines the stack.")
