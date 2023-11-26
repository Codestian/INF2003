class User:
    def __init__(self, user_id, email, name):
        self.user_id = user_id
        self.email = email
        self.name = name

    def __repr__(self):
        return f"User(user_id={self.user_id}, email='{self.email}', name='{self.name}')"
