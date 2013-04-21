secret = 'Lhn9QMD3niqa5JAqk0cTQrVHxOymFgIl1nU'
key    = 'qwertyuiopasdfghjklxcvbnm1234567890'
# ^must be same length^
def generate():
	def scramble(orig):
		import random
		dest = orig[:]
		random.shuffle(dest)
		return dest
	return ''.join([secret[i]+key[i] for i in scramble(range(len(secret)))])
def random(length=20):
	from random import choice
	import string
	return ''.join(choice(string.ascii_uppercase + string.digits) for x in range(length))
def valid(encryption):
	if len(encryption) != len(secret)+len(key):
		return False
	def group(seq,size):
		return (seq[pos:pos + size] for pos in xrange(0, len(seq), size))
	sequence = [list(key).index(item[1:]) for item in group(encryption,2)]
	opt = range(len(sequence))
	for i in range(len(sequence)):
		opt[sequence[i]] = encryption[i*2]
	opt = ''.join(opt)
	return True if secret == opt else False
def custom(secret,key):
	def scramble(orig):
		import random
		dest = orig[:]
		random.shuffle(dest)
		return dest
	return ''.join([secret[i]+key[i] for i in scramble(range(len(secret)))])
def extract(encryption,key):
	if len(encryption) != len(key)*2:
		return False
	def group(seq,size):
		return (seq[pos:pos + size] for pos in xrange(0, len(seq), size))
	sequence = [list(key).index(item[1:]) for item in group(encryption,2)]
	opt = range(len(sequence))
	for i in range(len(sequence)):
		opt[sequence[i]] = encryption[i*2]
	opt = ''.join(opt)
	return opt