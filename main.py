import webapp2, urllib, urllib2, json
import jinja2
import os
import logging
import time, datetime
from google.appengine.api import memcache

JINJA_ENVIRONMENT = jinja2.Environment(loader=jinja2.FileSystemLoader(os.path.dirname(__file__)),
    extensions=['jinja2.ext.autoescape'],
    autoescape=True)

def pretty(obj):
    return json.dumps(obj, sort_keys=True, indent=2)

def safeGet(url):
    try:
        return urllib2.urlopen(url)
    except urllib2.HTTPError, e:
        print "The server couldn't fulfill the request." 
        print "Error code: ", e.code
    except urllib2.URLError, e:
        print "We failed to reach a server"
        print "Reason: ", e.reason
    return None

def properDate(currlist):
    s = currlist[0][6:8] + "-"
    if currlist[0][4:6] == '01':
        s += "Jan"
    elif currlist[0][4:6] == '02':
        s += "Feb"
    elif currlist[0][4:6] == '03':
        s += "Mar"
    elif currlist[0][4:6] == '04':
        s += "Apr"
    elif currlist[0][4:6] == '05':
        s += "May"
    elif currlist[0][4:6] == '06':
        s += "Jun"
    elif currlist[0][4:6] == '07':
        s += "Jul"
    elif currlist[0][4:6] == '08':
        s += "Aug"
    elif currlist[0][4:6] == '09':
        s += "Sep"
    elif currlist[0][4:6] == '10':
        s += "Oct"
    elif currlist[0][4:6] == '11':
        s += "Nov"
    elif currlist[0][4:6] == '12':
        s += "Dec"
    s += "-" + currlist[0][2:4]
    #print s
    currlist[0] = s
    dic = {"Date":currlist[0], "Open":currlist[1], "High":currlist[2], "Low":currlist[3], "Close":currlist[4], "Volume":currlist[5]}
    return dic

#properDate('AAPL.txt')

def pullData(stock):
    try:
        print 'Currently pulling', stock
        print str(datetime.datetime.fromtimestamp(time.time()).strftime('%Y-%m-%d %H:%M:%S'))
        urlToVisit = 'http://chartapi.finance.yahoo.com/instrument/1.0/'+stock+'/chartdata;type=quote;range=1y/csv'
        dataMatrix = []
        print urlToVisit
    
        sourceCode = urllib2.urlopen(urlToVisit).read()
        splitSource = sourceCode.split('\n')
        for eachLine in splitSource:
            sortedKeyValue = eachLine.split(":")
            if sortedKeyValue[0] == "errorid":
                return None
        for eachLine in splitSource: 
            if 'values' not in eachLine:
                splitLine = eachLine.split(',')
                if len(splitLine)==6:
                    words = eachLine.split(',')
                    dicOfWords = properDate(words)
                    dataMatrix.append(dicOfWords)
        #print dataMatrix
        #logging.info(dataMatrix==None)

        return dataMatrix
    except Exception, e:
        print 'main loop', str(e)

#pullData('AAPL')

def pullTableContent(stock):
    try:
        print 'Currently pulling', stock
        print str(datetime.datetime.fromtimestamp(time.time()).strftime('%Y-%m-%d %H:%M:%S'))
        urlToVisit = 'http://chartapi.finance.yahoo.com/instrument/1.0/'+stock+'/chartdata;type=quote;range=1y/csv'
        tableData = {}
        sourceCode = urllib2.urlopen(urlToVisit).read()
        splitSource = sourceCode.split('\n')
        for i in range(18):
            keyVal = splitSource[i].split(':')
            tableData[keyVal[0]] = keyVal[1]
        return tableData
    except Exception, e:
        print 'main loop', str(e)

# dic = pullTableContent('AAPL')
# print pretty(dic)

'''def symbolCompanyData():
    #nameData = []
    sortedData = []
    data = open("symbol.txt", "r")
    data2 = open('new.txt', 'w')
    # for eachLine in data:
    #     eachLine = eachLine.replace(' \r\n','')
    #     nameData.append(eachLine)
    for curr in data:
        symbolName = curr.split(',')
        #sortedData.append(symbolName)
        #if (len(symbolName) == 2) and (symbolName != None) and (symbolName != '') and (symbolName != ' '):
        if len(symbolName[0]) == 4:
            symbolName[1] = symbolName[1].replace("\n","")
            data2.write('<option value="' + symbolName[0] + '">' + symbolName[1] + '</option>\n')
    data2.close()

symbolCompanyData()'''

'''class symbolCompany():
    def __init__(self, li):
        self.symbol = li[0].encode('utf-8')
        self.companyName = li[1].encode('utf-8')

pd = symbolCompanyData()
for curr in pd:
    d = symbolCompany(curr)
    print d.companyName'''

