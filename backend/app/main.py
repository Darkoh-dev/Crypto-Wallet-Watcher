import json
import re
from pathlib import Path
from datetime import datetime, timezone

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel


app = FastAPI(title="Crypto Wallet Watcher API")

WALLETS_FILE = Path("backend/data/wallets.json")



class WalletCreate(BaseModel):
    address: str
    chain: str
    label: str
    label: str
    notes: str = ""



def load_wallets() -> list[dict]:
    if not WALLETS_FILE.exists():
        return []
    
    with WALLETS_FILE.open("r") as file:
        return json.load(file)
    

def save_wallets(wallets: list[dict]) -> None:
    with WALLETS_FILE.open("w") as file:
        json.dump(wallets, file, indent=2)


def get_next_wallet_id(wallets: list[dict]) -> int:
    if not wallets:
        return 1
    
    return max(wallet["id"] for wallet in wallets) + 1


def is_vaild_ethereum_address(address: str) -> bool:
    pattern = r"^0x[a-fA-F0-9]{40}$"
    return bool(re.match(pattern, address))


@app.get("/")
def read_root():
    return {"message": "Crypto Wallet Watcher API is running"}

@app.get("/wallets")
def get_wallets():
    return load_wallets()

@app.post("/wallets")
def add_wallet(wallet: WalletCreate):
    if wallet.chain.lower() != "ethereum":
        raise HTTPException(
            status_code=400,
            detail="Only ethereum wallets are supported."
        )
    
    if not is_vaild_ethereum_address(wallet.address):
        raise HTTPException(
            status_code=400,
            detail="Invaild ethereum wallet address.",
        )
    
    wallets = load_wallets()
    normalized_address = wallet.address.lower()
    normalized_chain = wallet.chain.lower()

    for existing_wallet in wallets:
        same_address = existing_wallet["address"].lower() == normalized_address
        same_chain = existing_wallet["chain"].lower() == normalized_chain

        if same_address and same_chain:
            raise HTTPException(
                status_code=409,
                detail="This wallet is already being watched.",
            )

    new_wallet = {
        "id": get_next_wallet_id(wallets),
        "address": normalized_address,
        "chain": normalized_chain,
        "label": wallet.label,
        "notes": wallet.notes,
        "created_at": datetime.now(timezone.utc).isoformat(),
    }

    wallets.append(new_wallet)
    save_wallets(wallets)

    return new_wallet