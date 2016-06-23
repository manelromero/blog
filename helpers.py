import re
import random
import string
import hashlib
import hmac

# secret key for storing passwords
secret = 'LeWURczMDUhGTikoMcBkAOYtz'


# make cookie hash
def make_secure_val(val):
    return '%s|%s' % (val, hmac.new(secret, val).hexdigest())


# check cookie hash
def check_secure_val(secure_val):
    val = secure_val.split('|')[0]
    if secure_val == make_secure_val(val):
        return val


# generate salt for password
def make_salt(length=5):
    return ''.join(random.choice(string.letters) for i in range(length))


# make password hash
def make_pw_hash(name, pw, salt=None):
    if not salt:
        salt = make_salt()
    h = hashlib.sha256(name + pw + salt).hexdigest()
    return '%s,%s' % (salt, h)


# check if a password is correct
def valid_pw(name, password, h):
    salt = h.split(',')[0]
    return h == make_pw_hash(name, password, salt)


# validate regex patterns
def validate(value, pattern):
    prog = re.compile(pattern)
    return prog.match(value)
