# generic imports for all methods
from google.appengine.ext import db
import simplr
from google.appengine.ext import blobstore
import webapp2
import logging
# db models
class accesstoken(db.Model):
	url = db.StringProperty(indexed=True)
	age = db.DateTimeProperty(auto_now_add=True)
# methods
data = None
def build():
	def load():
		import urllib2
		try:
			return urllib2.urlopen(data['database']+'/HFrUAGfXSalEo0hSeeEq?dt=%s' % simplr.generate()).read()
			# the rt parameter merely stops caching of the module so multiple backups in a short period of time aren't canceled
		except Exception as error:
			logging.warning('Error 403: forbidden access; Access Refused by %s/HFrUAGfXSalEo0hSeeEq' % data['database'])
			raise Exception(error)
	def create():
		from google.appengine.ext import blobstore
		from google.appengine.api import files
		file_name = files.blobstore.create(mime_type='text/javascript',_blobinfo_uploaded_filename=simplr.random())
		with files.open(file_name, 'a') as f:
			f.write(content)
		files.finalize(file_name)
		blob_key = files.blobstore.get_blob_key(file_name)
		logging.info('Backup Success: blob key is %s' % blob_key)
		return 'Backup Was Successful'
	def memcache():
		import json
		latest = blobstore.BlobInfo.all().order('-creation').fetch(1)
		if len(latest) > 0:
			latest = json.loads(latest[0].open().read())
			if json.loads(content)['backup']==latest['backup']:
				logging.info('Canceling Backup: no changes from last backup detected.')
				return True
			else:
				return False
		else:
			return False
	def compensate():
		def totalSize():
			return sum([blob.size for blob in blobstore.BlobInfo.all()])
		if totalSize()+len(content) > 5360000000:#~ over 4.99gb = 5360000000 bytes
			compensation = 0
			fetch = 0
			while compensation < totalSize()+len(content)-5360000000:
				fetch += 1
				compensation = sum([blob.size for blob in blobstore.BlobInfo.all().order('-creation').fetch(fetch)])
			logging.info('Blobstore Overflow: initiating manditory maintenance sequence; deleting %s files' % fetch)
			for blob in blobstore.BlobInfo.all().order('creation').fetch(fetch):
				blob.delete()
	content = load()
	if memcache():
		return 'Backup Canceled: no changes from last backup detected.'
	compensate()
	return create()
def validateRequest(request,page):
	from google.appengine.api.datastore import Key
	try:
		token = accesstoken.all().filter('__key__ =',Key(request.get('a')))
	except:
		return False
	if token.count() > 0:
		token = token.get()
		if simplr.extract(token.url,'as2df4gh78jklqweo1iu') == page:
			token.delete()
			return True
		else:
			return False
	else:
		return False
def cleanup():
	from datetime import datetime
	tokens = accesstoken.all()
	deletions = 0
	for token in tokens:
		age = (datetime.now()-token.age).seconds
		if age > 3600:# ~ 1 hour = 3600 seconds
			deletions += 1
			token.delete()
	logging.info('%s Tokens Deleted' % str(deletions))
def stats():
	from math import pow, floor
	import datetime
	import EST
	def totalSize():
		bytes = sum([blob.size for blob in blobstore.BlobInfo.all()])
		values = ['Bytes','Kb','Mb','Gb'];
		for i in range(len(values)):
			if bytes >= pow(1024,i) and bytes < pow(1024,i+1):
				return str(round(float(bytes)/pow(1024,i),1))+' %s' % values[i]
		return '0 Bytes' if bytes == 0 else (str(round(bytes/pow(1024,len(values)-1),1))+' %s' % values[:-1])
	def nextBackup():
		difftime = EST.midnightdelta
		result = str(int(floor(float(difftime.seconds)/60/60)))+':'+str(int(round(60*(float(difftime.seconds)/60/60-int(floor(float(difftime.seconds)/60/60))),0)))
		return result if len(result[result.index(':')+1:]) == 2 else result[:result.index(':')+1]+'0'+result[result.index(':')+1:]
	total = blobstore.BlobInfo.all()
	return dict(
		num=total.count(),
		last=((total.order('-creation').fetch(1)[0].creation+EST.timedelta).strftime("%B %d, %Y, %I:%M %p")+' US/Eastern') if total.order('-creation').count() > 0  else 'No Previous Backups',
		next=nextBackup(),
		size=totalSize()
	)
