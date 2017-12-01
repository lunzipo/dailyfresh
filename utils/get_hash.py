from hashlib import sha1


def get_hash(str):
    '''取一个字符串的hash值'''
    sha_value = sha1()
    sha_value.update(str.encode('utf8'))
    return sha_value.hexdigest()
