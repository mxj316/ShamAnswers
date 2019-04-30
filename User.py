# User class, primarily used to deal with authorization to view admin page

class User():
    def __init__(self, email, username, authorized):
        self.email = email
        self.username = username
        self.authorized = authorized

    def set_username(self, username):
        self.username = username 

    def get_username(self):
        return self.username

    def set_email(self, email):
        self.email = email

    def get_email(self):
        return self.email

    def set_authorized(self, authorized):
        self.authorized = authorized

    def get_authorized(self):
        return self.authorized
