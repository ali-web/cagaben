import re
import html2text
import urllib2
from bs4 import BeautifulSoup
import requests
#for nyt
from cookielib import CookieJar

#cnn - zn-body__paragraph
#cnn - zn-body__paragraph
#fox - article-text
#nyt - story-body-text story-content
#gma - itemprop=articleBody



def scrapeContent(url, agency):

    config = {
        'cnn': {
            'attr_key': '_class',
            'attr_val': 'zn-body__paragraph',
            'cookie': False
        },
        'foxnews': {
            'attr_key': '_class',
            'attr_val': '',
            'cookie': False,
            'tag': 'p',
            'parent': {
                'attr_key': 'itemprop',
                'attr_val': 'articleBody',
            }
        },
        'nytimes': {
            'attr_key': '_class',
            'attr_val': 'story-body-text story-content',
            'cookie': True
        },
        'gma': {
            'attr_key': 'itemprop',
            'attr_val': 'articleBody',
            'cookie': False
        },
        'usatoday': {
            'attr_key': '_class',
            'attr_val': '',
            'cookie': False,
            'tag': 'p',
            'parent': {
                'attr_key': 'itemprop',
                'attr_val': 'articleBody',
            }
        },
        'latimes': {
            'attr_key': '_class',
            'attr_val': '',
            'cookie': False,
            'tag': 'p',
            'parent': {
                'attr_key': 'itemprop',
                'attr_val': 'articleBody',
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

    html = ''
    title = soup.find_all('h1')
    title = title[0].renderContents()
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

    for par in parent:
        #print par;exit()
        # container = par.find_all(**attributes)
        # html += str(container)
        elements = par.find_all(**attributes)
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







url = "http://www.cnn.com/2016/02/09/politics/new-hampshire-primary-highlights/index.html" #cnn
#url = "http://fxn.ws/1KaghNi" #foxnews
#url = "http://www.nytimes.com/2016/02/10/us/politics/supreme-court-blocks-obama-epa-coal-emissions-regulations.html" #nytimes
#url = 'http://abcn.ws/1ITCsGU' #gma
#url = 'http://usat.ly/1PID3L3' #usatoday
#url = "http://lat.ms/1OMb26s" #latimes

title, article = scrapeContent(url, 'cnn')

print article