class stockCo():
    def __init__(self, pd):
        self.company = pd['Company-Name'].encode('utf-8')
        ticker = pd['ticker'].upper()
        self.ticker = ticker.encode('utf-8')
        self.exchangeName = pd['Exchange-Name'].encode('utf-8')
        self.unit = pd['unit'].encode('utf-8')
        self.currency = pd['currency'].encode('utf-8')
        self.firsttrade = pd['first-trade']
        self.lasttrade = pd['last-trade']
        self.closeprice = pd['previous_close_price']
        self.date = pd['Date']
        self.close = pd['close']
        self.high = pd['high']
        self.low = pd['low']
        self.open = pd['open']
        self.volume = pd['volume']

###########################
#NY Article Search API
#https://api.nytimes.com/svc/search/v2/articlesearch.json?sort=oldest&fq=Samsung&api_key=dac195d1e79447eb8b8ebdf4828717fe
def article_search(baseurl = 'https://api.nytimes.com/svc/search/v2/articlesearch.json',
    params={},
    printurl = False
    ):
    
    #params['q'] = 'Samsung'
    params['api_key'] = 'dac195d1e79447eb8b8ebdf4828717fe'
    params['sort'] = 'newest'
    params['fq'] = 'news_desk: (Business)'
    url = baseurl + "?" + urllib.urlencode(params)
    if printurl:
        print url
    else:
        return safeGet(url)
        

def getArticle(q = None):
    resp = json.loads(article_search(params={"q": q}).read())
    result = resp['response']['docs']
    
    return result
#print pretty(getArticle())

class Article():
    def __init__(self, info):
        self.title = unicode(info['headline']['main'])
        self.url = unicode(info['web_url'])
        self.date = unicode(info['pub_date'])[0:10]

################################    

def live_article(baseurl = 'http://api.nytimes.com/svc/news/v3/content/all/all.json',
    params={},
    printurl = False
    ):

    params['api_key'] = 'dac195d1e79447eb8b8ebdf4828717fe'
    url = baseurl + "?" + urllib.urlencode(params)
    return safeGet(url)

        
def live_get_article():
    try:
        a = json.loads(live_article().read())
        memcache.add("articledata",a,60000)
    except:
        a = memcache.get("articledata")
    data = a['results']
    return data
    

#print pretty(live_get_article())


class News():
    def __init__(self, live_info):
        self.title_news = unicode(live_info['title'])
        self.section_news = unicode(live_info['section'])
        self.date_news = unicode(live_info['published_date'])
        self.url_news = unicode(live_info['url'])
        if len(live_info['multimedia']) > 2:
            self.pic_news = unicode(live_info['multimedia'][2]['url'])  
        else: 
            self.pic_news = "https://pmcdeadline2.files.wordpress.com/2016/10/the-new-york-times-logo-featured.jpg?w=210&h=140&crop=1"
            
################################

class MainHandler(webapp2.RequestHandler):
    def get(self):
        logging.info("In MainHandler")
        template_values={}
        template = JINJA_ENVIRONMENT.get_template('home.html')
        self.response.write(template.render(template_values))  

class ChartHandler(webapp2.RequestHandler):
    def get(self):
        logging.info("In ChartHandler")
        template_values={}
        template = JINJA_ENVIRONMENT.get_template('chart.html')
        self.response.write(template.render(template_values))

class AboutHandler(webapp2.RequestHandler):
    def get(self):
        logging.info("In AboutHandler")
        template_values={}
        template = JINJA_ENVIRONMENT.get_template('about.html')
        self.response.write(template.render(template_values))

class HomeHandler(webapp2.RequestHandler):
    def post(self):
        search = self.request.get('search')
            
        vals = {}
        vals['name'] = search
        vals['page_title']="Investment Calculator"
        
        go = self.request.get('gobtn')
        logging.info(search)
        logging.info(go)
        
        if search:
            if pullData(search) == None:
                template = JINJA_ENVIRONMENT.get_template('custom-error.html')
                self.response.write(template.render(vals))
            else:
                data = getArticle(search)
                vals['dataMatrix'] = pullData(search)
                print pullData(search)
                dic = pullTableContent(search)
                vals['tableData'] = stockCo(dic)

                listDic = []
                for curr in data:
                    sortedDic = Article(curr)
                    listDic.append(sortedDic)
                vals['urls'] = listDic
                
                news_data = live_get_article()
                news_list = []
                for n in news_data:
                    sortedNews = News(n)
                    news_list.append(sortedNews)
                    
                vals['news'] = news_list[0:5]

                # if form filled in, greet them using this data
                template = JINJA_ENVIRONMENT.get_template('chart.html')
                self.response.write(template.render(vals))
                logging.info('search= '+search)
        else:
            #if not, then show the form again with a correction to the user
            # vals['prompt'] = "How can I help you if you don't enter a company?"
            template = JINJA_ENVIRONMENT.get_template('custom-error.html')
            self.response.write(template.render(vals))

# for all URLs except alt.html, use MainHandler
application = webapp2.WSGIApplication([ \
                                      ('/chart', ChartHandler),
                                      ('/about', AboutHandler),
                                      ('/data', HomeHandler),
                                      ('/.*', MainHandler)
                                      ],
                                     debug=True) 

