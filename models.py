from sqlalchemy.dialects.postgresql import JSON,JSONB
from app import db

class TestTable(db.Model):
    __tablename__ = 'testtable'
    id   = db.Column(db.Integer, primary_key=True)
    data = db.Column(JSONB)
    message = db.Column(db.String)
    istrue = db.Column(db.Boolean, default=False)
