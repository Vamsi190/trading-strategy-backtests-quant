import pandas as pd  
import numpy as np  
import matplotlib.pyplot as plt  
import backtrader as bt  
import yfinance as yf  

def get_stock_data():
    return yf.download('AMD', start='2021-11-01', end='2022-12-31')

#  Calculate Bollinger Bands 
def prepare_data(data):
    data[('Middle Band', '')] = data[('Close', 'AMD')].rolling(window=20).mean() # Middle Band is the average price over 20 days
    data[('Std Dev', '')] = data[('Close', 'AMD')].rolling(window=20).std()  # Standard deviation helps measure how spread out prices are
    data[('Upper Band', '')] = data[('Middle Band', '')] + (2 * data[('Std Dev', '')]) # Upper Band is the Middle Band plus two times the standard deviation
    data[('Lower Band', '')] = data[('Middle Band', '')] - (2 * data[('Std Dev', '')]) # Lower Band is the Middle Band minus two times the standard deviation
    

    data[('Buy Signal', '')] = np.where(data[('Close', 'AMD')] < data[('Lower Band', '')], 1, 0)  # If the price goes below the lower band, it tells us to "buy"
    data[('Sell Signal', '')] = np.where(data[('Close', 'AMD')] > data[('Upper Band', '')], -1, 0)  # If the price goes above the upper band, it tells us to "sell"
    
    data = data.dropna(subset=[('Middle Band', ''), ('Upper Band', ''), ('Lower Band', '')])  # Remove any missing data to keep things clean
    return data

# stock price with buy and sell signals
def show_chart(data):
    plt.figure(figsize=(14, 7))
    
    plt.plot(data[('Close', 'AMD')], label='Stock Price', color='black', linewidth=1.5)  # stock price (black line)
    plt.plot(data[('Middle Band', '')], label='Middle Band (20-Day Average)', color='blue', linestyle='--', linewidth=1.5) # middle line of Bollinger Bands (blue dashed line)
    plt.plot(data[('Upper Band', '')], label='Upper Band', color='red', linestyle='--', alpha=0.7, linewidth=1.5) #upper band (red dashed line)
    plt.plot(data[('Lower Band', '')], label='Lower Band', color='green', linestyle='--', alpha=0.7, linewidth=1.5)  #the lower band (green dashed line)
    
    # Mark the "buy" spots with green arrows
    plt.scatter(data.index[data[('Buy Signal', '')] == 1], data[('Close', 'AMD')][data[('Buy Signal', '')] == 1],
                label='Buy Signal', marker='^', color='green', s=100, edgecolors='black')
    
    # Mark the "sell" spots with red arrows
    plt.scatter(data.index[data[('Sell Signal', '')] == -1], data[('Close', 'AMD')][data[('Sell Signal', '')] == -1],
                label='Sell Signal', marker='v', color='red', s=100, edgecolors='black')
    
    # title and labels
    plt.title('AMD Stock entry and exit with Bollinger Bands', fontsize=16)
    plt.xlabel('Date', fontsize=12)
    plt.ylabel('Price', fontsize=12)
    plt.legend(loc='upper left', fontsize=10)
    plt.grid(True)
    plt.tight_layout()  # Adjust the space 
    plt.show()  # Show the picture

# Automate
class TradingRobot(bt.Strategy):
    def __init__(self):
        self.bbands = bt.indicators.BollingerBands(self.data.close, period=20) # Use Bollinger Bands to decide when to buy or sell

    def next(self):
        if self.data.close[0] < self.bbands.bot[0] and not self.position:    # If the price goes below the lower band, buy some stock
            self.buy()
        elif self.data.close[0] > self.bbands.top[0] and self.position:       # If the price goes above the upper band, sell the stock
            self.sell()

# Step 5: Put everything together
if __name__ == "__main__":
    # Get the stock prices for Apple
    stock_data = get_stock_data()
    
    # Calculate the Bollinger Bands and find when to buy or sell
    stock_data = prepare_data(stock_data)
    
    # Draw the chart with buy and sell signals
    show_chart(stock_data)
    
    # Test our trading robot
    cerebro = bt.Cerebro()  # Create a place to run our tests
    cerebro.adddata(bt.feeds.PandasData(dataname=stock_data))  # Add the stock data
    cerebro.addstrategy(TradingRobot)  # Add the trading robot to the test
    cerebro.broker.setcash(10000.0)  # Start with $10,000
    cerebro.run()  # Run the test
    cerebro.plot()  # Show the results
