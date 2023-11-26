# Setup

1. Ensure you have Python3 installed
2. Make sure you have PostgreSQL installed in your environment and running.
3. Setup a python virtual environment inside the backend folder (`python3 -m venv env`).
4. To activate virtual environment (`source env/bin/activate`).
5. Run `pip install -r requirements.txt`.
6. Type `flask run` to run the backend server.
7. Server should run on `127.0.0.1:5000`. Must be 127.0.0.1, cannot use localhost.

## How to use API

To interface with the database, you need to send HTTP requests to this server API.
Refer below for the CRUD operations for table `users`, applies for other tables.

### CREATE
Url: http://127.0.0.1:5000/users/add
Method: POST
Description: Inserts the input from client with `INSERT`. The input is a JSON object. Refer to Fetch API on Google on usage.

### READ
Url: http://127.0.0.1:5000/users
Method: GET
Description: Retrieves the list of users with `SELECT * FROM USERS;`

### UPDATE
Url: http://127.0.0.1:5000/users/update/<int:user_id>
Method: PUT
Description: Updates the row based on its primary key inputted in the url, for example /users/update/4 updates row with userid=4. The input data is also a JSON object. Uses SQL `UPDATE` query.

### DELETE
Url: http://127.0.0.1:5000/users/delete/<int:user_id>
Method: GET
Description: Deletes the row based on its primary key inputted in the url. Uses SQL `DELETE` query.
