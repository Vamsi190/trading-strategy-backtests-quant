# SMA + Bollinger bands

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import backtrader as bt
import yfinance as yf

# Step 1: Get Apple stock prices from the internet
def get_stock_data():
    return yf.download('AAPL', start='2020-01-01', end='2023-12-31')

# Step 2: Calculate SMA and Bollinger Bands, and generate signals
def prepare_data(data):
    # Calculate SMA (Simple Moving Average)
    data[('SMA Short', '')] = data[('Close', 'AAPL')].rolling(window=50).mean()  # Short-term SMA
    data[('SMA Long', '')] = data[('Close', 'AAPL')].rolling(window=200).mean()   # Long-term SMA
    
    # Calculate Bollinger Bands
    data[('Middle Band', '')] = data[('Close', 'AAPL')].rolling(window=20).mean()
    data[('Std Dev', '')] = data[('Close', 'AAPL')].rolling(window=20).std()
    data[('Upper Band', '')] = data[('Middle Band', '')] + (2 * data[('Std Dev', '')])
    data[('Lower Band', '')] = data[('Middle Band', '')] - (2 * data[('Std Dev', '')])
    
    # Create signals
    data[('Buy Signal', '')] = np.where((data[('Close', 'AAPL')] < data[('Lower Band', '')]) & 
                                        (data[('SMA Short', '')] > data[('SMA Long', '')]), 1, 0)
    data[('Sell Signal', '')] = np.where((data[('Close', 'AAPL')] > data[('Upper Band', '')]) | 
                                        (data[('SMA Short', '')] < data[('SMA Long', '')]), -1, 0)
    
    # Drop any rows with NaN values after the rolling calculations
    data = data.dropna()
    return data

# Step 3: Draw the prices and signals with better spacing and visibility
def show_chart(data):
    plt.figure(figsize=(14, 7))  # Increase the figure size for better spacing
    
    # Plot the stock price
    plt.plot(data[('Close', 'AAPL')], label='Stock Price', color='black', linewidth=1.5)
    
    # Plot the Bollinger Bands
    plt.plot(data[('Middle Band', '')], label='Middle Band (20-Day SMA)', color='blue', linestyle='--', linewidth=1.5)
    plt.plot(data[('Upper Band', '')], label='Upper Band', color='red', linestyle='--', alpha=0.7, linewidth=1.5)
    plt.plot(data[('Lower Band', '')], label='Lower Band', color='green', linestyle='--', alpha=0.7, linewidth=1.5)

    # Plot the SMAs
    plt.plot(data[('SMA Short', '')], label='SMA Short (50-Day)', color='orange', linestyle='-', linewidth=1.5)
    plt.plot(data[('SMA Long', '')], label='SMA Long (200-Day)', color='purple', linestyle='-', linewidth=1.5)

    # Mark buy points with larger green upward triangles
    plt.scatter(data.index[data[('Buy Signal', '')] == 1], data[('Close', 'AAPL')][data[('Buy Signal', '')] == 1], 
                label='Buy Signal', marker='^', color='green', s=100, edgecolors='black', zorder=5)  
    
    # Mark sell points with larger red downward triangles
    plt.scatter(data.index[data[('Sell Signal', '')] == -1], data[('Close', 'AAPL')][data[('Sell Signal', '')] == -1], 
                label='Sell Signal', marker='v', color='red', s=100, edgecolors='black', zorder=5)
    
    plt.title('Combined Trading Strategy with SMA and Bollinger Bands', fontsize=16)  # Set the title
    plt.xlabel('Date', fontsize=12)  # X-axis label
    plt.ylabel('Price', fontsize=12)  # Y-axis label
    plt.legend(loc='upper left', fontsize=10)  # Show the legend with smaller font
    plt.grid(True)  # Add a grid for better visibility
    plt.tight_layout()  # Adjust spacing
    plt.show()  # Display the chart

# Step 4: Create the trading robot that uses the combined strategy
class CombinedTradingRobot(bt.Strategy):
    def __init__(self):
        self.sma_short = bt.indicators.SimpleMovingAverage(self.data.close, period=50)
        self.sma_long = bt.indicators.SimpleMovingAverage(self.data.close, period=200)
        self.bbands = bt.indicators.BollingerBands(self.data.close, period=20)

    def next(self):
        # Buy conditions
        if (self.data.close[0] < self.bbands.lines.bot[0] and 
            self.sma_short[0] > self.sma_long[0]) and not self.position:
            self.buy()
        # Sell conditions
        elif (self.data.close[0] > self.bbands.lines.top[0] or 
            self.sma_short[0] < self.sma_long[0]) and self.position:
            self.sell()

# Step 5: Run the backtesting
if __name__ == "__main__":
    stock_data = get_stock_data()  # Get stock prices
    stock_data = prepare_data(stock_data)  # Calculate signals
    show_chart(stock_data)  # Draw the chart

    cerebro = bt.Cerebro()  # Create a test environment
    cerebro.adddata(bt.feeds.PandasData(dataname=stock_data))  # Add stock data
    cerebro.addstrategy(CombinedTradingRobot)  # Add the combined strategy
    cerebro.broker.setcash(10000.0)  # Start with $10,000
    cerebro.run()  # Run the backtest
    cerebro.plot()  # Show results

