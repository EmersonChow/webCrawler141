import logging
import re
from urllib.parse import urlparse
from urllib.parse import urldefrag
from lxml import html 


logger = logging.getLogger(__name__)

#Lauryn Newsome (lnewsome)
#Lydia Lee (lydiaml)
#Emerson Chow (emersoc)

class Crawler:
    """
    This class is responsible for scraping urls from the next available link in frontier and adding the scraped links to
    the frontier
    """

    def __init__(self, frontier, corpus, analyzer):
        self.frontier = frontier
        self.corpus = corpus
        self.analyzer = analyzer
        self.recentHistory = []

    def start_crawling(self):
        """
        This method starts the crawling process which is scraping urls from the next available link in frontier and adding
        the scraped links to the frontier
        """
        while self.frontier.has_next_url():
            url = self.frontier.get_next_url()
            logger.info("Fetching URL %s ... Fetched: %s, Queue size: %s", url, self.frontier.fetched, len(self.frontier))
            url_data = self.corpus.fetch_url(url)


            for next_link in self.extract_next_links(url_data):
                
                #50 most common words in ENTIRE set of pages
                self.analyzer.addToCommonWordsDict(url_data['content'])

                if self.is_valid(next_link):
                    #Count outlinks
                    self.analyzer.countOutlinks(url_data['url'])
                    #Add to good list
                    self.analyzer.addToGoodFiles(next_link)

                    if self.corpus.get_file_name(next_link) is not None:
                        self.frontier.add_url(next_link)
                else:
                    self.analyzer.addToTraps(next_link)

    def extract_next_links(self, url_data):
        """
        The url_data coming from the fetch_url method will be given as a parameter to this method. url_data contains the
        fetched url, the url content in binary format, and the size of the content in bytes. This method should return a
        list of urls in their absolute form (some links in the content are relative and needs to be converted to the
        absolute form). Validation of links is done later via is_valid method. It is not required to remove duplicates
        that have already been fetched. The frontier takes care of that.

        Suggested library: lxml
        """

        outputLinks = []

        ogLink = url_data['url']
        if url_data['is_redirected'] == True:
            ogLink = url_data['final_url']

        self.analyzer.addToSubDomDict(ogLink)
        self.analyzer.findLongest(url_data['content'], ogLink)
        try:
            tree = html.fromstring(url_data['content'])
            tree.make_links_absolute(base_url = ogLink)
            links = list(tree.iterlinks())
            for element,srcType, link, index in links:
                if srcType == "href" and link is not None:
                    outputLinks.append(link)
            return outputLinks
        except:
            return []




    def catch_Scheme(self, parsed):
        if parsed.scheme not in set(["http", "https"]):
                return False
        return True
    
    def matchLogic(self, parsed):
        return ".ics.uci.edu" in parsed.hostname \
                   and not re.match(".*\.(css|js|bmp|gif|jpe?g|ico" + "|png|tiff?|mid|mp2|mp3|mp4" \
                                    + "|wav|avi|mov|mpeg|ram|m4v|mkv|ogg|ogv|pdf" \
                                    + "|ps|eps|tex|ppt|pptx|doc|docx|xls|xlsx|names|data|dat|exe|bz2|tar|msi|bin|7z|psd|dmg|iso|epub|dll|cnf|tgz|sha1" \
                                    + "|thmx|mso|arff|rtf|jar|csv" \
                                    + "|rm|smil|wmv|swf|wma|zip|rar|gz|pdf)$", parsed.path.lower())
    
    def addToRecentHistory(self,url):
        if len(self.recentHistory) >= 50:
            self.recentHistory.pop(0)
        self.recentHistory.append(url)


    #Remove the punctuation from path and check against recentHistory
    def tokenAndCheck(self, parsed):
        path = parsed.path
        splitPath = "".join([x if x.isalnum() else " " for x in path]).split()
        for url in self.recentHistory:
            parsedH = urlparse(url)
            splitPathH = "".join([x if x.isalnum() else " " for x in parsedH.path]).split()
            if splitPath[0:3] == splitPathH[0:3]:
                return False
        return True


    def is_valid(self, url):
        """
        Function returns True or False based on whether the url has to be fetched or not. This is a great place to
        filter out crawler traps. Duplicated urls will be taken care of by frontier. You don't need to check for duplication
        in this method
        """

        #If there is a '#' then use urllib.parse.urldefrag(url)[0] to get the url alone with no fragments. 
        #https://www.ics.uci.edu/~kibler/#Research
        #This removes header links

        parsed = urlparse(url)

        #Source: https://help.dragonmetrics.com/en/articles/213691-url-too-long 
        #states that a URL can be considered long if it is over 100 characters long
        TOO_LONG = 100

        try:
            if urldefrag(url)[1] != '':
                return False

            elif self.tokenAndCheck(parsed) == False:
                return False

            elif self.catch_Scheme(parsed) == False:
                return False

            elif self.matchLogic(parsed) == False:
                return False 

            elif len(parsed.path) >= TOO_LONG:
                return False 
            
            else:
                self.addToRecentHistory(url)
                return True


        except TypeError:
            print("TypeError for ", parsed)
            return False

