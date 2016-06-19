import webapp2
import os
import jinja2

from entities import User, Post, Comment
from helpers import validate, make_pw_hash, make_secure_val, valid_pw,\
    check_secure_val

template_dir = os.path.join(os.path.dirname(__file__), 'templates')
jinja_env = jinja2.Environment(
    loader=jinja2.FileSystemLoader(template_dir),
    autoescape=True
    )

def render_str(template, **pams):
    t = jinja_env.get_template(template)
    return t.render(params)


class Handler(webapp2.RequestHandler):
    def write(self, *a, **kw):
        self.response.out.write(*a, **kw)

    def render_str(self, template, **kw):
        t = jinja_env.get_template(template)
        return t.render(kw)

    def render(self, template, **kw):
        self.write(self.render_str(template, **kw))

    def set_secure_cookie(self, name, val):
        cookie_val = make_secure_val(val)
        self.response.headers.add_header(
            'Set-Cookie',
            '%s=%s; Path=/' % (name, cookie_val)
            )

    def read_secure_cookie(self, name):
        cookie_val = self.request.cookies.get(name)
        return cookie_val and check_secure_val(cookie_val)

    def uid(self):
        return int(self.read_secure_cookie('user_id'))

    def logout(self):
        self.response.headers.add_header('Set-Cookie', 'user_id=; Path=/')

    def login(self, user):
        self.set_secure_cookie('user_id', str(user.key().id()))

    def initialize(self, *a, **kw):
        webapp2.RequestHandler.initialize(self, *a, **kw)
        uid = self.read_secure_cookie('user_id')
        self.user = uid and User.by_id(int(uid))


class Home(Handler):
    def get(self):
        if self.user:
            posts = Post.get_all()
            self.render(
                'post.html',
                posts=posts,
                user=self.user.name,
                user_id=self.uid()
                )
        else:
            self.redirect('/login')


class SignUp(Handler):
    def get(self):
        self.render('sign-up.html')

    def post(self):
        name = self.request.get('username')
        password = self.request.get('password')
        verify = self.request.get('verify')
        email = self.request.get('email')
        error = {}

        user = User.by_name(name)
        if user:
            error['name'] = "User already exists"

        name_ok = name and validate(name, '^[a-zA-Z0-9_-]{3,20}$')
        if not name_ok:
            error['name'] = "That's not a valid user name"

        password_ok = password and validate(password, '^.{3,20}$')
        if not password_ok:
            error['password'] = "That wasn't a valid password"

        if email !='':
            if not validate(email, '^[\S]+@[\S]+.[\S]+$'):
                error['email'] = "That's not a valid email"

        if verify != password:
            error['verify'] = "Your passwords didn't match"

        if not error:
            pw_hash = make_pw_hash(name, password)
            user = User(name=name, password=pw_hash, email=email)
            user.put()
            self.login(user)
            self.redirect('/')

        self.render('sign-up.html',
            name=name,
            email=email,
            error=error
            )


class LogIn(Handler):
    def get(self):
        self.render('log-in.html')

    def post(self):
        name = self.request.get('username')
        password = self.request.get('password')
        error = {}

        user = User.by_name(name)
        if not user:
            error['name'] = "User doesn't exist"
        else:
            password_ok = password and valid_pw(name, password, user.password)
            if not password_ok:
                error['password'] = "Invalid password"

        if not error:
            self.login(user)
            self.redirect('/')

        self.render('log-in.html', name=name, error=error)


class LogOut(Handler):
    def get(self):
        self.logout()
        self.redirect('/login')


class NewPost(Handler):
    def render_new_post(self, subject="", content="", error=""):
        self.render(
            'new-post.html',
            subject=subject,
            content=content,
            error=error
            )

    def get(self):
        self.render_new_post()

    def post(self):
        subject = self.request.get('subject')
        content = self.request.get('content')

        if subject and content:
            post = Post(
                subject=subject,
                content=content,
                user_id=self.uid()
                )
            post.put()
            post_id = post.key().id()
            self.redirect('/' + str(post_id))
        else:
            error = 'Sorry, we need both, title and content.'
            self.render_new_post(subject, content, error)


class PostLink(Handler):
    def get(self, post_id):
        post = Post.get_by_id(int(post_id))
        self.render('permalink.html', post=post, user_id=self.uid())


app = webapp2.WSGIApplication([
    ('/', Home),
    ('/signup', SignUp),
    ('/login', LogIn),
    ('/logout', LogOut),
    ('/newpost', NewPost),
    ('/([0-9]+)', PostLink)
    ], debug=True)


# dev_appserver.py blog
# appcfg.py -A skilful-album-134323 -V v1 update blog/
# http://skilful-album-134323.appspot.com/
