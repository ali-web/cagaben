import re
import html2text
import urllib2
from bs4 import BeautifulSoup
import requests
#for nyt
from cookielib import CookieJar
import socket
from pymongo import MongoClient

#cnn - zn-body__paragraph
#cnn - zn-body__paragraph
#fox - article-text
#nyt - story-body-text story-content
#gma - itemprop=articleBody



def pageExists(url):

    cj = CookieJar()
    opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cj))


    # page = requests.get(url)
    # print page.content
    # exit()


    hdr = {'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.11 (KHTML, like Gecko) Chrome/23.0.1271.64 Safari/537.11',
           'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
           'Accept-Charset': 'ISO-8859-1,utf-8;q=0.7,*;q=0.3',
           'Accept-Encoding': 'none',
           'Accept-Language': 'en-US,en;q=0.8',
           'Connection': 'keep-alive'}

    req = urllib2.Request(url, headers=hdr)

    try:
        a = urllib2.urlopen(req, timeout=1)
    except urllib2.HTTPError, err:
        return err.code
    except:
        return None
    # except socket.timeout:
    #     return None
    # except urllib2.URLError:
    #     return None

    return a.getcode()



def scrapeContent(url, agency):

    config = {
        'washtimes': {
            'attr_key': 'class_',
            'attr_val': '',
            'cookie': False,
            'tag': 'p',
            'parent': {
                'attr_key': 'class_',
                'attr_val': 'storyareawrapper',
            }
        },
        'FoxNews': {
            'attr_key': 'class_',
            'attr_val': '',
            'cookie': False,
            'tag': 'p',
            'parent': {
                'attr_key': 'itemprop',
                'attr_val': 'articleBody',
            }
        },
        'NewsHour': {
            'attr_key': 'class_',
            'attr_val': '',
            'cookie': False,
            'tag': 'p',
            'parent': {
                'attr_key': 'class_',
                'attr_val': 'entry-content',
            }
        },
        'cnn': {
            'attr_key': 'class_',
            'attr_val': 'zn-body__paragraph',
            'cookie': False,
            'tag': 'p',
            'parent': {
                'attr_key': 'itemprop',
                'attr_val': 'articleBody',
            }
        },
        'gma': {
            'attr_key': 'itemprop',
            'attr_val': 'articleBody',
            'cookie': False
        },
        'usatoday': {
            'attr_key': 'class_',
            'attr_val': '',
            'cookie': False,
            'tag': 'p',
            'parent': {
                'attr_key': 'itemprop',
                'attr_val': 'articleBody',
            }
        },
        'usnews': {
            'attr_key': 'class_',
            'attr_val': 'MsoNormal',
            'cookie': False,
            'tag': 'p',
            # 'parent': {
            #     'attr_key': '_class',
            #     'attr_val': 'block skin-editable',
            # }
        },
        'latimes': {
            'attr_key': 'class_',
            'attr_val': '',
            'cookie': False,
            'tag': 'p',
            'parent': {
                'attr_key': 'itemprop',
                'attr_val': 'articleBody',
            }
        },
        'CBSNews': {
            'attr_key': 'class_',
            'attr_val': '',
            'cookie': False,
            'tag': 'p',
            'parent': {
                'attr_key': 'itemprop',
                'attr_val': 'articleBody',
            }
        },
        'nytimes': {
            'attr_key': 'class_',
            'attr_val': 'story-body-text story-content',
            'cookie': True
        },
        'washingtonpost': {
            'attr_key': 'class_',
            'attr_val': '',
            'cookie': False,
            'tag': 'p',
            'parent': {
                'attr_key': 'itemprop',
                'attr_val': 'articleBody',
            }
        },
        'wsj': {
            'attr_key': 'class_',
            'attr_val': '',
            'cookie': False,
            'tag': 'p',
            'parent': {
                'attr_key': 'class_',
                'attr_val': 'wsj-snippet-body',
            }
        },
    }

    cj = CookieJar()
    opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cj))


    # page = requests.get(url)
    # print page.content
    # exit()


    hdr = {'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.11 (KHTML, like Gecko) Chrome/23.0.1271.64 Safari/537.11',
           'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
           'Accept-Charset': 'ISO-8859-1,utf-8;q=0.7,*;q=0.3',
           'Accept-Encoding': 'none',
           'Accept-Language': 'en-US,en;q=0.8',
           'Connection': 'keep-alive'}

    req = urllib2.Request(url, headers=hdr)
    #a = urllib2.urlopen(req)
    # print a.getcode()
    # return

    #necessary for cookie setter websites like nyt
    if config[agency]['cookie']:
        soup = BeautifulSoup(opener.open(req), "lxml")
    else:
        soup = BeautifulSoup(urllib2.urlopen(req), "lxml")


    # for row in soup.find_all('section', attrs={"class": "zn-has-46-containers"}):
    #     print row.text

    #print soup
    # for item in soup.findAll("section", {}, True):
    #     if 'zn-has-46-containers' in item.attrs['class']:
    #         print item

    #mydivs = soup.findAll('section', {'class': lambda x: 'zn-has-46-containers' in x.split()})

    #print mydivs


    #print soup.find_all("section", class_="zn-has-46-containers")
    #print soup.find_all("section", class_="zn-has-46-containers", True)


    #print soup; exit()


    #print soup.find_all("div")
    #container = soup.find_all("div", class_="l-container")
    #container = soup.find_all(class_="zn-body__paragraph")
    #container = soup.find_all("div", class_="article-text")
    #container = soup.find_all(class_="story-body-text story-content")

    # print config[agency]["attr_key"]
    # name = "soup.find_all(" + "" + "='articleBody')"
    # container = eval(name)

    #print config[agency]

    #print soup; exit()

    html = ''
    title = soup.find_all('title')
    title = title[0].renderContents() if len(title) > 0 else ''
    #print title; exit()
    #title = html2text.html2text(str(title))


    if 'parent' in config[agency]:
        parent_attributes = {
            config[agency]['parent']['attr_key']: config[agency]['parent']['attr_val']
        }
        parent = soup.find_all(**parent_attributes)
    else:
        parent = soup.find_all('html')

    #print parent; exit()

    attributes = {
        config[agency]['attr_key']: config[agency]['attr_val']
    }

    if 'tag' in config[agency]:
        attributes['name'] = config[agency]['tag']

    #print parent; exit()

    #print len(parent); exit()

    for par in parent:
        #print par;exit()
        # container = par.find_all(**attributes)
        # html += str(container)
        # elements = par.find_all("p", _class="MsoNormal")
        elements = par.find_all(**attributes)
        #print attributes
        #print elements; exit()
        for e in elements:
            html += unicode(e.renderContents(), 'utf-8')



    h = html2text.HTML2Text()
    h.ignore_links = True
    article = h.handle(html)

    # article =  h.handle(html) \
    #     .replace('\n,\n', '').replace('\r,\r', '').replace('\n,', '').replace(',\n', '').replace('\\n', '') \
    #     .strip("[").strip("]")

    return title, article





