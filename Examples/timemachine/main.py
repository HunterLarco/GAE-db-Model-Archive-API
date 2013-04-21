import webapp2
import os
from google.appengine.ext.webapp import template
from lib.archive import timemachine
from google.appengine.api import users

# handlers
class MainHandler(webapp2.RequestHandler):
	def get(self,random):
		cu = users.get_current_user()
		if not cu or cu == None:
			self.redirect(users.create_login_url("/"))
		else:
			if isAdmin(cu.email()):
				token = timemachine.requestToken()
				template_values = {
					'logout':users.create_logout_url("/"),
					'stats':timemachine.stats(),
					'url':'/Tshk25zecErcQ5IAC9Az'+token,
					'backups':timemachine.fetch(token),
					'message':self.request.get('m')
				}
				path = os.path.join(os.path.dirname(__file__), 'templates/main.html')
				self.response.out.write(template.render(path, template_values))
			else:
				self.abort(403)

# definitions
def isAdmin(email):
	path = os.path.join(os.path.dirname(__file__), 'lib/permissions.dat')
	permissions = eval(open(path,'r').read())
	return True if email in permissions['admins'] else False
		
timemachine.data = dict(database='http://database.appspot.com')
app = timemachine.WSGIApplication([('/(.*)', MainHandler)],debug=True)

# error handlers
def handle_403(request, response, exception):
	logging.exception(exception)
	template_values = {
		'logout':users.create_logout_url(users.create_login_url("/"))
	}
	path = os.path.join(os.path.dirname(__file__), 'templates/403.html')
	response.out.write(template.render(path, template_values))
app.error_handlers[403] = handle_403