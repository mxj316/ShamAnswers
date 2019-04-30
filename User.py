# User class, primarily used to deal with authorization to view admin page

class User():
    def __init__(self, id, email, authorized):
        self.id = id
        self.email = username
        if authorized == 'admin':
            self.authorized = True
        else:
            self.authorized = False

    def set_id(self, id):
        self.id = id

    def get_id(self):
        return self.id

    def set_email(self, email):
        self.email = email

    def get_email(self):
        return self.email

    def set_authorized(self, authorized):
        self.authorized = authorized

    def get_authorized(self):
        return self.authorized