def requestToken():
	key = 'as2df4gh78jklqweo1iu'
	secret = simplr.random(length=len(key))
	token = accesstoken()
	token.url = simplr.custom(secret,key)
	token.put()
	return '/%s?a=%s' % (secret, str(token.key()))
def fetch(token):
	import datetime
	import json
	import EST
	url = '/DCc5Nyr336hUKo5loqWk'+token
	def Blob(i):
		blob = blobstore.BlobInfo.all().order('-creation')[i]
		def size():
			bytes = blob.size
			values = ['Bytes','Kb','Mb','Gb']
			for i in range(len(values)):
				if bytes >= pow(1024,i) and bytes < pow(1024,i+1):
					return str(round(float(bytes)/pow(1024,i),1))+' %s' % values[i]
			return '0 Bytes' if bytes == 0 else (str(round(bytes/pow(1024,len(values)-1),1))+' %s' % values[:-1])
		blob.stats = dict(
			size=size(),
			creation=(blob.creation+EST.timedelta).strftime("%B %d, %Y, %I:%M %p"),
			content=blob.open().read(),
			id=i,
			post='%s&d=%s' % (url, str(blob.key()))
		)
		return blob
	return [Blob(i) for i in range(blobstore.BlobInfo.all().order('-creation').count())]
# webapp2 handlers
class AutomatedBackup(webapp2.RequestHandler):
	def get(self):
		logging.info('Backup sequence initiated.')
		if self.request.headers.get('X-Appengine-Cron') == None:
			logging.warning('Illegal Request: X-Appengine-Cron header not found; access forbidden.')
			self.error(403)
		else:
			logging.info('Cron Job Ligitimacy Verified: requesting access to %s/HFrUAGfXSalEo0hSeeEq now' % data['database'])
			build()
	def post(self):
		self.error(403)
class RequestedBackup(webapp2.RequestHandler):
	def get(self,page):
		self.response.out.write('Backing up, please wait...')
		logging.info('Backup request recieved: verifying ligitimacy.')
		if validateRequest(self.request,page):
			logging.info('Backup Request Ligitimacy Verified: requesting access to %s/HFrUAGfXSalEo0hSeeEq now.' % data['database'])
			message = build()
			self.redirect('/?m=%s' % message)
		else:
			logging.warning('Illegal Request: invalid access token; access forbidden.')
			self.error(403)
	def post(self):
		self.error(403)
class DatestoreCleanup(webapp2.RequestHandler):
	def get(self):
		logging.info('Hourly token screening initiated.')
		if self.request.headers.get('X-Appengine-Cron') == None:
			logging.warning('Illegal Request: X-Appengine-Cron header not found; access forbidden.')
			self.error(403)
		else:
			logging.info('Cron Job Ligitimacy Verified: cleaning up now')
			cleanup()
			logging.info('Cleanup Complete')
class RestoreRequest(webapp2.RequestHandler):
	def get(self,page):
		logging.info('Restore Request Recieved: verifying ligitimacy.')
		if validateRequest(self.request,page):
			logging.info('Restore Request Ligitimacy Verified: accessing %s now.' % data['database'])
			token = requestToken()
			self.redirect(str(data['database']+'/iSJpvIINXZ3cxLYeM3z8?q=%s&k=%s' % (token, self.request.get('d'))))
		else:
			logging.warning('Illegal Request: invalid access token; access forbidden.')
			self.error(403)
	def post(self):
		self.error(403)
class AccessBackup(webapp2.RequestHandler):
	def get(self,page):
		logging.info('Blob Access Request Recieved: verifying ligitimacy.')
		if validateRequest(self.request,page):
			logging.info('Blob Access Request Ligitimacy Verified')
			self.response.out.write(blobstore.BlobInfo.get(self.request.get('d')).open().read())
		else:
			logging.warning('Illegal Request: invalid access token; access forbidden.')
			self.error(403)
	def post(self):
		self.error(403)
def WSGIApplication(routes,debug=False):
	if data == None:
		raise Exception("database reference must be set")
	else:
		if not 'database' in data:
			raise Exception("database reference must be set")
	return webapp2.WSGIApplication([('/kl6imvteNJh4fh9PfXSB', AutomatedBackup),('/Tshk25zecErcQ5IAC9Az/(.*)', RequestedBackup),('/G5Pjss5Rf6ovRN70VJy6', DatestoreCleanup),('/DCc5Nyr336hUKo5loqWk/(.*)', RestoreRequest),('/VBVQCflHOBX0Pixz2pFo/(.*)', AccessBackup)]+routes,debug=debug)