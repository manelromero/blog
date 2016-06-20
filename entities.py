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
	votes = db.IntegerProperty(default=0)

	def text(self):
		self._text = self.content.replace('\n', '<br>')
		return self._text

	def upvote(self):
		self.votes += 1

	def downvote(self):
		self.votes += 1

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
