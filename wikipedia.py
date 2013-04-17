# -*- coding: utf-8 -*-
'''
Created on Mar 01, 2011

@author: Mourad Mourafiq

@copyright: Copyright © 2011

other contributers:
'''
 
import re
from django.utils import simplejson
import urllib
import urllib2
import cookielib
import os
 
url_article = 'http://%s.wikipedia.org/w/index.php?action=raw&title=%s'
url_search = 'http://%s.wikipedia.org/w/api.php?action=query&list=search&srsearch=%s&sroffset=%d&srlimit=%d&format=json'

# Cookie jar. Stored at the user's home folder.
home_folder = os.getenv('HOME')
if not home_folder:
    home_folder = os.getenv('USERHOME')
    if not home_folder:
        home_folder = '.'   # Use the current folder on error.
cookie_jar = cookielib.LWPCookieJar(
                            os.path.join(home_folder, '.wikipedia-cookie'))
try:
    cookie_jar.load()
except Exception:
    pass

class WikipediaError(Exception):
    pass
 
class Wikipedia:   
    def __init__(self, lang):
        self.lang = lang
   
    def _get_page(self, url):
        request = urllib2.Request(url)
        request.add_header('User-Agent',                           
                           'Mozilla/5.0 (X11; U; Linux x86_64; en-US; rv:1.9.2.10) Gecko/20100915\
                            Ubuntu/10.04 (lucid) Firefox/3.6.10')
        cookie_jar.add_cookie_header(request)
        response = urllib2.urlopen(request)
        cookie_jar.extract_cookies(response, request)
        html = response.read()
        response.close()
        cookie_jar.save()
        return html
   
    def article(self, article):
        url = url_article % (self.lang, urllib.quote_plus(article))
        content = self._get_page(url)
       
        if content.upper().startswith('#REDIRECT'):
            match = re.match('(?i)#REDIRECT \[\[([^\[\]]+)\]\]', content)
           
            if not match == None:
                return self.article(match.group(1))
           
            raise WikipediaError('Can\'t found redirect article.')
       
        return content
    
    def search(self, query, page=1, limit=10):
        offset = (page - 1) * limit
        url = url_search % (self.lang, urllib.quote_plus(query), offset, limit)
        content = self._get_page(url)    
        parsed = simplejson.loads(content)
        search = parsed['query']['search']
       
        results = []
       
        if search:
            for article in search:
                title = article['title'].strip()
               
                snippet = article['snippet']
                snippet = re.sub(r'(?m)<.*?>', '', snippet)
                snippet = re.sub(r'\s+', ' ', snippet)
                snippet = snippet.replace(' . ', '. ')
                snippet = snippet.replace(' , ', ', ')
                snippet = snippet.strip()
               
                wordcount = article['wordcount']
               
                results.append({
                    'title' : title,
                    'snippet' : snippet,
                    'wordcount' : wordcount
                })
       
        # yaml.dump(results, default_style='', default_flow_style=False,
        #     allow_unicode=True)
        return results
 
if __name__ == '__main__':
    wiki = Wikipedia('simple')
    print wiki.article('Tony Blair')    
    print wiki.search('the king of Morocco Mohammed V ')   
    print 'OK'

