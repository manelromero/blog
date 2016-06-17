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
	subject = db.StringProperty(required=True)
	content = db.TextProperty(required=True)
	created = db.DateTimeProperty(auto_now_add=True)

	def text(self):
		self._text = self.content.replace('\n', '<br>')
		return self._text

	@classmethod
	def get_all(cls):
		return cls.all().order('-created')


class Comment(db.Model):
	subject = db.StringProperty(required=True)
	content = db.TextProperty(required=True)
	created = db.DateTimeProperty(auto_now_add=True)

	def text(self):
		self._text = self.content.replace('\n', '<br>')
		return self._text

	@classmethod
	def get_all(cls):
		return cls.all().order('-created')


