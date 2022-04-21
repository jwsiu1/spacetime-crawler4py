import re
from urllib.parse import urlparse
from bs4 import BeautifulSoup
from collections import defaultdict

stop_words = {"a", "about", "above", "after", "again", "against", "all", "am", "an", "and", "any", "are", "aren't", "as", "at", "be", "because", "been", 
              "before", "being", "below", "between", "both", "but", "by", "can't", "cannot", "could", "couldn't", "did", "didn't", "do", "does", "doesn't", 
              "doing", "don't", "down", "during", "each", "few", "for", "from", "further", "had", "hadn't", "has", "hasn't", "have", "haven't", "having", 
              "he", "he'd", "he'll", "he's", "her", "here", "here's", "hers", "herself", "him", "himself", "his", "how", "how's", "i", "i'd", "i'll", "i'm", 
              "i've", "if", "in", "into", "is", "isn't", "it", "it's", "its", "itself", "let's", "me", "more", "most", "mustn't", "my", "myself", "no", "nor", 
              "not", "of", "off", "on", "once", "only", "or", "other", "ought", "our", "ours", "ourselves", "out", "over", "own", "same", "shan't", "she", 
              "she'd", "she'll", "she's", "should", "shouldn't", "so", "some", "such", "than", "that", "that's", "the", "their", "theirs", "them", "themselves", 
              "then", "there", "there's", "these", "they", "they'd", "they'll", "they're", "they've", "this", "those", "through", "to", "too", "under", "until", 
              "up", "very", "was", "wasn't", "we", "we'd", "we'll", "we're", "we've", "were", "weren't", "what", "what's", "when", "when's", "where", "where's", 
              "which", "while", "who", "who's", "whom", "why", "why's", "with", "won't", "would", "wouldn't", "you", "you'd", "you'll", "you're", "you've", 
              "your", "yours", "yourself", "yourselves"}

# set of urls to avoid duplication of url with same domain and path
visited_urls = set()
# keeps track of the longest page and how many words in the page
longest_page = ""
longest_word = 0
# dictionary to hold word frequencies
word_freq = defaultdict(int)

def scraper(url, resp):
    # add start urls to list of visited urls
    visited_urls.add(url)
    links = extract_next_links(url, resp)
    return [link for link in links if is_valid(link)]

def extract_next_links(url, resp):
    # Implementation required.
    # url: the URL that was used to get the page
    # resp.url: the actual url of the page
    # resp.status: the status code returned by the server. 200 is OK, you got the page. Other numbers mean that there was some kind of problem.
    # resp.error: when status is not 200, you can check the error here, if needed.
    # resp.raw_response: this is where the page actually is. More specifically, the raw_response has two parts:
    #         resp.raw_response.url: the url, again
    #         resp.raw_response.content: the content of the page!
    # Return a list with the hyperlinks (as strings) scrapped from resp.raw_response.content
    
    # list to store hyperlinks
    list = []
    # checks that status code is 200
    if resp.status != 200:
        # check response code error
        return list
    # use BeautifulSoup to extract links
    soup = BeautifulSoup(resp.raw_response.content, 'lxml')
    for link in soup.find_all('a'):
        l = link.get('href')
        # makes sure link is valid
        if l is not None:
            # remove url fragment
            l_defrag = l.split("#")
            # checks for duplication and if url can be crawled
            if l_defrag[0] not in visited_urls and is_valid(l_defrag[0]):
                visited_urls.add(l_defrag[0])
                list.append(l_defrag[0])
    #set_list = set(list)
    #list = [a for a in set_list]
    return list

def is_valid(url):
    # Decide whether to crawl this url or not. 
    # If you decide to crawl it, return True; otherwise return False.
    # There are already some conditions that return False.
    try:
        parsed = urlparse(url)
        # checks if scheme is valid
        if parsed.scheme not in set(["http", "https"]):
            return False
        # checks if hostname is valid
        if not any(parsed.netloc.endswith(domain) for domain in set(["ics.uci.edu", "cs.uci.edu", "informatics.uci.edu", 
                                       "stat.uci.edu", "today.uci.edu"])):
            return False
        # checks if path is valid
        if parsed.netloc.endswith("today.uci.edu") and "/department/information_computer_sciences/" not in parsed.path:
            return False
        # checks if urls are traps
        if trap(url):
            return False
        
        return not re.match(
            r".*\.(css|js|bmp|gif|jpe?g|ico"
            + r"|png|tiff?|mid|mp2|mp3|mp4"
            + r"|wav|avi|mov|mpeg|ram|m4v|mkv|ogg|ogv|pdf"
            + r"|ps|eps|tex|ppt|pptx|doc|docx|xls|xlsx|names"
            + r"|data|dat|exe|bz2|tar|msi|bin|7z|psd|dmg|iso"
            + r"|epub|dll|cnf|tgz|sha1"
            + r"|thmx|mso|arff|rtf|jar|csv"
            + r"|rm|smil|wmv|swf|wma|zip|rar|gz)$", parsed.path.lower())

    except TypeError:
        print ("TypeError for ", parsed)
        raise
        
def trap(url):
    if "replyto" in url:
        return True
    if "calendar" in url: 
        return True
    if "?share=" in url:
        return True
    return False

def tokenize(url, soup):
    text = soup
    result = re.split("[^a-zA-Z0-9]", text)
    result = list(filter(None, result))
    if len(result) > longest_word:
      longest_page = url
      longest_word = len(result)
    for word in result and word not in stop_words:
        word_freq[word] += 1
            
    
    
# Report Answers:
    # unique pages : http://www.ics.uci.edu#aaa and http://www.ics.uci.edu#bbb are the same
    # longest page in terms of words
    # 50 most common words (ignore stop words)
    # number of subdomains (print URL, number)
    
    
def create_report():
    # create new text file to store report results
    f = open("Report.txt", mode="w")
    f.write("Number of unique pages: ") ## need to defrag urls
    f.write("Longest page: " + longest_page + ", " + str(longest_word))
    f.write("50 most common words: ")
    word_freq = sorted(word_freq.items(), key=lambda x:x[1], reverse=True)
    for word in word_freq:
      if count < 50:
        print(word)
      count += 1
    f.write("ics.uci.edu subdomains: ")
    
    f.close()
    
    
    
    
