from google.appengine.ext import db


class User(db.Model):
    """
    User entity class
    -----------------------------------------------------------------------
    Stores all user data. Declares methods for getting users by id and name
    """
    name = db.StringProperty(required=True)
    password = db.StringProperty(required=True)
    email = db.StringProperty()

    @classmethod
    def by_id(cls, uid):
        return cls.get_by_id(uid)

    @classmethod
    def by_name(cls, name):
        user = cls.all().filter('name =', name).get()
        return user


class Post(db.Model):
    """
    Post entity class
    ------------------------------------------------------------------------
    Stores all posts. It has an user reference property, methods for getting
    all posts and post by id. Declares functions to include safe HTML code in
    the post content and manage post voting
    """
    user = db.ReferenceProperty(User)
    subject = db.StringProperty(required=True)
    content = db.TextProperty(required=True)
    last_edited = db.DateTimeProperty(auto_now=True)

    def text(self):
        self._text = self.content.replace('\n', '<br>')
        return self._text

    def sumVotes(self):
        total = 0
        for vote in self.votes:
            total += vote.vote
        return total

    @classmethod
    def by_id(cls, pid):
        return cls.get_by_id(pid)

    @classmethod
    def get_all(cls):
        return cls.all().order('-last_edited')


class Comment(db.Model):
    """
    Comment entity class
    --------------------------------------------------------------------------
    Stores all comments. It has post and user reference properties. Declares a
    function to include safe HTML code in the comment content
    """
    post = db.ReferenceProperty(Post, collection_name='comments')
    user = db.ReferenceProperty(User)
    content = db.TextProperty(required=True)
    created = db.DateTimeProperty(auto_now_add=True)

    def text(self):
        self._text = self.content.replace('\n', '<br>')
        return self._text

    @classmethod
    def by_id(cls, pid):
        return cls.get_by_id(pid)


class Vote(db.Model):
    """
    Vote entity class
    ---------------------------------------------------------------------------
    Stores all votes. It has post and user reference properties and a method to
    get all comments of a post used for checking that any user doesn't vote
    more than once on a post
    """
    post = db.ReferenceProperty(Post, collection_name='votes')
    user = db.ReferenceProperty(User, collection_name='votes')
    vote = db.IntegerProperty()

    @classmethod
    def by_post(cls, post):
        return cls.all().filter('post =', post)
