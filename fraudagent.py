
import pandas as pd
import numpy as np
from sklearn.ensemble import IsolationForest

np.random.seed(42)



num_transactions = 500

data = pd.DataFrame({
    "user_id": np.random.randint(1, 21, num_transactions),
    "amount": np.random.normal(5000, 1000, num_transactions),
    "country": np.random.choice(["IN", "US", "UK"], num_transactions),
    "device_id": np.random.randint(1, 5, num_transactions),
    "hour": np.random.randint(0, 24, num_transactions)
})


for i in range(10):
    data.loc[i, "amount"] = np.random.randint(20000, 40000)
    data.loc[i, "country"] = "NG"
    data.loc[i, "device_id"] = 99
    data.loc[i, "hour"] = 2



def create_features(df):
    user_avg = df.groupby("user_id")["amount"].transform("mean")
    df["amount_ratio"] = df["amount"] / user_avg
    df["new_country"] = df["country"].apply(lambda x: 1 if x == "NG" else 0)
    df["new_device"] = df["device_id"].apply(lambda x: 1 if x == 99 else 0)
    df["odd_hour"] = df["hour"].apply(lambda x: 1 if x in [1,2,3,4] else 0)
    return df[["amount_ratio", "new_country", "new_device", "odd_hour"]]


features = create_features(data.copy())



model = IsolationForest(contamination=0.05, random_state=42)
model.fit(features)



def fraud_check(user_id, amount, country, device_id, hour):
   
    new_txn = pd.DataFrame({
        "user_id": [user_id],
        "amount": [amount],
        "country": [country],
        "device_id": [device_id],
        "hour": [hour]
    })

   
    combined = pd.concat([data, new_txn], ignore_index=True)
    features_new = create_features(combined.copy())

    new_features = features_new.tail(1)
    prediction = model.predict(new_features)[0]

    fraud_score = 0.9 if prediction == -1 else 0.1
    status = "FLAGGED" if fraud_score > 0.7 else "APPROVED"

    return {
        "fraud_score": fraud_score,
        "status": status
    }


if __name__ == "__main__":
    print("Model Trained Successfully")

    result = fraud_check(
        user_id=1,
        amount=30000,
        country="NG",
        device_id=99,
        hour=2
    )
    print("Fraud Check Result:")
    print(result)
