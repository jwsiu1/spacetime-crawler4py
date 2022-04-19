import re
from urllib.parse import urlparse
from bs4 import BeautifulSoup

def scraper(url, resp):
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
        print(resp.error)
        return list
    # use BeautifulSoup to extract links
    soup = BeautifulSoup(resp.raw_response.content, 'html.parser')
    for link in soup.find_all('a'):
        list.append(link.get('href'))

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
        if any(parsed.netloc.endswith(domain) for domain in set(["ics.uci.edu", "cs.uci.edu", "informatics.uci.edu", 
                                       "stat.uci.edu", "today.uci.edu"])):
            return False
        # checks if path is valid
        if parsed.netloc.endswith("today.uci.edu") and "/department/information_computer_sciences/" not in parsed.path:
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
        
# Report Answers:
    # unique pages : http://www.ics.uci.edu#aaa and http://www.ics.uci.edu#bbb are the same
    # longest page in terms of words
    # 50 most common words (ignore stop words)
    # number of subdomains (print URL, number)
    
    
def report():
    # create new text file to store report results
    f = open("Report.txt", mode="w")
    f.write("Number of unique pages: ") ## need to defrag urls
    f.write("Longest page (words): ")
    f.write("50 most common words: ")
    f.write("ics.uci.edu subdomains: ")
    
    
    f.close
    
    
    
    
