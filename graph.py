import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd
import requests
import yfinance as yf


def fetch_crypto_data(symbol, days=30):
    coingecko_url = f"https://api.coingecko.com/api/v3/coins/{symbol}/market_chart"
    params = {
        'vs_currency': 'usd',
        'days': days,
        'interval': 'daily'
    }

    try:
        response = requests.get(coingecko_url, params=params)
        response.raise_for_status()
        crypto_data = response.json()
        return crypto_data['prices']
    except requests.exceptions.RequestException as e:
        print(f"Error fetching crypto data: {e}")
        return None

def visualize_crypto_prices(symbol, crypto_data, graph_type):
    if not crypto_data:
        print(f"Unable to visualize crypto prices for {symbol}.")
        return

    print(f"Graph type: {graph_type}")  # Debugging line

    # Convert crypto data to a DataFrame
    df = pd.DataFrame(crypto_data, columns=['timestamp', 'priceUSD'])
    df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')

    fig = make_subplots(rows=1, cols=1, subplot_titles=[f'{symbol} Prices Over Time'])

    if graph_type == 'line':
        # Line graph
        print("Using line graph")  # Debugging line
        fig.add_trace(go.Scatter(x=df['timestamp'], y=df['priceUSD'], mode='lines+markers', name='Price (USD)'), row=1, col=1)

    elif graph_type == 'bar':
        # Bar chart
        print("Using bar chart")  # Debugging line
        fig.add_trace(go.Bar(x=df['timestamp'], y=df['priceUSD'], name='Price (USD)'), row=1, col=1)

    else:
        print(f"Invalid graph type: {graph_type}. Defaulting to line graph.")
        fig.add_trace(go.Scatter(x=df['timestamp'], y=df['priceUSD'], mode='lines+markers', name='Price (USD)'), row=1, col=1)

    fig.update_xaxes(title_text='Date and Time', row=1, col=1)
    fig.update_yaxes(title_text='Price (USD)', row=1, col=1)
    fig.update_layout(title_text=f'{symbol} Prices Over Time', showlegend=True)
    fig.show()

def fetch_stock_data(ticker, days=30):
    try:
        stock_data = yf.download(ticker, period=f"{days}d")
        return stock_data['Close'].reset_index()
    except Exception as e:
        print(f"Error fetching stock data: {e}")
        return None

def visualize_stock_prices(ticker, stock_data, graph_type):
    if stock_data.empty:
        print(f"No stock data available for {ticker}.")
        return

    print(f"Graph type: {graph_type}")  # Debugging line

    # Convert stock data to a DataFrame
    df = stock_data

    fig = make_subplots(rows=1, cols=1, subplot_titles=[f'{ticker} Prices Over Time'])

    if graph_type == 'line':
        # Line graph
        print("Using line graph")  # Debugging line
        fig.add_trace(go.Scatter(x=df['Date'], y=df['Close'], mode='lines+markers', name='Closing Price (USD)'), row=1, col=1)

    elif graph_type == 'bar':
        # Bar chart
        print("Using bar chart")  # Debugging line
        fig.add_trace(go.Bar(x=df['Date'], y=df['Close'], name='Closing Price (USD)'), row=1, col=1)

    else:
        print(f"Invalid graph type: {graph_type}. Defaulting to line graph.")
        fig.add_trace(go.Scatter(x=df['Date'], y=df['Close'], mode='lines+markers', name='Closing Price (USD)'), row=1, col=1)

    fig.update_xaxes(title_text='Date', row=1, col=1)
    fig.update_yaxes(title_text='Closing Price (USD)', row=1, col=1)
    fig.update_layout(title_text=f'{ticker} Prices Over Time', showlegend=True)
    fig.show()
