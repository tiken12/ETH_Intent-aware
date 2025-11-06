#!/usr/bin/env python3
import argparse
from web3 import Web3
from eth_abi import abi

def main():
    p = argparse.ArgumentParser()
    p.add_argument("--factory", required=True, help="Factory contract address (0x...)")
    p.add_argument("--func", required=True, help='Function signature, e.g. "createAccount(address,uint256)"')
    p.add_argument("--arg", action="append", default=[], help="Function argument (repeat for each)")
    args = p.parse_args()

    factory = Web3.to_checksum_address(args.factory)

    sig = args.func.strip()
    if "(" not in sig or not sig.endswith(")"):
        raise SystemExit("Invalid --func; expected e.g. createAccount(address,uint256)")
    name, types_str = sig.split("(", 1)
    types_str = types_str[:-1]
    types = [t.strip() for t in types_str.split(",")] if types_str else []

    if len(types) != len(args.arg):
        raise SystemExit(f"Got {len(args.arg)} --arg values for {len(types)} types in --func")

    coerced = []
    for t, v in zip(types, args.arg):
        if t.startswith(("uint","int")):
            coerced.append(int(v, 16) if isinstance(v, str) and v.startswith(("0x","0X")) else int(v))
        elif t == "address":
            coerced.append(Web3.to_checksum_address(v))
        elif t == "bytes32":
            vv = v[2:] if v.startswith("0x") else v
            if len(vv) != 64: raise SystemExit("bytes32 must be 32 bytes (64 hex chars)")
            coerced.append(bytes.fromhex(vv))
        elif t == "bytes":
            vv = v[2:] if v.startswith("0x") else v
            coerced.append(bytes.fromhex(vv))
        else:
            coerced.append(v)

    selector = Web3.keccak(text=f"{name}({','.join(types)})")[:4]
    encoded_args = abi.encode(types, coerced)
    calldata = b"".join([selector, encoded_args])

    init_code = factory + calldata.hex()
    print("factory_address:", factory)
    print("function:", f"{name}({','.join(types)})")
    print("calldata:", "0x" + calldata.hex())
    print("initCode:", "0x" + init_code)

if __name__ == "__main__":
    main()
