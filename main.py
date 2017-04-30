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
import webapp2
import os
import jinja2

from google.appengine.ext import db

template_dir = os.path.join(os.path.dirname(__file__), 'templates')
jinja_env = jinja2.Environment(loader=jinja2.FileSystemLoader(template_dir),autoescape=True)


class Handler(webapp2.RequestHandler):
    def write(self, *a, **kw):
        self.response.write(*a, **kw)

    def render_str(self, template, **params):
        t=jinja_env.get_template(template)
        return t.render(params)

    def render(self, template, **kw):
        self.write(self.render_str(template, **kw))

class BlogPost(db.Model):
    title = db.StringProperty(required = True)
    entry = db.TextProperty(required = True)
    created = db.DateTimeProperty(auto_now_add = True)

class MainPageHandler(Handler):
    def get(self):
        self.redirect("/blog")

class BlogPage(Handler):
    def render_blog(self, title="", entry="", error=""):
        posts = db.GqlQuery("SELECT * FROM BlogPost ORDER BY created DESC LIMIT 5")
        self.render('blog.html', title=title, entry=entry, error=error, posts=posts)

    def get(self):
        page = self.request.get("page","1")
        self.render_blog(page)


class NewPost(Handler):

    def render_form(self, title="", entry="", error=""):
        self.render("newpost.html", title=title, entry=entry, error=error)

    def get(self):
        self.render_form()

    def post(self):
        title = self.request.get("title")
        entry = self.request.get("entry")

        if title and entry:
            b = BlogPost(title=title, entry=entry)
            b.put()
            postroute = BlogPost.key(b).id()
            self.redirect("/blog/" + str(postroute))
        else:
            error="Please enter a title and text!"
            self.render_form(title=title, entry=entry, error=error)

class ViewPost(Handler):
    def get(self, id):
        id = int(id)
        blogpost= BlogPost.get_by_id(id)

        self.render("viewpost.html", blogpost=blogpost, id=id)


app = webapp2.WSGIApplication([
    ('/', MainPageHandler),
    ('/blog', BlogPage),
    ('/newpost', NewPost),
    webapp2.Route('/blog/<id:\d+>', ViewPost),
], debug=True)
