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
import cgi
import re

from google.appengine.ext import db

template_dir = os.path.join(os.path.dirname(__file__), 'templates')
jinja_env = jinja2.Environment(loader=jinja2.FileSystemLoader(template_dir),autoescape=True)

class Handler(webapp2.RequestHandler):
    def write(self, *a, **kw):
        self.response.out.write(*a, **kw)

    def render_str(self, template, **params):
        t=jinja_env.get_template(template)
        return t.render(params)

    def render(self, template, **kw):
        self.write(self.render_str(template, **kw))

class Blog(db.Model):
    title = db.StringProperty(required = True)
    blog = db.TextProperty(required = True)
    created = db.DateTimeProperty(auto_now_add = True)

class MainPage(Handler):
    def render_blog(self):
        blogposts = db.GqlQuery("SELECT * FROM Blog ORDER BY created DESC limit 5")
        self.render("blog.html", blogposts=blogposts)

    def get(self):
        self.render_blog()


class NewPost(Handler):
    def render_form(self, title="", blog="", error=""):
        self.render("newpost.html", title=title, blog=blog, error=error)

    def get(self):
        self.render_form()

    def post(self):
        title = self.request.get("title")
        blog = self.request.get("blog")

        if title and blog:
            b = Blog(title=title, blog=blog)
            b.put()

            self.redirect("/blog/%s" %(b.key().id()))
        else:
            error="Please enter a title and a blog post!"
            self.render_form(title, blog, error)

class ViewPost(Handler):
    def get(self, id):
        id = int(id)
        blogpost= BlogPost.get_by_id(id)

        self.render("viewpost.html", blogpost=blogpost, id=id)


app = webapp2.WSGIApplication([
    ('/', MainPage),
    ('/newpost', NewPost),
    webapp2.Route('/blog/<ID:\d+>', ViewPost)], debug=True)
