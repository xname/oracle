#!/usr/bin/python
#SPAM oracle class
###############################
from __future__ import division
import nltk, re, pprint
from xgoogle.search import GoogleSearch, SearchError
from urllib2 import *
import urllib, time, os, string
from xgoogle.BeautifulSoup import *
from sys import stderr
#############################

# What we are pretending to be when we ask google.
user_agents = [
        'Mozilla/5.0 (Windows; U; Windows NT 5.1; it; rv:1.8.1.11) Gecko/20071127 Firefox/2.0.0.11',
        'Opera/9.25 (Windows NT 5.1; U; en)'
        'Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.1; SV1; .NET CLR 1.1.4322; .NET CLR 2.0.50727)',
        'Mozilla/5.0 (compatible; Konqueror/3.5; Linux) KHTML/3.5.5 (like Gecko) (Kubuntu)',
        'Mozilla/5.0 (X11; U; Linux i686; en-US; rv:1.8.0.12) Gecko/20070731 Ubuntu/dapper-security Firefox/1.5.0.12',
        'Lynx/2.8.5rel.1 libwww-FM/2.14 SSL-MM/1.4.1 GNUTLS/1.2.9',
        'Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.1; en) Opera 8.50  Opera 8.5, Windows XP',
        'Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.1; en) Opera 8.0 Opera 8.0, Windows XP',
        'Mozilla/4.0 (compatible; MSIE 6.0; MSIE 5.5; Windows NT 5.1) Opera 7.02 [en] Opera 7.02, Windows XP',
        'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-US; rv:1.7.5) Gecko/20060127 Netscape/8.1'
    ]
class MyOpener(urllib.URLopener):
    version = choice(user_agents)
    
class SmartRedirectHandler(HTTPRedirectHandler):
    def http_error_301(self, req, fp, code, msg, headers):
        result = urllib2.HTTPRedirectHandler.http_error_301(self, req, fp, code, msg, headers)
        result.status = code          
        return result

                        
##############################
        
class Oracle():
    def __init__(self):
        self.cached_results = {}
        self.results = []
        self.retry   = 5
        self.words   = []
        self.url     = ""
        self.zzz     = 12
        self.wordlist = [w for w in nltk.corpus.brown.words() if w.islower()]
    def seed(self):
        """ Outputs a number 'n' that we use as a seed. It is derived from the time of the execution. We use this for picking the nth result page 
            from our search, the nth a word from that  page and it will be the total of words we are going to search for. 
        """
        t=list(time.gmtime())
        n=t[3]+t[4]
        n=list(str(n))
        if len(n) == 1:
            num=int(n[0])
        else:
            num=int(n[0])+int(n[1])
        return num

    def cachedresults(self,word,new_results=[]):
        """Return cached results for word if we have them
           otherwise add them to the dictionary
        """
        if word in self.cached_results:
            print "-----Cached results for :", word
            return self.cached_results[word]
        else:
            self.cached_results[word]=new_results
            return self.cached_results[word]
        
    def opener(self,url):
        """ Get a url as an argument, retrieve it and dump the html 
            sleep randomly between opening urls so google does not figures out we 
            are not humans.
        """
        try:
            print "--opening : ", url
            self.zzz=(random.random()+random.choice([0.3,1,1.2,2,0.3]))            
            time.sleep(self.zzz) #random sleep before we hit the web
            w = MyOpener()
            #print w.version
            request = w.open(url)
            f=request.read()
            request.close()
            print "--closed "
            return f
            
        except Exception,e:
            raise e
        

    def goggle(self,word):
        """Get results from google """
        try:
            results = []
            gs = GoogleSearch(word,random_agent=True)
            gs.results_per_page = 50
            hits = gs.get_results()
            for hit in hits:
                results.append(hit.url.encode('utf8'))
            return results
        except SearchError, e:
            print "Search failed: %s" % e

    def get_word(self,number,url):
        """Extracts words from url  """
        try:
            print "-----get word starts"
            html=self.opener(url)
            if html:
                soup = BeautifulSoup(html.decode('utf-8', 'ignore'))
                clean = nltk.clean_html(html)
                tokens = nltk.word_tokenize(clean)
                tokens = [b for b in tokens if len(b) > 1]
                tokens = [c for c in tokens if not c.istitle()]
#                tokens = [d for d in tokens if not d[0].isdigit()]
                print "New list"
                print len(tokens), number
                if len(tokens) < 24:
                    tokens = [x for x in tokens if x not in set(tokens).difference(self.wordlist)]
                else:
                    print 'more than 24'
                    print int(len(tokens)/2)
                    #tokens = tokens[int(len(tokens))/2:len(tokens)-1]
                    tokens = tokens[int(len(tokens)/2):int((len(tokens)/2)+20)]
                    tokens = [x for x in tokens if x not in set(tokens).difference(self.wordlist)]
                print tokens
                print "---------t--------------------"
                if len(tokens) < number:
                    word   = tokens[-1]
                else:
                    word   = tokens[number]+" "+tokens[number+1]
                print word
            else:
                print "-----Nothing came back. What Do I do? "
                return
        except Exception,e:
            raise  e
            print e
  
        print "----get words end"        
        return word

    def makeoracle(self,words):
        """ A futile attempt to make sense of the words"""
        s = ' '.join(self.words)
        tokens  = nltk.word_tokenize(s)
        text    = nltk.Text(tokens)
        tagged  = nltk.pos_tag(tokens)
        grammar = "NP: {<NNS><TO><VB>}"
        cp = nltk.RegexpParser(grammar)
        result = cp.parse(tagged)
        return tokens
        
    def oracle(self,word,x):
        """ This is the main function, runs in a loop until we have collected all the words we needed. It quits if there are too many failures.
        """
        self.word=word
        self.words.append(word)

        while len(self.words) < x  and self.retry > 0:
                y=x

                print self.words
                print "|Number: %s |Current Word: %s |Word Count : %s" % (x, self.word, len(self.words))
                self.results = self.goggle(self.word)
                #print self.results 
                try:
                    print "PASS: ", x, y
                    print len(self.results)  ##
                    if self.results:
                        if len(self.results) < x:
                            print "We got Less Results than expected"
                            url=self.results[len(self.results)-1]
                        else:
                            url=self.results[x]
                        #print "-URL: %s For Word: %s" % (url, self.word)

                        for i in range(len(self.results)):
                            #we try all results until we hit one that returns the word.
                            try:
                                self.word = self.get_word(23+x,url)
                                if self.word:
                                    print "We Got The Word?", self.word
                                    self.words.append(self.word)
                                    self.retry=5
                                    print "Retry => ", self.retry
                                    break
                            except:
                                y=y-1
                                url=self.results[y]
                                print "We crapped out while trying for a word. Decrement y", y, url
                                time.sleep(self.zzz)
                        
                    else:
                        print "-No results from google. Try Again"
                        print "Sleeping for %s seconds... " %  self.zzz
                        self.zzz=(self.zzz+5)
                        time.sleep(self.zzz)
                        
                except Exception,e:
                    
                    print "Ouch !!!" ,e
            

                    y=y-1
                    self.retry=self.retry-1
                    print "Retry: " , self.retry
                    continue
        if self.words:
            #print self.makeoracle(self.words)
            return self.makeoracle(self.words)

