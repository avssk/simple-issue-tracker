from sqlalchemy import Column,Integer,String,ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker
from sqlalchemy import create_engine
from passlib.apps import custom_app_context as pwd_context
import random, string
from itsdangerous import(TimedJSONWebSignatureSerializer as Serializer, BadSignature, SignatureExpired)

Base = declarative_base()
secret_key = ''.join(random.choice(string.ascii_uppercase + string.digits) for x in xrange(32))

class User(Base):
    __tablename__ = 'user'
    id = Column(Integer, primary_key=True)
    email = Column(String)
    username = Column(String(32), index=True)
    firstname = Column(String)
    lastname = Column(String)
    password_hash = Column(String(64))

    def hash_password(self, password):
        self.password_hash = pwd_context.encrypt(password)

    def verify_password(self, password):
        return pwd_context.verify(password, self.password_hash)

    def generate_auth_token(self, expiration=600):
    	s = Serializer(secret_key, expires_in = expiration)
    	return s.dumps({'id': self.id })

    @staticmethod
    def verify_auth_token(token):
    	s = Serializer(secret_key)
    	try:
    		data = s.loads(token)
    	except SignatureExpired:
    		#Valid Token, but expired
    		return None
    	except BadSignature:
    		#Invalid Token
    		return None
    	user_id = data['id']
    	return user_id

    @property
    def serialize(self):
         return {
            "id" : self.id,
            "email" : self.email,
            "username": self.username,
            "firstname" : self.firstname,
            "lastname" : self.lastname
            }


class Issue(Base):
    __tablename__ = 'issue'
    id = Column(Integer, primary_key=True)
    title = Column(String)
    description = Column(String)
    status = Column(String)
    user_assigned_by_id = Column(Integer, ForeignKey('user.id'), nullable=False)
    user_assigned_to_id = Column(Integer, ForeignKey('user.id'), nullable=False)
    user_assigned_by = relationship("User", foreign_keys=[user_assigned_by_id])
    user_assigned_to = relationship("User", foreign_keys=[user_assigned_to_id])

    @property
    def serialize(self):
        return {
        'id' : self.id,
        'title' : self.title,
        'description' : self.description,
        'user_assigned_to_id' : self.user_assigned_to_id,
        'user_assigned_by_id' : self.user_assigned_by_id,
        'status' : self.status
            }

engine = create_engine('sqlite:///SIT.db')
Base.metadata.create_all(engine)
