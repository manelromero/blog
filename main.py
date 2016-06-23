import webapp2
import os
import jinja2

from entities import User, Post, Comment, Vote
from helpers import validate, make_pw_hash, make_secure_val, valid_pw,\
    check_secure_val

# jinja2 template location definition
template_dir = os.path.join(os.path.dirname(__file__), 'templates')
jinja_env = jinja2.Environment(
    loader=jinja2.FileSystemLoader(template_dir),
    autoescape=True
    )


class Handler(webapp2.RequestHandler):
    """
    Handler class
    -----------------------------------------------------------------
    Contains all needed functions for the rest handlers to inheritate
    """
    # writes the response
    def write(self, *a, **kw):
        self.response.out.write(*a, **kw)

    # sends the jinja2 template for rendering
    def render_str(self, template, **kw):
        t = jinja_env.get_template(template)
        return t.render(kw)

    # renders the template
    def render(self, template, **kw):
        self.write(self.render_str(template, **kw))

    # sets cookie
    def set_secure_cookie(self, name, val):
        cookie_val = make_secure_val(val)
        self.response.headers.add_header(
            'Set-Cookie',
            '%s=%s; Path=/' % (name, cookie_val)
            )

    # reads cookie
    def read_secure_cookie(self, name):
        cookie_val = self.request.cookies.get(name)
        return cookie_val and check_secure_val(cookie_val)

    # gets the user id
    def uid(self):
        uid = self.read_secure_cookie('user_id')
        if uid:
            return int(uid)

    # logs the user out
    def logout(self):
        self.response.headers.add_header('Set-Cookie', 'user_id=; Path=/')

    # logs the user in
    def login(self, user):
        self.set_secure_cookie('user_id', str(user.key().id()))

    # checks the user is logged in
    def initialize(self, *a, **kw):
        webapp2.RequestHandler.initialize(self, *a, **kw)
        uid = self.uid()
        self.user = uid and User.by_id(uid)


class Home(Handler):
    """
    Home class
    --------------------------------------------------------------------------
    Main blog page
    Shows all posts and gets post votes. If an user tries to vote without been
    logged in, then is redirected to the login page
    """
    # get posts and show them all
    def get(self):
        posts = Post.get_all()
        self.render('home.html', posts=posts, user=self.user)

    # get votes, up or down
    def post(self):
        # somebody is trying to vote, let's check if is logged in
        if self.user:
            post = Post.by_id(int(self.request.get('post_id')))
            user = self.user
            vote = int(self.request.get('vote'))
            # prepare the new vote
            new_vote = Vote(post=post, user=user, vote=vote)
            # check the user has not voted on this post before
            no_vote = True
            votes = Vote.by_post(post)
            for v in votes:
                # if user has already voted then False
                if v.user.key().id() == self.uid():
                    no_vote = False
            # has not voted before, let's put the vote
            if no_vote:
                new_vote.put()
            self.redirect('/')
        # not logged in, let's go to the login page
        else:
            self.redirect('/login')


class SignUp(Handler):
    """
    SignUp class
    ----------------------------------------------------------------------
    Sign up page for new users
    Checks that the new user doesn't already exist and that all fields are
    correct
    """
    # renders the HTML page with the sign up form
    def get(self):
        self.render('sign-up.html')

    # gets form values
    def post(self):
        name = self.request.get('username')
        password = self.request.get('password')
        verify = self.request.get('verify')
        email = self.request.get('email')
        error = {}
        # let's check if user already exists
        user = User.by_name(name)
        if user:
            error['name'] = "User already exists"
        # let's check if a name it's been introduced and its format
        name_ok = name and validate(name, '^[a-zA-Z0-9_-]{3,20}$')
        if not name_ok:
            error['name'] = "That's not a valid user name"
        # let's check there is a password and its format
        password_ok = password and validate(password, '^.{3,20}$')
        if not password_ok:
            error['password'] = "That wasn't a valid password"
        # let's check the verify password is the same as the password
        if verify != password:
            error['verify'] = "Your passwords didn't match"
        # not needed, but if there is an email let's check its format
        if email != '':
            if not validate(email, '^[\S]+@[\S]+.[\S]+$'):
                error['email'] = "That's not a valid email"
        # if everything went right, let's introduce our new friend
        if not error:
            pw_hash = make_pw_hash(name, password)
            user = User(name=name, password=pw_hash, email=email)
            user.put()
            # now we logged the user in
            self.login(user)
            self.redirect('/')
        # if something went wrong, let's render again showing the error
        self.render('sign-up.html', name=name, email=email, error=error)


