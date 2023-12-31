from flask import Flask, render_template, request,redirect,flash,session
import DBoperations as db
import nonrelationaldb as ndb
from datetime import datetime
import pandas as pd

app = Flask(__name__)
app.secret_key = 'your_very_secret_key_here'

@app.route('/')
@app.route('/home')
def index():
    return render_template('index.html')

@app.route('/register')
def showregister():
    return render_template('register.html')

@app.route('/register', methods=['POST'])
def register():
    if request.method=='POST':
        email = request.form['email']
        username = request.form['username']
        password = request.form['password']
        response = db.register_user(email,username,password)
        
        return redirect('/')
    


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        if db.valid_login(email, password):
            user =db.retrieve_userdata(email)
            session['id'] = user.user_id
            session['name']=user.name
            session['email']=user.email
            return redirect('/dashboard')
        else:
            flash('Invalid email or password', 'error')
            return redirect('/login')

    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('id', None)
    session.pop('name', None)
    session.pop('email', None)  
    return redirect('/')

@app.route('/dashboard')
def dashboard():
    return render_template('dashboard.html')

@app.route('/assets')
def show_assets():

    assets = db.get_assets_for_user(session['id'])
    
    
    return render_template('assets.html', assets=assets)
@app.route('/filter_highest_assets')
def show_highest_assets():

    assets = db.filter_highest_assets(session['id'])


    return render_template('assets.html', assets=assets)
@app.route('/addasset')
def add_assets():
    return render_template('addasset.html')

@app.route('/submit_asset', methods=['POST'])
def submit_asset():
    asset_type = request.form['assetType']
    id_or_ticker = request.form['idOrTicker']
    amount = request.form['amount']
    price = request.form['price']

    
    if asset_type == 'crypto':
        asset_type_id = 1
        retrieve = ndb.retrieve_price(id_or_ticker)
        coindata = retrieve.json() 
        first_key = next(iter(coindata)) 
        value = coindata[first_key]['usd']
        
    elif asset_type == 'stock':
        asset_type_id = 2
        value = ndb.getStockPrice(id_or_ticker)

    
    date_purchased = datetime.now()
    db.add_new_asset(id_or_ticker,value,amount,asset_type_id,date_purchased,session['id'],price)
    

    return redirect('/assets')  

@app.route('/delete_asset', methods=['POST'])
def delete_asset():
    asset_id = request.form['asset_id']
    db.delete_asset(asset_id)

    return redirect('/assets')  

@app.route('/incomeandexpenses')
def view_income_and_expenses():
    
    incomes = db.get_all_incomes(session['id'])  

    
    expenses = db.get_all_expenses(session['id'])  
    
    return render_template('incomeandexpenses.html', incomes=incomes, expenses=expenses)

@app.route('/add_income', methods=['GET', 'POST'])
def add_income():
    income_types = db.get_transaction_types('income')  
    frequencies = db.get_frequencies()  
        

    return render_template('add_income.html', income_types=income_types, frequencies=frequencies)
@app.route('/filter_highest_return_assets')
def show_highest_return_assets():

    assets = db.filter_highest_return_assets(session['id'])


    return render_template('assets.html', assets=assets)
@app.route('/filter_alphabetical')
def show_alphabetical():

    assets = db.filter_alphabetical(session['id'])


    return render_template('assets.html', assets=assets)
@app.route('/update_nextdue', methods=['GET', 'POST'])
def update_nextdue():
    db.update_nextdue()
    incomes = db.get_all_incomes(session['id']) 

    
    expenses = db.get_all_expenses(session['id'])  

    return render_template('incomeandexpenses.html', incomes=incomes, expenses=expenses)
@app.route('/save_income', methods=['POST'])
def save_income():
    try:

        name = request.form['name']
        value = request.form['value']
        type_name = request.form['type']  
        date_purchased = request.form['datepurchased']
        frequency_name = request.form['frequency']  
        next_due = request.form['nextdue']

        
        

        
        db.add_income(name, value, type_name, date_purchased,session['id'], frequency_name, next_due)

        
        return redirect('/incomeandexpenses')
    except Exception as e:
        
        print(f"An error occurred: {e}")
        
        return str(e), 500

@app.route('/delete_income', methods=['POST'])
def delete_income():
    income_id = request.form['income_id']
    db.delete_income(income_id)
    return redirect('/incomeandexpenses')  
    
@app.route('/add_expense', methods=['GET', 'POST'])
def add_expense():
    expense_types = db.get_transaction_types('expense') 
    frequencies = db.get_frequencies()
    return render_template('add_expense.html',expense_types=expense_types,frequencies=frequencies)

@app.route('/save_expense', methods=['POST'])
def save_expense():
    try:
        
        name = request.form['name']
        value = request.form['value']
        type_name = request.form['type']  
        date_occurred = request.form['datepurchased']
        frequency_name = request.form['frequency']  
        next_due = request.form['nextdue']

        
        print(f"Received expense form data: {name}, {value}, {type_name}, {date_occurred}, {frequency_name}, {next_due}")

        
        db.add_expense(name, value, type_name, date_occurred, session['id'], frequency_name, next_due)

        
        return redirect('/incomeandexpenses')  
    except Exception as e:
        print(f"An error occurred: {e}")
        return str(e), 500

@app.route('/delete_expense', methods=['POST'])
def delete_expense():
    expense_id = request.form['expense_id']
    db.delete_expense(expense_id)
    return redirect('/incomeandexpenses')

@app.route('/predict_income_expenses', methods=['GET'])
def predict_income_expenses():
    expenses = db.predict_income_expenses(session['id'])
    print(expenses)
    return expenses

@app.route('/overall_distribution_of_expenses', methods=['GET'])
def overall_distribution_of_expenses():
    expenses = db.overall_distribution_of_expenses(session['id'])
    return expenses

@app.route('/overall_distribution_of_income', methods=['GET'])
def overall_distribution_of_income():
    expenses = db.overall_distribution_of_income(session['id'])
    return expenses

@app.route('/overall_distribution_of_portfolio', methods=['GET'])
def overall_distribution_of_portfolio():
    expenses = db.overall_distribution_of_portfolio(session['id'])
    return expenses

@app.route('/get_portfolio_value', methods=['GET'])
def get_portfolio_value():
    data=db.overall_portfolio_value(session['id'])
    return data

@app.route('/most_recently_added', methods=['GET'])
def most_recently_added():
    data=db.most_recently_added(session['id'])
    return data

if __name__ == '__main__':
    app.run(port=5000, debug=False)
    



