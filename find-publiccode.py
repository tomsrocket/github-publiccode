
import requests
import logging
import time
import os.path
import os
import re
import sys
from datetime import datetime
import subprocess
import sqlite3
import http.cookiejar as cookielib



logging.basicConfig(level=logging.INFO, format='<%(asctime)s %(levelname)s> %(message)s')
logging.info("START")


def get_cookies(cj, ff_cookies):
  con = sqlite3.connect(ff_cookies)
  cur = con.cursor()
  cur.execute("SELECT host, path, isSecure, expiry, name, value FROM moz_cookies")
  for item in cur.fetchall():
    c = cookielib.Cookie(0, item[4], item[5],
      None, False,
      item[0], item[0].startswith('.'), item[0].startswith('.'),
      item[1], False,
      item[2],
      item[3], item[3]=="",
      None, None, {})
    logging.debug("cookie %s", c)
    cj.set_cookie(c)


#
# use firefox cookies for github

# copy cookies sqlite file (otherwise it will be "file locked" error)
cookiePath = 'firefox.sqlite'
if not os.path.isfile(cookiePath):
  batcmd='find ~/.mozilla/firefox/  -name "cookies.sqlite"'
  firefoxPath = subprocess.check_output(batcmd, shell=True, text=True).strip()
  logging.info("cookiepath: %s", firefoxPath)
  copyCookie = subprocess.check_output(["cp",firefoxPath, cookiePath])
  logging.info("copied cookies: %s", copyCookie)

# read github cookies
cj = cookielib.CookieJar()
get_cookies(cj, cookiePath)
s = requests.Session()
s.cookies = cj




# get all result pages

repositoryList = []

for pageNr in range(1, 33):

  filename = "htmls/resultpage{}.html".format(pageNr)
  filecontent = ''

  if os.path.isfile(filename):
    logging.info("%s - using cache", filename)
    with open(filename) as myfile:
      filecontent ="".join(line.rstrip() for line in myfile)

  else:
    logging.info("%s - HTTP GET", filename)
    url = 'https://github.com/search?o=desc&p={}&q=+filename%3Apubliccode.yml+path%3A%2F&s=indexed&type=Code'.format(pageNr)
    req = s.get(url)
    open(filename, 'wb').write(req.content)
    filecontent = req.text
    # will github ban you if you do too many automated search requests via frontend..??
    # so lets wait! who cares how long this takes
    time.sleep(20)

  if not filecontent:
    logging.error('EMPTY RESULT')
    raise SystemExit

  repositoryUrls = re.findall( r'<a\s+href="([^"]+/publiccode.yml)"', filecontent)
  logging.info(repositoryUrls)

  repositoryList = repositoryList + repositoryUrls



logging.info("DONE")
logging.info(repositoryList)


# download all publiccode.yml files

for repo in repositoryList:
  url = 'https://raw.githubusercontent.com{}'.format(repo.replace('/blob',''))
  m = re.search('^/([^/]+/[^/]+)/', repo)
  reponame = m.group(1)
  filename = 'yamls/' + reponame.replace('/', '-')
  if os.path.isfile(filename):
    logging.info("OK %s", filename)
  else:
    logging.info('reading %s <- %s', filename, url)
    req = requests.get(url)
    open(filename, 'wb').write(req.content)
    time.sleep(20)
