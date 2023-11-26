from nonrelationaldb import Database
import datetime
import requests
import yfinance as yf

class Portfolio:
    def __init__(self):
        self.db = Database()

    def add_investment(self):
        investment_type = input("Enter the type of investment (crypto/stock): ").lower()

        if investment_type == "crypto":
            self.add_crypto_investment()
        elif investment_type == "stock":
            self.add_stock_investment()
        else:
            print("Invalid investment type. Please enter 'crypto' or 'stock'.")

    def add_crypto_investment(self):
        crypto_symbol = input("Enter the symbol of the cryptocurrency: ").lower()

        try:
            coingecko_url = f"https://api.coingecko.com/api/v3/coins/{crypto_symbol}"
            coingecko_response = requests.get(coingecko_url)
            coingecko_response.raise_for_status()
            coingecko_data = coingecko_response.json()

            crypto_name = coingecko_data.get("name", "Unknown")
            crypto_price_usd = coingecko_data.get("market_data", {}).get("current_price", {}).get("usd", 0)
            crypto_last_updated = coingecko_data.get("last_updated", "Unknown")

            try:
                crypto_last_updated_timestamp = int(crypto_last_updated)
            except ValueError:
                crypto_last_updated_timestamp = 0

            crypto_data = {
                "symbol": crypto_symbol,
                "name": crypto_name,
                "priceUSD": crypto_price_usd,
                "lastUpdated": datetime.datetime.utcfromtimestamp(crypto_last_updated_timestamp).strftime("%Y-%m-%dT%H:%M:%SZ"),
            }

            crypto_collection = self.db.database["cryptocurrency"]
            crypto_collection.insert_one(crypto_data)

            print(f"Successfully added cryptocurrency with symbol {crypto_symbol}.")

        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 404:
                print(f"Cryptocurrency with symbol '{crypto_symbol}' not found on CoinGecko.")
            else:
                print(f"Error connecting to CoinGecko API: {e}")

    def add_stock_investment(self):
        stock_ticker = input("Enter the ticker of the stock: ").upper()

        try:
            stock = yf.Ticker(stock_ticker)
            stock_info = stock.info

            stock_name = stock_info.get("longName", "Unknown")
            stock_price_usd = stock_info.get("regularMarketPrice", 0)
            stock_last_updated = datetime.datetime.utcfromtimestamp(stock_info.get("regularMarketTime", 0)).strftime("%Y-%m-%dT%H:%M:%SZ")
            stock_daily_volume = stock_info.get("regularMarketVolume", 0)
            stock_market_cap = stock_info.get("marketCap", 0)

            stock_data = {
                "ticker": stock_ticker,
                "name": stock_name,
                "priceUSD": stock_price_usd,
                "lastUpdated": stock_last_updated,
                "dailyVolume": stock_daily_volume,
                "marketCap": stock_market_cap
            }

            stock_collection = self.db.database["stocks"]
            stock_collection.insert_one(stock_data)

            print(f"Successfully added stock with ticker {stock_ticker}.")

        except Exception as e:
            print(f"Error adding stock data: {e}")

    def remove_investment(self):
        symbol = input("Enter the symbol or ticker of the investment to remove: ").lower()
        investment_type = input("Enter the type of investment (crypto/stock): ").lower()

        collection_name = "cryptocurrency" if investment_type == "crypto" else "stocks"
        investment_collection = self.db.database[collection_name]

        # Check if the investment exists before attempting to delete
        existing_investment = investment_collection.find_one({"symbol": symbol})

        if existing_investment:
            result = investment_collection.delete_one({
                "symbol": symbol,
                "lastUpdated": existing_investment.get("lastUpdated")
            })

            if result.deleted_count > 0:
                print(f"Successfully removed {investment_type} with symbol {symbol}.")
            else:
                print(f"Failed to remove {investment_type} with symbol {symbol}.")
        else:
            print(f"No {investment_type} found with symbol {symbol}.")

    def update_investment(self):
        symbol = input("Enter the symbol or ticker of the investment to update: ").upper()
        investment_type = input("Enter the type of investment (crypto/stock): ").lower()

        collection_name = "cryptocurrency" if investment_type == "crypto" else "stocks"
        investment_collection = self.db.database[collection_name]

        result = investment_collection.find_one({"symbol": symbol})

        if result:
            # Display current details
            print(f"Current details for {investment_type} with symbol {symbol}:")
            print(result)

            # Get updated details
            updated_price = float(input("Enter the updated price in USD: "))
            updated_last_updated = input("Enter the updated last updated timestamp (YYYY-MM-DDTHH:MM:SSZ): ")
            updated_daily_volume = float(input("Enter the updated daily trading volume: "))
            updated_market_cap = float(input("Enter the updated market capitalization: "))

            # Update the investment details
            result["priceUSD"] = updated_price
            result["lastUpdated"] = datetime.datetime.strptime(updated_last_updated, "%Y-%m-%dT%H:%M:%SZ")
            result["dailyVolume"] = updated_daily_volume
            result["marketCap"] = updated_market_cap

            # Update the document in the collection
            investment_collection.replace_one({"symbol": symbol}, result)

            print(f"Successfully updated {investment_type} with symbol {symbol}.")
        else:
            print(f"No {investment_type} found with symbol {symbol}.")

    def view_portfolio(self):
        print("\n===== Portfolio Summary =====")

        # Display cryptocurrency data
        crypto_collection = self.db.database["cryptocurrency"]
        crypto_data = list(crypto_collection.find())
        if crypto_data:
            print("\nCryptocurrency Data:")
            for crypto in crypto_data:
                print(crypto)
        else:
            print("No cryptocurrency data available.")

        # Display stock data
        stock_collection = self.db.database["stocks"]
        stock_data = list(stock_collection.find())
        if stock_data:
            print("\nStock Data:")
            for stock in stock_data:
                print(stock)
        else:
            print("No stock data available.")