class LogIn(Handler):
    """
    LogIn class
    --------------------------------------------------------------
    Log in page for existing users
    Checks that the user already exist and the password is correct
    """
    # renders the HTML page with the log in form
    def get(self):
        self.render('log-in.html')

    # gets form values
    def post(self):
        name = self.request.get('username')
        password = self.request.get('password')
        error = {}
        # let's check if user already exists
        user = User.by_name(name)
        if not user:
            error['name'] = "User doesn't exist"
        # and now the password
        else:
            password_ok = password and valid_pw(name, password, user.password)
            if not password_ok:
                error['password'] = "Invalid password"
        # if everything is right, let's log in the user
        if not error:
            self.login(user)
            self.redirect('/')
        # if something is wrong, let's render again showing the error
        self.render('log-in.html', name=name, error=error)


class LogOut(Handler):
    """
    LogOut class
    --------------------------------------------
    Log out option for logged in users
    Logs out the user and redirects to main page
    """
    def get(self):
        self.logout()
        self.redirect('/')


class NewPost(Handler):
    """
    NewPost class
    ----------------------------------------------------------------------
    New post page for logged in users.
    Checks that the new user doesn't already exist and that all fields are
    correct
    """
    # just a DRY function called from get and post functions
    def render_new_post(self, subject='', content='', error=''):
        self.render(
            'new-post.html',
            subject=subject,
            content=content,
            error=error,
            user=self.user,
            new=True
            )

    # if user is logged in, renders the HTML page with the new post form
    def get(self):
        if self.user:
            self.render_new_post()
        else:
            self.redirect('/')

    # gets form values
    def post(self):
        subject = self.request.get('subject')
        content = self.request.get('content')
        # let's check we have a subject and a content
        if subject and content:
            post = Post(
                subject=subject,
                content=content,
                user=User.by_id(self.uid())
                )
            # post creation
            post.put()
            self.redirect('/')
        # if something is wrong let's show the error
        else:
            error = 'Sorry, we need both, title and content.'
            self.render_new_post(subject, content, error)


class PostLink(Handler):
    """
    PostLink class
    -------------------------------------------------------------
    Permalink page for posts.
    Shows the post page with comments and a form for new comments
    """
    # just a DRY function called from get and post functions
    def render_post(self, post='', error='', user_id=''):
        self.render('permalink.html', post=post, error=error, user=self.user)

    # gets the post and renders the page
    def get(self, post_id):
        post = Post.get_by_id(int(post_id))
        self.render_post(post)

    # gets form values
    def post(self, post_id):
        post = Post.get_by_id(int(post_id))
        content = self.request.get('content')
        # let's check if user is logged in
        if self.user:
            # and there is something in the content field
            if content:
                comment = Comment(
                    post=post,
                    user=User.by_id(self.uid()),
                    content=content
                    )
                comment.put()
                self.render_post(post)
            else:
                error = "Your comment can't be empty"
                self.render_post(post, error)
        # user not logged in, let's go to the login page
        else:
            self.redirect('/login')


class EditPost(NewPost):
    """
    EditPost class
    -----------------------------------------------------
    Shows the edit page with the post content for editing
    """
    # renders the HTML page with the edit form
    def get(self, post_id):
        post = Post.get_by_id(int(post_id))
        self.render('edit-post.html', post=post, user=self.user)

    # gets form values
    def post(self, post_id):
        post = Post.by_id(int(post_id))
        subject = self.request.get('subject')
        content = self.request.get('content')
        # check if we have both subject and content
        if subject and content:
            # check if the user is the post owner or somebody cheating
            if post.user.key().id() == self.uid():
                post.subject = subject
                post.content = content
                post.put()
            self.redirect('/')
        # if something is missing, let's show it to the user
        else:
            error = 'Sorry, we need both, title and content.'
            self.render(
                'edit-post.html',
                post=post,
                user=self.user,
                error=error
                )


class DeletePost(Handler):
    """
    DeletePost class
    --------------------------------------------------------------
    Shows de delete page and if user press 'yes', deletes the post
    """
    # renders the HTML page with the delete form
    def get(self, post_id):
        post = Post.get_by_id(int(post_id))
        self.render('delete-post.html', post=post, user=self.user)

    # if user press 'yes'
    def post(self, post_id):
        post = Post.get_by_id(int(post_id))
        # check if the user is the post owner
        if post.user.key().id() == self.uid():
            post.delete()
        self.redirect('/')


app = webapp2.WSGIApplication([
    ('/', Home),
    ('/signup', SignUp),
    ('/login', LogIn),
    ('/logout', LogOut),
    ('/newpost', NewPost),
    ('/([0-9]+)', PostLink),
    ('/delete/([0-9]+)', DeletePost),
    ('/edit/([0-9]+)', EditPost)
    ], debug=True)
