# models for questmap.

from google.appengine.ext import db
from google.appengine.api import users

class Quest(db.Model):
  """Store info about a specific quest."""
  title = db.StringProperty(required=True)
  description = db.TextProperty()
  is_done = db.BooleanProperty(default=False)
  created = db.DateProperty()
  location = db.GeoPtProperty(required=False)
  loc_name = db.StringProperty(required=False)
  owner = db.UserProperty()
