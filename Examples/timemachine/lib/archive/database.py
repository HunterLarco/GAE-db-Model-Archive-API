# generic imports for all methods
from google.appengine.ext import db
import simplr
import webapp2
import logging
# methods
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
def populate(namespace):
	import json
	backup = {
		'backup':[db.to_dict(u) for u in namespace.all()]
	}
	return json.dumps(backup)
def restore(namespace,backup):
	import json
	backup = json.loads(backup)
	db.delete(namespace.all(keys_only=True))
	for item in backup['backup']:
		nu = namespace()
		nu.json = item['json']
		nu.email = item['email']
		nu.put()
		data = None
# webapp handlers
class BackupRequest(webapp2.RequestHandler):
	def get(self):
		import simplr
		logging.info('Backup Request Detected: verifying legitimacy.')
		if simplr.valid(self.request.get('dt')):
			logging.info('Backup Request Allowed: feeding data.')
			self.response.headers['Content-Type'] = "text/javascript"
			self.response.out.write(populate(data['model']))
		else:
			logging.warning('Illegal Backup Request: invalid access token; access forbidden.')
			self.error(403)
	def post(self):
		self.error(403)
class RestoreRequest(webapp2.RequestHandler):
	def get(self):
		import urllib2
		logging.info('Restore Request Detected: verifying legitimacy.')
		url = data['backupdrive']+'/VBVQCflHOBX0Pixz2pFo%s&d=%s' % (self.request.get('q'), self.request.get('k'))
		logging.info('Restore Request Allowed: requesting data from %s now.' % url)
		try:
			backup = urllib2.urlopen(url).read()
			logging.info('Restoration File Successfully Read: reseting the datastore')
			restore(data['model'],backup)
			logging.info('Restoration Successful')
			self.redirect(data['backupdrive']+'/?m=Restoration Successful')
		except Exception as error:
			logging.error(error)
			self.error(403)
	def post(self):
		self.error(403)
def WSGIApplication(routes,debug=False):
	if data == None:
		raise Exception("backupdrive and model references must be set")
	else:
		if not 'backupdrive' in data or not 'model' in data:
			raise Exception("backupdrive and model references must be set")
	return webapp2.WSGIApplication([('/HFrUAGfXSalEo0hSeeEq',BackupRequest),('/iSJpvIINXZ3cxLYeM3z8',RestoreRequest)]+routes,debug=debug)