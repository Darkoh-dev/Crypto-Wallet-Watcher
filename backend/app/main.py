import json
import re
from pathlib import Path
from datetime import datetime, timezone

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel


app = FastAPI(title="Crypto Wallet Watcher API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

WALLETS_FILE = Path("backend/data/wallets.json")



class WalletCreate(BaseModel):
    address: str
    chain: str
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


SUPPORTED_CHAINS = {"bitcoin", "ethereum", "litecoin", "dogecoin"}


def is_valid_wallet_address(chain: str, address: str) -> bool:
    if chain == "ethereum":
        pattern = r"^0x[a-fA-F0-9]{40}$"
        return bool(re.match(pattern, address))
    
    if chain == "bitcoin":
        pattern = r"^(bc1|[13])[a-zA-HJ-NP-Z0-9]{25,62}$"
        return bool(re.match(pattern, address))
    
    if chain == "litecoin":
        pattern = r"^(ltc1|[LM3])[a-zA-HJ-NP-Z0-9]{25,62}$"
        return bool(re.match(pattern, address))
    
    if chain == "dogecoin":
        pattern = r"^D[a-zA-HJ-NP-Z0-9]{25,34}$"
        return bool(re.match(pattern, address))
    
    return False


@app.get("/")
def read_root():
    return {"message": "Crypto Wallet Watcher API is running"}

@app.get("/wallets")
def get_wallets():
    return load_wallets()

@app.post("/wallets")
def add_wallet(wallet: WalletCreate):
    normalized_chain = wallet.chain.lower()

    if normalized_chain not in SUPPORTED_CHAINS:
        raise HTTPException(
            status_code=400,
            detail="Supported chains are bitcoin, ethereum, litecoin, and dogecoin."
        )
    
    if not is_valid_wallet_address(normalized_chain, wallet.address):
        raise HTTPException(
            status_code=400,
            detail=f"Invalid {normalized_chain} wallet address.",
        )
    
    wallets = load_wallets()
    normalized_address = wallet.address.lower()

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