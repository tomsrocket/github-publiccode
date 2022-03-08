
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
from datetime import datetime, timedelta

# check this page - you should add github client id and secret to the config
# https://docs.github.com/rest/overview/resources-in-the-rest-api#rate-limiting
import config


TODAY = datetime.now()

GITHUB_SEARCHRESULT_URL_TEMPLATE = 'https://github.com/search?o=desc&p={}&q=+filename%3Apubliccode.yml+path%3A%2F&s=indexed&type=Code'




# Init logging with colorized error messages on the command line
logging.basicConfig(level=logging.INFO, format='<%(asctime)s %(levelname)s> %(message)s')
logging.addLevelName( logging.WARNING, "\033[1;31m%s\033[1;0m" % logging.getLevelName(logging.WARNING))
logging.addLevelName( logging.ERROR, "\033[1;41m%s\033[1;0m" % logging.getLevelName(logging.ERROR))
logging.info("START")

# Helper functions to extract nested values of an array in a "failsafe" way
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
        logging.log(logging.DEBUG if value == 'logo' else logging.WARNING, "Did not find key %s", value)

    response[key] = node_value
  return response


#
# Helper functions to acces firefox cookies (otherwise the github search won't work)
#
def readFirefoxCookiesSqlite(cj, ff_cookies):
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


def getFirefoxCookies():
  # copy cookies sqlite file (otherwise it will be "file locked" error)
  cookiePath = 'firefox.sqlite'
  if not os.path.isfile(cookiePath):
    batcmd='find ~/.mozilla/firefox/  -name "cookies.sqlite"'
    firefoxPath = subprocess.check_output(batcmd, shell=True, text=True).strip()
    logging.info("cookiepath: %s", firefoxPath)
    copyCookie = subprocess.check_output(["cp",firefoxPath, cookiePath])
    logging.info("copied cookies: %s", copyCookie)

  # read all firefox cookies
  cj = cookielib.CookieJar()
  readFirefoxCookiesSqlite(cj, cookiePath)
  return cj



def getListOfGithubReposWithPubliccodeYml(s):

  # start with some known repositories
  repositoryList = [
    '/mpfiesole/mpfiesole/5cdb57572d4df224532c26433d4d881490fce42f/publiccode.yml',
    '/aziendazero/ecm/57fd6fba8ead03db016395269e3f2dd1b998d42b/publiccode.yml',
    '/CodeForBaltimore/Healthcare-Rollcall/0ceb4067444c71674d1af97e2022975e83cc9c92/publiccode.yml',
    '/CodeForBaltimore/ProjectTemplate/c2206173b56e8466aa18dc7a108438faa8b673ea/publiccode.yml'
    '/regione-marche/e-procurement-WSGene/e46bfd82681e3b7adfc5afcddbd27ef86df3e8b7/publiccode.yml',
    '/regione-marche/e-procurement-appalti-rest/92970ba0e25c760911bf139eed4e1d4093d00a4d/publiccode.yml',
    '/regione-marche/e-procurement-BANDEU/74b3e47c5e2999925e5c4def4d10a5b3c852ecd9/publiccode.yml',
    '/regione-marche/e-procurement-WSCompositore/4acf452b5033a1db5ad3ba253e02c66bc7d2cdba/publiccode.yml',
    '/kokorin/Jaffree/master/publiccode.yml',
    '/Azienda-USL-di-Bologna/babel/master/publiccode.yml',
    '/ESTAR2021/LOGICAR/main/publiccode.yml',
    '/r3vit/publiccode.yml-validator/master/publiccode.yml'
  ]

  # scrape search result pages from github frontend
  for pageNr in range(1, 35):
    filename = "htmls/resultpage{}.html".format(pageNr)
    filecontent = ''

    if os.path.isfile(filename):
      logging.debug("%s - using cache", filename)
      with open(filename) as myfile:
        filecontent ="".join(line.rstrip() for line in myfile)

    else:
      logging.info("%s - HTTP GET", filename)
      url = GITHUB_SEARCHRESULT_URL_TEMPLATE.format(pageNr)
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

  return repositoryList



def downloadPubliccodeYmls(repositoryList):
  # download all publiccode.yml files to "yamls/" directory
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
  return repo_lookup


