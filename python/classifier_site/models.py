from db import db

class Business(db.Model):
  id = db.Column(db.Integer, primary_key=True)
  unique_id = db.Column(db.String(80))
  name = db.Column(db.String(80))
  address = db.Column(db.String(80))
  description = db.Column(db.Text)
  website = db.Column(db.String(40))
  business_type = db.Column(db.String(40))
  six_code_guesses = db.Column(db.PickleType)
  three_code_buckets = db.Column(db.PickleType)

  def __init__(self, business, business_type, six_code_guesses, three_code_buckets):
    self.unique_id = business['unique_id']
    self.name = business['name']
    self.address = business['address']
    self.description = business['description']
    self.website = business['website'][0] if business['website'] else None
    self.business_type = business_type
    self.six_code_guesses = six_code_guesses
    self.three_code_buckets = three_code_buckets

  def __repr__(self):
    return '<Business %r>' % self.name

