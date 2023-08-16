from werkzeug.security import generate_password_hash, check_password_hash

class User():
    def __init__(self, id, username, password, alvallalkozok):
        self.id = id
        self.username = username
        self.password_hash = generate_password_hash(password)
        self.alvallalkozok = alvallalkozok

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



# Example users (id, username, password)
users = [
    User(1, 'test', 'test123', ['Privát Technoszer']),
    User(2, 'baloghj', 'kkhalas', ['Privát Technoszer']),
]