from fastapi import FastAPI
from pydantic import BaseModel
import random
import time

from routingagent import RoutingAgent
from complianceagent import Transaction, compliance_agent
from fraudagent import fraud_check
from fx_optimizer import best_provider
from fastapi.middleware.cors import CORSMiddleware





agent = RoutingAgent()
app = FastAPI(title="AI-Powered Payment Execution Layer")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # later restrict to frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def execute_bank_transfer(tx_dict, provider=None):
    time.sleep(1)
    return {
        "rail": "Bank",
        "status": "Success",
        "reference_Id": "BNK " + str(random.randint(10000, 99999)),
        "fx_provider": provider
    }

def execute_wallet_transfer(tx_dict, provider=None):
    time.sleep(1)
    return {
        "rail": "Wallet",
        "status": "Success",
        "reference_Id": "WLT " + str(random.randint(10000, 99999)),
        "fx_provider": provider
    }

def execute_card_transfer(tx_dict, provider=None):
    time.sleep(1)
    return {
        "rail": "Card",
        "status": "Success",
        "reference_Id": "CRD " + str(random.randint(10000, 99999)),
        "fx_provider": provider
    }

def execute_crypto_transfer(tx_dict, provider=None):
    time.sleep(1)
    return {
        "rail": "Crypto",
        "status": "Success",
        "reference_Id": "CTX " + str(random.randint(10000, 99999)),
        "fx_provider": provider
    }



def routing_agent(tx_dict):
    amount = tx_dict["amount"]
    risk_score = tx_dict.get("risk_score", 0)
    result = agent.select_best_route(amount, risk_score)
    return result.get("selected_route", None)


def execution_layer(tx: Transaction):
    
    compliance_result = compliance_agent(tx)
    tx_dict = tx.dict()
    tx_dict["risk_score"] = compliance_result.get("risk_score", 0)

    if compliance_result.get("status") == "BLOCKED":
        return {"status": "FAILED", "reason": "Blocked by Compliance", "compliance": compliance_result}

    
    fraud_result = fraud_check(
        user_id=tx.user_id,
        amount=tx.amount,
        country=tx.receiver_country,
        device_id=random.randint(1, 5),  
        hour=random.randint(0, 23)       
    )

    if fraud_result["status"] == "FLAGGED":
        return {"status": "FAILED", "reason": "Flagged by Fraud Detection", "fraud": fraud_result}

    
    routing_result = agent.select_best_route(tx.amount, tx_dict["risk_score"])

    if not routing_result["selected_route"]:
        return {
          "status": "FAILED",
          "reason": "No safe route due to high risk",
          "compliance": compliance_result
        }

    route = routing_result["selected_route"]


    
    fx_provider, fx_results = best_provider(tx.amount)

    
    if route in ["BANK", "SWIFT"]:
        execution_result = execute_bank_transfer(tx_dict, provider=fx_provider)
    elif route in ["WALLET", "Wallet Partner"]:
        execution_result = execute_wallet_transfer(tx_dict, provider=fx_provider)
    elif route in ["CARD", "Card Network"]:
        execution_result = execute_card_transfer(tx_dict, provider=fx_provider)
    elif route.upper() == "CRYPTO":
        execution_result = execute_crypto_transfer(tx_dict, provider=fx_provider)
    else:
        execution_result = {"status": "FAILED", "reason": "Unknown Rail"}

    
    return {
        "compliance": compliance_result,
        "fraud": fraud_result,
        "routing": routing_result,
        "fx": {"provider": fx_provider, "results": fx_results},
        "execution": execution_result
    }


@app.get("/health")
def health_check():
    return {"status": "OK", "message": "Payment System is running"}

@app.post("/send_payment")
def send_payment(tx: Transaction):
    return execution_layer(tx)