def readGithubApiContent(basefilename, url):
  # read and parse github api json
  # and cache it to a public file (for later use via clientside javascript)
  directory = 'public/details/'
  filename = directory + basefilename
  filecontent = "{}"

  if os.path.isfile(filename):
    logging.debug("%s - using cache", filename)
    with open(filename) as myfile:
      filecontent = "".join(line.rstrip() for line in myfile)
      data = json.loads(filecontent)

  else:
    logging.info("%s - HTTP GET", filename)

    req = requests.get(url, auth=(config.github_client_id, config.github_client_secret))
    open(filename, 'wb').write(req.content)
    filecontent = req.text
    time.sleep(2)

    data = json.loads(filecontent)
    if isinstance(data, list):
      if data and not ("id" in data[0]):
        logging.error("UNWANTED GITHUB RESPONSE: %s", filename)
        logging.error("maybe rate limit exceeded? %s", filecontent)
        raise SystemExit

    elif not ("id" in data):
      logging.error("UNWANTED GITHUB RESPONSE: %s", filename)
      logging.error("maybe rate limit exceeded? %s", filecontent)
      raise SystemExit

  return data


def getGithubApiInformation(s, reponame):

  ghData = {}
  if reponame:

    # load basic github stats
    filename = reponame.replace('/', '-') + ".json"
    url = 'https://api.github.com/repos/{}'.format(reponame)
    data = readGithubApiContent(filename, url)

    ghData = k_extract(data, {
      'd2': 'description',
      's': 'size',
      'w': 'watchers_count',
      'f': 'forks_count',
      'l': 'language',
      'f': 'fork',
      'pa': 'pushed_at',
      'av': 'owner-avatar_url'
      }
    )
    ghData["pa"] = abs((TODAY - datetime.strptime(str(ghData["pa"][0:10]), "%Y-%m-%d")).days)


    # load contributor data
    filename = reponame.replace('/', '-') + "-contributors.json"
    url = 'https://api.github.com/repos/{}/contributors'.format(reponame)
    contributors = readGithubApiContent(filename, url)
    c10 = c100 = c1000 = 0
    contributions = 0
    for contributor in contributors:
      contributions = contributions + contributor["contributions"]
      if contributor["contributions"]<10:
        c10 = c10 + 1
      elif contributor["contributions"]<100:
        c100 = c100 + 1
      else:
        c1000 = c1000 + 1
    ghData.update({
      'c': c10+c100+c1000,
      'cn': '{}/{}/{}'.format(c1000,c100,c10),
      'cb': contributions
    })

  else:
    logging.warning("EMPTY REPO NAME?")

  return ghData

  """
  content of github repo info
  ===========================

  size	201875
  stargazers_count	25
  watchers_count	25
  forks_count	16
  language	"TypeScript"
  has_pages	false
  fork	false
  open_issues_count	43
  license
    key
    name
  default_branch	"master"
  network_count	16
  topics
    0	"burndown"
    1	"git"
    2	"git-analysis"
    3	"machine-learning"
  subscribers_count	7
  created_at	"2019-04-14T13:56:20Z"
  updated_at	"2022-02-03T11:09:34Z"
  pushed_at	"2022-03-02T14:51:58Z"
  owner
    login	"ikuseiGmbH"
    avatar_url	"https://avatars.githubusercontent.com/u/661953?v=4"
    gravatar_id	""
    type	"Organization"

  """


