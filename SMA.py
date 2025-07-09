#MOVING AVERAGES 

import pandas as pd  
import numpy as np  
import matplotlib.pyplot as plt  
import backtrader as bt  
import yfinance as yf  

def get_stock_data():
    return yf.download('AAPL', start='2020-01-01', end='2023-12-31')

# Calculate averages and decide when to buy or sell
def prepare_data(data):

    data['Short Average'] = data['Close'].rolling(window=50).mean()     # Calculate a short average (50 days)
    data['Long Average'] = data['Close'].rolling(window=200).mean()     # Calculate a long average (200 days)
    data['Signal'] = np.where(data['Short Average'] > data['Long Average'], 1, 0)  # Create a signal to buy (1) or do nothing (0)
    data['Position'] = data['Signal'].diff()   # Find out when to buy or sell
    return data

# Draw the prices and our signals
def show_chart(data):
    plt.figure(figsize=(10, 5))  # Create a big picture
    plt.plot(data['Close'], label='Stock Price')  # Draw the stock prices

    plt.plot(data['Short Average'], label='50-Day Average')  # Draw the short average
    plt.plot(data['Long Average'], label='200-Day Average')  # Draw the long average

    plt.scatter(data.index[data['Position'] == 1], data['Close'][data['Position'] == 1], 
                label='Buy', marker='^', color='green')  # Mark buy points
    plt.scatter(data.index[data['Position'] == -1], data['Close'][data['Position'] == -1], 
                label='Sell', marker='v', color='red')  # Mark sell points
                
    plt.title('Apple Stock Trade with SMA')  # Title of the chart
    plt.grid(True)
    plt.tight_layout()
    plt.legend()  # Show labels
    plt.show()  # Show the picture

# Automate
class TradingRobot(bt.Strategy):
    def __init__(self):
        # Set up the short and long averages
        self.short_average = bt.indicators.SimpleMovingAverage(self.data.close, period=50)
        self.long_average = bt.indicators.SimpleMovingAverage(self.data.close, period=200)

    def next(self):
        # If short average is above long average, buy
        if self.short_average[0] > self.long_average[0] and not self.position:
            self.buy()
        # If short average is below long average, sell
        elif self.short_average[0] < self.long_average[0] and self.position:
            self.sell()

# Step 5: Put everything together
if __name__ == "__main__":
    stock_data = get_stock_data()  # Get the stock prices
    stock_data = prepare_data(stock_data)  # Calculate averages and signals
    show_chart(stock_data)  # Draw the chart

    # Start testing our trading robot
    cerebro = bt.Cerebro()  # Create a place to run our tests
    cerebro.adddata(bt.feeds.PandasData(dataname=stock_data))  # Add our stock data
    cerebro.addstrategy(TradingRobot)  # Add our trading robot
    cerebro.broker.setcash(10000.0)  # Start with $10,000
    cerebro.run()  # Run the test
    cerebro.plot()  # Show the results






