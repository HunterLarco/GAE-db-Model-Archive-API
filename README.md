Archive API
========

### Summary ###
The purpose of the Archive API is to create a seamless, easy to use, automated backup system for the Google App Engine datastore. Originally created for [The Acton-Boxborough Regional High School Community Service Website](http://abrhscs.appspot.com) (ABRHSCS), the API has been used since.

**Note:** the function `restore` in [database.py](./Scripts/Archive API/database.py) is static and must be changed to apply to each individual datastore it is backing up. Also note that the provided timemachine example is operational.

### Setting Up The API ###
Two websites are maintained under the Archive API: the targeted website which provides the database to backup and the remote backup drive. The backup drive will back up the other's database every day and may restore that database from any backup at any time. Thus each is configured differently as instructed below.

### The Target Database ###
Setup for the database is easy. Construct the website as you normally would using the `webapp2` module. However, in place of the `webapp.WSGIApplication` use the `database.WSGIApplication` as shown:

```python
from archive import database
database.data = dict(
	backupdrive = 'http://mydrive.com',
	model = &lt;database here&gt;
)
app = database.WSGIApplication([('/(.*)', MainHandler)],debug=True)
```

The app variable is just an instance of the `webapp.WSGIApplication` with database backup handlers added. The `database.data` dictionary contains two values: backupdrive and model. The backup drive is the url of your other website where the database will be backed up. The model is the `db.model` instance you will be backing up.

That is all that is needed, now onto the actual remote drive.

### The Remote Drive ###
Again setup the website as needed with `webapp.WSGIApplication`. This time however it needs to be defined as the backup drive. This is done as so:

```python
from archive import timemachine
timemachine.data = dict(
	database = 'http://mydatabase.com',
)
app = timemachine.WSGIApplication([('/(.*)', MainHandler)],debug=True)
```

**Note:** do not forget to also include the [cron.yaml](./Scripts/Archive API/cron.yaml) file in the root of your remote drive application, otherwise it will not automatically backup.

### Methods ###
All the methods are contained within the timemachine and are only used from the remote drive
* `requestToken()` is used to obtain one-use access tokens that give permission to either force a backup or restore from a backup.
```python
# for example, this obtains a url for forcing a backup
backupURL = '/Tshk25zecErcQ5IAC9Az'+timemachine.requestToken()
```
* `stats()` returns a dictionary of the number of backups, the total size of the backups, the time of the last backup, and the time of the next scheduled backup.
```python
# example usage
stats = timemachine.stats()
number = stats.num
last = stats.last
next = stats.next
size = stats.size
```
* `fetch(token)` returns a list of all the backups, each one with a stats key which contains the size, creation time, content, and restoration url. Keep in mind that each entity in the list is also an instance of the Blobstore.
```python
# example usage
for item in timemachine.fetch(timemachine.requestToken()):
	size = item.stats.size
	creation = item.stats.creation
	content = item.stats.content
	restoreURL = item.stats.post
```

**Note:** additional methods exist but are used by the cron jobs and don't require any use from the app.

### Change Log ###
2013 3 8
* First stable release
