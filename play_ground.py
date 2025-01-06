import pandas as pd
import numpy as np

# Load data
data = pd.read_csv("app/data/stock_data/3406.csv")
per_values = data["PER"].dropna().values  # Array of PER values
prices = data["Price"].dropna().values    # Array of Prices

# Calculate metrics
median_per = np.median(per_values)
gep25 = np.percentile(per_values, 25)

print(f"Median PER: {median_per:.2f}")
print(f"25th Percentile PER: {gep25:.2f}")

# Initialize counters
triggers = 0
successful_reversions = 0
returns = []
drawdowns = []

# Loop through PER values
lookback_period = 20  # e.g., 1 month = 20 trading days
for i in range(len(per_values) - lookback_period):
    if per_values[i] < gep25:  # Trigger condition
        triggers += 1
        initial_deviation = abs(per_values[i] - median_per)

        # Check for reversion
        for j in range(1, lookback_period + 1):
            future_per = per_values[i + j]
            future_deviation = abs(future_per - median_per)

            if future_deviation < initial_deviation:  # Reversion detected
                successful_reversions += 1

                # Calculate return and drawdown
                entry_price = prices[i]
                exit_price = prices[i + j]
                returns.append((exit_price / entry_price) - 1)

                max_price_during = max(prices[i:i + j + 1])
                drawdowns.append((entry_price - max_price_during) / entry_price)

                break  # Exit inner loop after success

# Calculate win rate and averages
win_rate = (successful_reversions / triggers) * 100 if triggers > 0 else 0
average_return = np.mean(returns) if returns else 0
average_drawdown = np.mean(drawdowns) if drawdowns else 0

print(f"Win Rate: {win_rate:.2f}%")
print(f"Average Return: {average_return:.2%}")
print(f"Average Drawdown: {average_drawdown:.2%}")
