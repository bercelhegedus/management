from werkzeug.security import generate_password_hash, check_password_hash

class User():
    def __init__(self, id, username, password):
        self.id = id
        self.username = username
        self.password_hash = generate_password_hash(password)

    def verify_password(self, password):
        return check_password_hash(self.password_hash, password)

    @property
    def is_authenticated(self):
        return True

    @property
    def is_active(self):
        return True  # You can change this if you want to add an active/inactive system

    @property
    def is_anonymous(self):
        return False

    def get_id(self):
        return str(self.id)  # Python 3