#1 - washtimes
#url = "http://goo.gl/gr7n9R"
#2 - FoxNews
#url = "http://fxn.ws/1KaghNi"
#3 - NewsHour
#url = "http://to.pbs.org/1O2PG2Q"
#4 - cnn
#url = "http://www.cnn.com/2016/02/09/politics/new-hampshire-primary-highlights/index.html"
#5 - gma
#url = 'http://abcn.ws/1ITCsGU'
#6 - usatoday
#url = 'http://usat.ly/1PID3L3'
#7 - usnews
#url = "http://trib.al/3lutizl"
#8 - latimes
#url = "http://lat.ms/1OMb26s"
#9 - CBSNews
#url = "http://cbsn.ws/11InvLJ"
#10 - nytimes
#url = "http://www.nytimes.com/2016/02/10/us/politics/supreme-court-blocks-obama-epa-coal-emissions-regulations.html" #nytimes
#11 - washingtonpost
#url = "http://wapo.st/1QeLShp"
#11 - wsj - need subscription
#url = "http://on.wsj.com/1SaQMy4"

# title, article = scrapeContent(url, 'washingtonpost')
#
# print title
# print article


# cl = MongoClient()
# storyCollection = cl.cagaben.story
#
#
# stories = storyCollection.find({'source': {'$ne': 'cnn'}})
# for story in stories:
#     print story['link']
#     print story['source']

#print stories


pageExists("http://fxn.ws/1SwRlzC")
# pageExists('http://fxn.ws/1UA3Azi')