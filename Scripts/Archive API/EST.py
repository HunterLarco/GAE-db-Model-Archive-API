##### used to get EST time #####
##### imports ##### 
import datetime
##### time zone handlers #####
class UtcTzinfo(datetime.tzinfo):
  def utcoffset(self, dt): return datetime.timedelta(0)
  def dst(self, dt): return datetime.timedelta(0)
  def tzname(self, dt): return 'UTC'
  def olsen_name(self): return 'UTC'
class EstTzinfo(datetime.tzinfo):
  def utcoffset(self, dt): return datetime.timedelta(hours=-4)
  def dst(self, dt): return datetime.timedelta(hours=-1)
  def tzname(self, dt): return 'EST+04EDT'
  def olsen_name(self): return 'US/Eastern'
TZINFOS = {
  'utc': UtcTzinfo(),
  'est': EstTzinfo()
}
##### methods ##### 
# now
now = datetime.datetime.now()
now = now.replace(tzinfo=TZINFOS['utc'])
now = now.astimezone(TZINFOS['est'])
# midnight
midnight = datetime.datetime.now()
midnight = now.replace(tzinfo=TZINFOS['utc'])
midnight = now.astimezone(TZINFOS['est'])
midnight = datetime.datetime.combine(midnight.date(), datetime.time(0))+datetime.timedelta(1)
# midnightdelta
midnightdelta = midnight.replace(tzinfo=None)-now.replace(tzinfo=None)
# timedelta
timedelta = now.utcoffset()