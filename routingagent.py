class RoutingAgent:
    def __init__(self):
        self.routes = [
            {
               "name": "SWIFT", #bank network
               "fee_percentage": 3,
               "time_hours": 24,
               "fx_spread": 1.5,
               "max_risk_allowed": 100
            },

            {
                 "name": "Wallet Partner", #online like paypal , upi
                 "fee_percentage": 1.5,
                 "time_hours":6,
                 "fx_spread": 0.8,
                 "max_risk_allowed": 70 
            },

            {
                "name": "Card Network", #visa, mastercard
                "fee_percentage": 2,
                "time_hours": 2,
                "fx_spread": 1.2,
                "max_risk_allowed": 80
            },
            
            {
                "name": "Crypto",  #Cryptocurrency
                "fee_percentage": 0.5,  
                "time_hours": 0.5,      
                "fx_spread": 0.5,
                "max_risk_allowed": 60   
            }
        ]
    
    def select_best_route(self, amount, risk_score):
        best_route = None;
        lowest_score = float('inf')
        for route in self.routes:
            if risk_score > route["max_risk_allowed"]:
                continue
            fee= amount * (route["fee_percentage"]/100)
            fx_loss = amount * (route["fx_spread"]/100)
            risk_penalty = risk_score*2
            time_penalty = route["time_hours"]*5
            total_score = fee + fx_loss + risk_penalty + time_penalty
            if total_score < lowest_score:
                lowest_score = total_score
                best_route = route
        if best_route is None:
            return {
                "selected_route": None,
                "reason": "No route available due to high risk."
            }
        return {
            "selected_route": best_route["name"],
            "estimated_time": best_route["time_hours"],
            "routing score": round(lowest_score, 2),
            "reason": "Selected route based on lowest combined cost, risk, and time."
        }
if __name__ == "__main__":
    agent = RoutingAgent()

    result = agent.select_best_route(amount=10000,risk_score=50)

    print(result) 