import numpy as np
import pandas as pd
from statsmodels.tsa.arima.model import ARIMA

def best_provider(amount):
    """
    Selects the best FX provider based on rate and fee.
    """
    providers = {
        "Provider A": {"rate": 0.0121, "fee": 0.015},
        "Provider B": {"rate": 0.0120, "fee": 0.005},
        "Provider C": {"rate": 0.0119, "fee": 0.000}
    }

    results = {}
    for name, data in providers.items():
        final_amount = (amount * data["rate"]) * (1 - data["fee"])
        results[name] = final_amount

    best = max(results, key=results.get)
    return best, results


def predict_next_rate(rates=None):
    """
    Predicts the next INR/USD rate using ARIMA.
    """
    if rates is None:
        np.random.seed(42)
        rates = [83]  # starting INR/USD rate
        for _ in range(200):
            change = np.random.normal(0, 0.05)
            rates.append(rates[-1] + change)

    df = pd.DataFrame({"rate": rates})
    model = ARIMA(df["rate"], order=(1, 1, 1))
    model_fit = model.fit()
    prediction = model_fit.forecast(steps=1)
    return float(prediction.iloc[0])


if __name__ == "__main__":
    amount_example = 100000  
    best, results = best_provider(amount_example)
    print("Conversion Results:", results)
    print("Best Provider:", best)

    predicted_rate = predict_next_rate()
    print("Predicted Next INR/USD Rate:", round(predicted_rate, 4))
