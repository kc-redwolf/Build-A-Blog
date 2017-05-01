import webapp2
import os
import jinja2
import re
import cgi


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
        blogposts = db.GqlQuery("SELECT * FROM Blog ORDER BY created LIMIT 5")
        self.render("blog.html", blogposts=blogposts)

    def get(self):
        self.render_blog()


class NewPost(Handler):
    def render_form(self, title="", blog="", error=""):
        self.render("newpost.html", title=title, blog=blog, error=error)

    def get(self):
        self.render_form()

    def post(self):
        title = self.request.get("blog-title")
        blog = self.request.get("blog-body")

        if title and blog:
            blog_post = Blog(title=title, blog=blog)
            blog_post.put()
            id = blog_post.key().id()
            self.redirect("/blog/" + str(id))
        else:
            error="Please enter a title and a blog post!"
            self.render_form(title=title, blog=blog, error=error)

class ViewPostHandler(Handler):
    def get(self, id, title="", blog=""):
        post = Blog.get_by_id(int(id))

        if post:
            self.render("viewpost.html", title=title, blog=blog, post=post)
        else:
            error = "No Post Found For ID"
            self.render("viewpost.html", error=error)


app = webapp2.WSGIApplication([
    ('/', MainPage),
    ('/blog', Blog),
    ('/blog/newpost', NewPost),
    (webapp2.Route('/blog/<id:\d+>', ViewPostHandler))], debug=True)