def getCalculatedRating(entry):
  overallRating = 0

  # number of stars
  rating = 0
  if 'w' in entry:
    stars = entry['w']
    if stars>=10000:
      rating = 5
    elif stars>=1000:
      rating = 4
    elif stars>=100:
      rating = 3
    elif stars>=10:
      rating = 2
    else:
      rating = 1
  overallRating = overallRating + rating*1000

  # days since last commit
  rating = 0
  if 'pa' in entry:
    daysSinceLastPush = entry['pa']
    if daysSinceLastPush>=500:
      rating = 1
    elif daysSinceLastPush>=200:
      rating = 2
    elif daysSinceLastPush>=100:
      rating = 3
    elif daysSinceLastPush>=30:
      rating = 4
    else:
      rating = 5
  overallRating = overallRating + rating*100

  # number of contributions
  rating = 0
  if 'cb' in entry:
    contributions = entry['cb']
    if contributions>=10000:
      rating = 5
    elif contributions>=1000:
      rating = 4
    elif contributions>=100:
      rating = 3
    elif contributions>=10:
      rating = 2
    else:
      rating = 1
  overallRating = overallRating + rating*10

  # number of contributors
  rating = 0
  if 'c' in entry:
    contributors = entry['c']
    if contributors>=50:
      rating = 5
    elif contributors>=20:
      rating = 4
    elif contributors>=10:
      rating = 3
    elif contributors>=5:
      rating = 2
    else:
      rating = 1
  overallRating = overallRating + rating

  return str(overallRating)


def extractSummaryInformationForAllPubliccodeYmls(session, repo_lookup):
  # read and parse all publiccode.yml files
  notValid = []
  flist = []
  for p in pathlib.Path('yamls/').iterdir():
    if p.is_file():
      with open(p, "r") as stream:
        try:
          data = yaml.safe_load(stream)
          if not isinstance(data, dict):
            raise ValueError('YAML not of type "dictionary": {}'.format(data))

          data['src'] = repo_lookup[str(p)] if str(p) in repo_lookup else "*unknown*"

          # list of the publiccode-data that we collect
          entry = k_extract(data, {
            'v': 'publiccodeYmlVersion',
            'date': 'releaseDate',
            'stat': 'developmentStatus',
            'n': 'name',
            'cat': 'categories',
            'lang': 'localisation-availableLanguages',
            'type': 'softwareType',
            'lgl': 'legal-license',
            'p': 'platforms',
            'mnt': 'maintenance-type',
            'url': 'url',
            'src': 'src',
            'l': 'logo'
            }
          )

          # separate organisation name and repository name
          m = re.search('^https://[^/]+/([^/]+/[^/]+)/', data['src'])
          reponame = m.group(1) if m else ""
          if reponame:
            (rOrg, rName) = reponame.split("/")
            entry['r'] = rName
            entry['rg'] = rOrg

          # fix relative logo urls
          if entry["l"] and not entry["l"].startswith("http"):
            entry["l"] = 'https://raw.githubusercontent.com/{}/master/{}'.format(reponame, entry["l"])

          # get any "shortDescription" from publiccode.yml, prioritize english
          if "description" in data:
            if "en" in data["description"]:
              desc = data["description"]["en"]
              lang = "🇬🇧"
            elif isinstance(data["description"], dict):
              lang, desc = next(iter( data["description"].items() ))
              lang = "🇮🇹" if lang == "it" else "({})".format(lang)
            desc = desc["shortDescription"] if "shortDescription" in desc else ""
            entry["d"] = lang + " " + desc

          gh = getGithubApiInformation(session, reponame)
          entry.update(gh)
          entry['rt'] = getCalculatedRating(entry)

          logging.debug(entry)
          if not "n" in entry:
            logging.error('Repo is missing name: %s', p)
          flist.append(entry)

        except (ValueError, yaml.YAMLError, TypeError) as exc:
          logging.error("yaml file is broken: %s - %s", p, exc)
          notValid.append({
            'name': str(p).replace('yamls/',''),
            'src': repo_lookup[str(p)] if str(p) in repo_lookup else "*unknown*",
            'error': str(exc)
            })

  # write two lists:
  # 1. summary information from all the publiccode.ymls
  with open('public/public-code-list.json', 'w') as outfile:
    json.dump(flist, outfile, default=str)

  # 2. list of invalid publiccode.ymls
  with open('public/public-code-invalid.json', 'w') as outfile:
    json.dump(notValid, outfile, default=str)

  logging.debug(flist)



def main():
  session = requests.Session()
  session.cookies = getFirefoxCookies()

  repositoryList = getListOfGithubReposWithPubliccodeYml(session)

  logging.info("DONE")
  logging.debug(repositoryList)

  repositoryNames = downloadPubliccodeYmls(repositoryList)

  extractSummaryInformationForAllPubliccodeYmls(session, repositoryNames)

main()

logging.info("ALL DONE!")


