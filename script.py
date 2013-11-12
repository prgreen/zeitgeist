# choose the zeitgeist, update it and tweet it
# this script is executed once a day

import redis, tweepy
from datetime import date

consumer_token = "0uZ5qmOCbpo7FFOm5O4OdA"
consumer_secret = "Gir1qikphKcUObNaixMCedyngfa8cZfTzX6FmVLv9U"

key = "1241197884-xHLDF5zpAVcyJFOzKK9JDvKm1LKF65gv08YNeiu"
secret = "GWO9bZ2TY1x0PDppwdOHHJma1CO70COPwzD9Hcawc"

r = redis.StrictRedis(host='localhost', port=6379, db=0)

SENTENCES_KEY = 'zeitgeist:sentences'
ZEITGEIST_KEY = 'zeitgeist:zeitgeist'
DATE_KEY =      'zeitgeist:date'

DATE_TODAY = date.today().isoformat()

sentences = r.zrange(SENTENCES_KEY, 0, 1, desc=True, withscores=True)

zeitgeist = None
try:
    zeitgeist = sentences[0][0]
except:
    pass

if zeitgeist != None: #if there's an available zeitgeist
    print "Zeitgeist: ", zeitgeist

    #TODO save old zeitgeist in a zeitgeist:history list

    #make zeitgeist the new zeitgeist in redis server
    r.set(ZEITGEIST_KEY, zeitgeist)
    r.set(DATE_KEY, DATE_TODAY)
    print "Saved on "+ DATE_TODAY

    #tweet it
    auth = tweepy.OAuthHandler(consumer_token, consumer_secret)

    auth.set_access_token(key, secret)

    api = tweepy.API(auth)
    api.update_status(zeitgeist)

    #remove all current sentences
    r.zremrangebyrank(SENTENCES_KEY, 0, -1)







