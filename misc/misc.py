import string
from random import choice
import hashlib
from python_backend.settings import SECRET_KEY


__all__ = [
    'random_str',
    'gen_uuid4', 'gen_uuid6', 'gen_uuid8', 'gen_uuid10', 'gen_uuid12', 'gen_uuid16',
    'gen_uuid20', 'gen_uuid24', 'gen_uuid32', 'genearteMD5', 'check_md5_password']
RANDOM_CHARS = string.ascii_letters + string.digits


def random_str(length=16, chars=RANDOM_CHARS):
    """generates random string.
    """
    return ''.join([choice(chars) for i in range(length)])


def gen_uuid4():
    return random_str(4)

def gen_uuid6():
    return random_str(6)

def gen_uuid8():
    return random_str(8)

def gen_uuid10():
    return random_str(10)

def gen_uuid12():
    return random_str(12)

def gen_uuid16():
    return random_str(16)

def gen_uuid20():
    return random_str(20)

def gen_uuid24():
    return random_str(24)

def gen_uuid32():
    return random_str(32)

def genearteMD5(str):
    hl = hashlib.md5(SECRET_KEY.encode(encoding='utf-8'))
    hl.update(str.encode(encoding='utf-8'))
    return hl.hexdigest()

def check_md5_password(password, md5password):
    return genearteMD5(password) == md5password