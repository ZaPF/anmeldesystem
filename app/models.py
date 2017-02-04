from flask_login import UserMixin

class User(UserMixin):
    def __init__(self, **kwargs):
        self.__dict__.update(kwargs)

    def get_id(self):
        return self.username
