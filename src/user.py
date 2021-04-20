from flask_login import UserMixin

class User(UserMixin):
    user = None
    password = None

    def __init__(self, user, password):
        self.id = user
        self.user = user
        self.password = password
        self.authenticated = False 
        
    def get_user(self):
        return self.user
    
    def get_password(self):
        return self.password

    def is_active(self):
        return self.is_active()    
    
    def is_anonymous(self):
        return False    
    
    def is_authenticated(self):
        return self.authenticated    
    
    def is_active(self):
        return True  

    def get_id(self):
        return self.id