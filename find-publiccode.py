
import requests
import logging
import time
import yaml
import json
import pathlib
import os.path
import os
import re
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

for pageNr in range(1, 34):

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
  logging.info(len(repositoryUrls))

  repositoryList = repositoryList + repositoryUrls



logging.info("DONE")
logging.debug(repositoryList)


# download all publiccode.yml files
nr = 0
repo_lookup = {}
for repo in repositoryList:
  nr = nr + 1
  url = 'https://raw.githubusercontent.com{}'.format(repo.replace('/blob',''))
  m = re.search('^/([^/]+/[^/]+)/', repo)
  reponame = m.group(1)
  filename = 'yamls/' + reponame.replace('/', '-')
  repo_lookup[filename] = url
  if os.path.isfile(filename):
    logging.info("%s OK %s", nr, filename)
  else:
    logging.info('%s reading %s <- %s', nr, filename, url)
    req = requests.get(url)
    open(filename, 'wb').write(req.content)
    time.sleep(20)


logging.info("YO")









# helper function to extract nested value of array

def kk(d, n):
  return d[n] if n in d else ""

def k_extract(target_dict, k_dict):
  response = {}
  for key, value in k_dict.items():
    node_value = ''
    try:
      keys = value.split('-')
      if len(keys) == 4:
        node_value = target_dict[keys[0]][keys[1]][keys[2]][keys[3]]
      elif len(keys) == 3:
        node_value = target_dict[keys[0]][keys[1]][keys[2]]
      elif len(keys) == 2:
        node_value = target_dict[keys[0]][keys[1]]
      elif len(keys) == 1:
        node_value = target_dict[keys[0]]
      else:
        raise Exception("get_nested_json_value() not implemented for {} keys in: {}".format(len(keys), keys))

    except (TypeError, KeyError, IndexError):
        logging.warn("Did not find key %s", value)

    response[key] = node_value
  return response



# read and parse all publiccode.yml files

notValid = []
flist = []
for p in pathlib.Path('yamls/').iterdir():
  if p.is_file():
    with open(p, "r") as stream:
      try:
        data = yaml.safe_load(stream)
        data['src'] = repo_lookup[str(p)] if str(p) in repo_lookup else "*unknown*"
        entry = k_extract(data, {
          'v': 'publiccodeYmlVersion',
          'date': 'releaseDate',
          'stat': 'developmentStatus',
          'name': 'name',
          'cat': 'categories',
          'lang': 'localisation-availableLanguages',
          'type': 'softwareType',
          'l': 'legal-license',
          'p': 'platforms',
          'mnt': 'maintenance-type',
          'url': 'url',
          'src': 'src'
          }
        )

        logging.debug(entry)
        if not "name" in entry:
          logging.error('Repo is missing name: %s', p)
        flist.append(entry)

      except (yaml.YAMLError, TypeError) as exc:
        logging.error("yaml file is broken: %s - %e", p, exc)
        notValid.append({
          'name': str(p).replace('yamls/',''),
          'src': repo_lookup[str(p)] if str(p) in repo_lookup else "*unknown*",
          'error': str(exc)
          })



with open('public/public-code-list.json', 'w') as outfile:
  json.dump(flist, outfile, default=str)

with open('public/public-code-invalid.json', 'w') as outfile:
  json.dump(notValid, outfile, default=str)

logging.debug(flist)


