from portfolio import Portfolio
from graph import fetch_crypto_data, fetch_stock_data, visualize_crypto_prices, visualize_stock_prices

def main():
    portfolio = Portfolio()

    while True:
        print("\n===== Stock and Crypto Portfolio Management =====")
        print("1. Add Investment")
        print("2. Remove Investment")
        print("3. Update Investment")
        print("4. View Portfolio")
        print("5. Visualize Crypto Prices")
        print("6. Visualize Stock Prices")
        print("7. Exit")

        choice = input("Enter your choice (1-7): ")

        if choice == "1":
            portfolio.add_investment()
        elif choice == "2":
            portfolio.remove_investment()
        elif choice == "3":
            portfolio.update_investment()
        elif choice == "4":
            portfolio.view_portfolio()
        elif choice == "5":
            crypto_symbol = input("Enter the symbol of the cryptocurrency: ").lower()

            # Ask the user for the graph type
            graph_type = input("Enter the type of graph (line/bar): ").lower()

            crypto_data = fetch_crypto_data(crypto_symbol)
            visualize_crypto_prices(crypto_symbol, crypto_data, graph_type)
        elif choice == "6":
            stock_symbol = input("Enter the stock symbol (e.g., AAPL): ").upper()

            # Ask the user for the graph type
            graph_type = input("Enter the type of graph (line/bar): ").lower()

            stock_data = fetch_stock_data(stock_symbol)
            visualize_stock_prices(stock_symbol, stock_data, graph_type)
        elif choice == "7":
            print("Exiting the application. Goodbye!")
            portfolio.close_connection()
            break
        else:
            print("Invalid choice. Please enter a number between 1 and 7.")

if __name__ == "__main__":
    main()
