from google.appengine.ext import db


class User(db.Model):
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
    user = db.ReferenceProperty(User)
    subject = db.StringProperty(required=True)
    content = db.TextProperty(required=True)
    created = db.DateTimeProperty(auto_now_add=True)
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
        return cls.all().order('-created')


class Comment(db.Model):
    post = db.ReferenceProperty(Post, collection_name='comments')
    user = db.ReferenceProperty(User)
    content = db.TextProperty(required=True)
    created = db.DateTimeProperty(auto_now_add=True)

    def text(self):
        self._text = self.content.replace('\n', '<br>')
        return self._text


class Vote(db.Model):
    post = db.ReferenceProperty(Post, collection_name='votes')
    user = db.ReferenceProperty(User, collection_name='votes')
    vote = db.IntegerProperty()

    @classmethod
    def by_post(cls, post):
        return cls.all().filter('post =', post)
