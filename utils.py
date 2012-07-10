import string
from random import shuffle
from urlparse import urlparse
#from django.utils.encoding import smart_str


def validate_url(url):
    #import pdb; pdb.set_trace()
    #this only wants bytestrs
    pieces = urlparse(url)
    assert all([pieces.scheme, pieces.netloc])
    assert set(pieces.netloc) <= set(string.letters + string.digits + '-.')  # and others?
    assert pieces.scheme in ['http', 'https', 'ftp']
    return pieces.geturl()



class Alphabet():
    def __init__(self,chars="23456789abcdefghijkmnpqrstuvwxyzABCDEFGHJKLMNPQRSTUVWXYZ",
               salt=lambda:0.03950477560662613,
               min_size=6,
               skip=1000 ):
        _ = list(chars)
        shuffle(_,salt)
        self.alphabet = ''.join(_)
        base = len(self.alphabet)
        #the lowest number with min_size digits in this base is base^6
        self.offset = base**min_size
        self.skip = skip
        self.base_dict = dict((c, i) for i, c in enumerate(self.alphabet))

        #BASE_DICT = lambda a : dict((c, i) for i, c in enumerate(a))


def base_decode(string):
    alphabet = Alphabet()
    reverse_base = alphabet.base_dict
    length = len(reverse_base)
    ret = 0
    for i, c in enumerate(string[::-1]):
        ret += (length ** i) * reverse_base[c]
    ret /= alphabet.skip
    ret -= alphabet.offset
    return ret

def base_encode(integer):
    alphabet = Alphabet()
    base = alphabet.alphabet
    length = len(base)
    ret = ''
    integer += alphabet.offset
    integer *= alphabet.skip
    while integer != 0:
        ret = base[integer % length] + ret
        integer /= length

    return ret


if __name__=='__main__':
    nums = [0, 10 ** 10] + range(0, 1000)
    for i in nums:
        assert i == base_decode(base_encode(i)), '%s failed' % i