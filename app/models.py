from flask import current_app
from flask_login import UserMixin
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer

from app import db, login_manager


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)

    # User authentication information
    username = db.Column(db.String(50), nullable=False, unique=True)
    password = db.Column(db.String(255), nullable=False, server_default='')

    # User email information
    email = db.Column(db.String(255), nullable=False, unique=True)
    # confirmed_at = db.Column(db.DateTime())

    # User information
    # active = db.Column('is_active', db.Boolean(), nullable=False, server_default='0')
    # first_name = db.Column(db.String(100), nullable=False, server_default='')
    # last_name = db.Column(db.String(100), nullable=False, server_default='')

    # user account confirmation
    confirmed = db.Column(db.Boolean, default=False)

    # Relationships
    roles = db.relationship('Role', secondary='user_roles',
                            backref=db.backref('users', lazy='dynamic'))

    def __init__(self, username, email, password):
        self.username = username
        self.email = email
        self.password = password

    def generate_confirmation_token(self, expiration=3600):
        s = Serializer(current_app.config['SECRET_KEY'], expiration)
        return s.dumps({'confirm': self.id}).decode('utf-8')

    def confirm(self, token):
        s = Serializer(current_app.config['SECRET_KEY'])
        try:
            data = s.loads(token.encode('utf-8'))
        except:
            return False
        if data.get('confirm') != self.id:
            return False
        self.confirmed = True
        db.session.add(self)
        return True


# Define the Role data model
class Role(db.Model):
    id = db.Column(db.Integer(), primary_key=True)
    name = db.Column(db.String(50), unique=True)


# Define the UserRoles data model
class UserRoles(db.Model):
    id = db.Column(db.Integer(), primary_key=True)
    user_id = db.Column(db.Integer(), db.ForeignKey('user.id', ondelete='CASCADE'))
    role_id = db.Column(db.Integer(), db.ForeignKey('role.id', ondelete='CASCADE'))


# def set_password(self, password):
#     self.password_hash = generate_password_hash(password)
#
# def check_password(self, password):
#     return check_password_hash(self.password_hash, password)
@login_manager.user_loader
def load_user(user_id):
    return db.session.query(User).get(user_id)
