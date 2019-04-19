import time

from xml.dom.minidom import parseString

import requests
import praw
import redis

redis_host = "localhost"
redis_port = 6379
redis_password = ""

r = redis.StrictRedis(host=redis_host, port=redis_port, password=redis_password, decode_responses=True)

def getText(nodelist):
    rc = ""
    for node in nodelist:
        if node.nodeType == node.TEXT_NODE:
            rc = rc + node.data
    return rc

def proceed(reddit, title, link, flair):
    submited = reddit.subreddit("MetapolisFreeland").submit(title, url=link, resubmit=False, send_replies=False)
    try:
        choices = submited.flair.choices()
        template_id = next(x for x in choices if x['flair_text_editable'])['flair_template_id']
        submited.flair.select(template_id, flair)
    except:
        pass

def try_retry():
    # Note that twitrss is broken and it might take more than one request to return back a valid response sometimes
    try:
        req = requests.get("https://twitrss.me/twitter_user_to_rss/?user=%40MfCoin")
        parsed = parseString(req.text)
        item = parsed.getElementsByTagName("item")
        flair = "Metapolis Twitter"
        title = item[0].getElementsByTagName("title")[0]
        title_raw = getText(title.childNodes)
        if "http" in title_raw:
            title_raw = title_raw.split("http")[0]
        link = item[0].getElementsByTagName("link")[0]
        return flair, title_raw, link
    except:
        time.sleep(10)
        try_retry()

flair, title_raw, link = try_retry()

reddit = praw.Reddit("bot1")
extract = r.get("freeland_twitter")
if extract == None:
    proceed(reddit, title_raw, getText(link.childNodes), flair)
    r.set("freeland_twitter", title_raw)
else:
    if extract != title_raw:
        proceed(reddit, title_raw, getText(link.childNodes), flair)
        r.delete("freeland_twitter")
        r.set("freeland_twitter", title_raw)