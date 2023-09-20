from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import MetaData
from sqlalchemy.orm import validates
from sqlalchemy.ext.associationproxy import association_proxy
from sqlalchemy_serializer import SerializerMixin

convention = {
    "ix": "ix_%(column_0_label)s",
    "uq": "uq_%(table_name)s_%(column_0_name)s",
    "ck": "ck_%(table_name)s_%(constraint_name)s",
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
    "pk": "pk_%(table_name)s"
}

metadata = MetaData(naming_convention=convention)

db = SQLAlchemy(metadata=metadata)


class Activity(db.Model, SerializerMixin):
    __tablename__ = 'activities'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    difficulty = db.Column(db.Integer)

    # Add relationship
    signups = db.relationship('Signup', backref='activity', cascade='all, delete-orphan')
    campers = association_proxy('signups', 'camper')
    # Add serialization rules
    
    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "difficulty": self.difficulty,
        }

    def __repr__(self):
        return f'<Activity {self.id}: {self.name}>'


class Camper(db.Model, SerializerMixin):
    __tablename__ = 'campers'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    age = db.Column(db.Integer)

    # Add relationship
    signups = db.relationship('Signup', backref='camper', cascade='all, delete-orphan')
    activities = association_proxy('signups', 'activity')
    # Add serialization rules
    
    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "age": self.age
        }
    
    def to_dict_su_act(self):
        camper = self.to_dict()
        camper['signups'] = [{"activity": a.to_dict()} for a in self.activities]
        return camper



    # Add validation
    
    @validates('name')
    def validate_name(self, key, name):
        if type(name) is str and name:
            return name
        else:
            raise ValueError('Camper must have a name of type str')

    @validates('age')
    def validate_age(self, key, age):
        if type(age) is int and 8 <= age <= 18:
            return age
        else:
            raise ValueError('Camper must be between 8 - 18 years old')

    
    def __repr__(self):
        return f'<Camper {self.id}: {self.name}>'


class Signup(db.Model, SerializerMixin):
    __tablename__ = 'signups'

    id = db.Column(db.Integer, primary_key=True)
    time = db.Column(db.Integer)

    # Add relationships
    camper_id = db.Column(db.Integer, db.ForeignKey('campers.id'))
    activity_id = db.Column(db.Integer, db.ForeignKey('activities.id'))
    # Add serialization rules
    def to_dict(self):
        return {
            "id": self.id,
            "time": self.time,
            "camper_id": self.camper_id,
            "activity_id": self.activity_id
        }
    def signup_to_dict_full_details(self):
        signup = self.to_dict()
        signup['activity'] = self.activity.to_dict()
        signup['camper'] = self.camper.to_dict()
        return signup


    # Add validation
    @validates('time')
    def validate_time(self, key, time):
        if type(time) is int and 0<= time <= 23:
            return time
        else:
            raise ValueError('Activity time must be between 0 - 23')

    
    def __repr__(self):
        return f'<Signup {self.id}>'


# add any models you may need.
