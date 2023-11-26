from pymongo import MongoClient 
import requests 
from datetime import datetime 
import yfinance as yf 
client = MongoClient("mongodb://127.0.0.1:27017/?directConnection=true&serverSelectionTimeoutMS=2000") 
db = client["db_expensetracker"] 
collection = db["cryptoPrices"] # Live Prices of coins 
stockprices = db["stockPrices"] # Live Prices of stocks
availableCrypto = db["availableCrypto"] 
 

def allAvailableCrypto(): 
    url = 'https://api.coingecko.com/api/v3/coins/list' 
    response = requests.get(url) 
    data = response.json()  
    
    availableCrypto.insert_many(data)  
 

 
def search_by_name(name): 
    result = availableCrypto.find_one({'name': name}) 
    if result: 
        return result['id'] 
    else: 
        return "No match found." 
 
# Function to search by ID and return the name 
def search_by_id(id): 
    result = availableCrypto.find_one({'id': id}) 
    if result: 
        return result['name'] 
    else: 
        return "No match found." 
     
#Return price of coin 
def retrieve_price(id): 
    if search_by_id(id) == "No match found.": 
        return False 
 
    apicall = f'https://api.coingecko.com/api/v3/simple/price?ids={id}&vs_currencies=usd&include_market_cap=true' 
 
    
    headers = { 
        'x_cg_pro_api_key': 'CG-LE3C32z3cRVZ57fGDz8aivus' 
    } 
    response = requests.get(apicall, headers=headers) 

    return response 
 
def addCrypto(id): 
    
    retrieve = retrieve_price(id) 
    coindata = retrieve.json() 
    first_key = next(iter(coindata)) 
 
    
    crypto_data = { 
        'symbol': id,  
        'name': search_by_id(id),   
        'priceUSD': coindata[first_key]['usd'], 
        'lastUpdated': datetime.now().strftime('%Y-%m-%d %H:%M'), 
        'marketCap': coindata[first_key]['usd_market_cap'] 
    } 
     
     
    existing_document = collection.find_one({'symbol': id}) 
     
    if existing_document: 
        
        collection.update_one( 
            {'symbol': id},   
            {'$set': crypto_data} 
        ) 
    else: 
        
        collection.insert_one(crypto_data) 
 
 
def add_stock_investment(id): 
    stock = yf.Ticker(id) 
    stock_info = stock.info 
 
    stock_name = stock_info.get("longName", "Unknown") 
    stock_price_usd = stock_info.get("currentPrice") 
    stock_last_updated = datetime.now().strftime('%Y-%m-%d %H:%M') 
    stock_market_cap = stock_info.get("marketCap", 0) 
 
    stock_data = { 
        "ticker": id, 
        "name": stock_name, 
        "priceUSD": stock_price_usd, 
        "lastUpdated": stock_last_updated, 
        "marketCap": stock_market_cap 
        } 
    existing_document = stockprices.find_one({'ticker': id}) 
     
    if existing_document: 
         
        stockprices.update_one( 
            {'ticker': id},  
            {'$set': stock_data} 
        ) 
    else: 
        
        collection.insert_one(stock_data)

def getStockPrice(id):
    stock = yf.Ticker(id)
    return stock.info.get("currentPrice")

    