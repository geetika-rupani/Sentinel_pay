from pydantic import BaseModel
import numpy as np
from sklearn.linear_model import LogisticRegression

class Transaction(BaseModel):
    user_id: str
    name: str
    dob: str
    email_or_phone: str
    id_proof: bool        
    address_proof: bool   
    verified: bool        
    sender_country: str
    receiver_country: str
    amount: float
    transactions_last_24h: int


country_risk_table = {
    "India": "low",
    "USA": "Low",
    "Singapore": "Low",
    "UAE": "Medium",
    "Nigeria": "High",
    "North Korea": "Sanctioned"
}


X = np.array([
    [5000,1,0,0],
    [20000,0,1,1],
    [800,1,0,0],
    [15000,0,1,0],
    [30000,0,1,1],
    [12000,0,1,1],
    [7000,1,1,0],
])
Y = np.array([0,1,0,1,1,1,0])

model = LogisticRegression()
model.fit(X,Y)


def determine_kyc_level(tx: Transaction):
    if tx.id_proof and tx.address_proof and tx.verified:
        return "Full"
    elif tx.id_proof:
        return "Medium"
    else:
        return "Basic"


def rule_based_check(tx: Transaction):
    kyc_level = determine_kyc_level(tx)
    receiver_risk = country_risk_table.get(tx.receiver_country, "Medium")
    
    if receiver_risk == "Sanctioned":
        return "BLOCKED", "Receiver country is sanctioned"
    
    if kyc_level == "Basic" and tx.amount > 10000:
        return "REVIEW", "High amount with basic KYC"
    
    if receiver_risk == "High" and tx.amount > 5000:
        return "REVIEW", "Transfer to high risk country"
    
    return "PASS", "No Rule Violation"



def ai_risk_score(tx: Transaction):
    kyc_level = determine_kyc_level(tx)
    receiver_risk = country_risk_table.get(tx.receiver_country, "Medium")

    features = [[
        tx.amount,
        1 if kyc_level == "Full" else 0,
        1 if receiver_risk == "High" else 0,
        1 if tx.transactions_last_24h > 5 else 0
    ]]

    risk_prob = float(model.predict_proba(features)[0][1])
    return risk_prob


def compliance_agent(tx: Transaction):
    rule_status, rule_reason = rule_based_check(tx)

    if rule_status == "BLOCKED":
        return {
            "status": "BLOCKED",
            "risk_score": 1.0,
            "kyc_level": determine_kyc_level(tx),
            "reason": rule_reason
        }

    risk = ai_risk_score(tx)

    if risk > 0.75:
        return {
            "status": "REVIEW",
            "risk_score": round(risk,2),
            "kyc_level": determine_kyc_level(tx),
            "reason": "AI detected high AML risk"
        }

    return {
        "status": "APPROVED",
        "risk_score": round(risk,2),
        "kyc_level": determine_kyc_level(tx),
        "reason": "Transaction is compliant"
    }
