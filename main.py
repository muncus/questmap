#!/usr/bin/env python
#
# Copyright 2007 Google Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
import jinja2
import os
import webapp2
import simplejson as json

from datetime import datetime

from google.appengine.ext import db
from google.appengine.api import users

import model

jinja_env = jinja2.Environment(autoescape=True,
    loader=jinja2.FileSystemLoader(os.path.join(os.path.dirname(__file__), 'templates')))

class MainHandler(webapp2.RequestHandler):
    def get(self):
        if self.request.path == '/list':
            self.qlist()
            return
        template = jinja_env.get_template('index.html')
        self.response.write(template.render())

    def qlist(self):
      """List some quests."""
      qlist = db.GqlQuery("SELECT * FROM Quest")
      template = jinja_env.get_template("list.html")
      self.response.out.write(template.render(questlist=qlist))

class AddQuestHandler(webapp2.RequestHandler):
    """Display form, or receive POST of quest data."""
    def get(self):
      template = jinja_env.get_template('addquest.html')
      self.response.write(template.render())

    def post(self):
      desc = self.request.get('desc', None)
      lat = self.request.get('lat', None)
      lon = self.request.get('lon', None)
      if not lat or not lon:
        self.redirect('/add')
      else:
        nq = model.Quest(
          title=desc,
          description=desc,
          owner=users.get_current_user(),
          created = datetime.now(),
          location = db.GeoPt(lat, lon),
          loc_name = self.request.get('location', ''),
        )
        nq.put()
        self.redirect('/list')

class MapHandler(webapp2.RequestHandler):
    """Handle the showing of the map, and feed of locations."""
    def get(self):
      if self.request.path == "/json":
        return self.getJson()
      else:
        template = jinja_env.get_template('map.html')
        self.response.write(template.render())

    def getJson(self):
      """Generate a json feed, for loading from the map."""
      ZVAL = 1 # static z value for stacking.
      quests = db.GqlQuery(
          "SELECT * FROM Quest WHERE owner = :1", users.get_current_user())
      qlist = []
      for q in quests:
        if not q.location:
          continue
        qlist.append([q.title, q.location.lat, q.location.lon, ZVAL, self.getInfoWindowHtml(q)])
      self.response.write("var locations = " + json.dumps(qlist))

    def getInfoWindowHtml(self, quest):
      """get html to display in the InfoWindow."""
      return "<b>%(title)s</b><br/><span class='muted'>%(loc)s</span>" % {
          'title': quest.title,
          'loc': quest.loc_name, }


app = webapp2.WSGIApplication([
    ('/', MainHandler),
    ('/list', MainHandler),
    ('/add', AddQuestHandler),
    ('/json', MapHandler),
    ('/map', MapHandler),
], debug=True)
