import re
from urllib.parse import urlparse
from bs4 import BeautifulSoup
from collections import defaultdict
import configparser
from utils import download, config, server_registration


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

visited_urls = set()
longest_page = 0
word_freq = defaultdict(int)

def scraper(url, resp):
  if resp.status != 200:
    return []
  # add start urls to list of visited urls
  if url not in visited_urls:
    visited_urls.add(url)
  links = extract_next_links(url, resp)
  
  # create and update report
  create_report(url, links)
  
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
  # checks for valid response status (200)
  if resp.status != 200:
    return list
  # checks that webpages have at least 250 words or less than 20000 words 
  # https://wordcounter.net/words-per-page
  if len(resp.raw_response.content) < 250 or len(resp.raw_response.content) > 45000:
    return list
  # use BeautifulSoup to extract links
  soup = BeautifulSoup(resp.raw_response.content, 'lxml')
  tokens = tokenize(soup)
  # check and update word freqeuncies
  for word in tokens:
    if word not in stop_words:
      word_freq[word.lower()] += 1
  for link in soup.find_all('a'):
      l = link.get('href')
      # makes sure link is valid
      if l is not None:
          # remove url fragment
          l_defrag = l.split("#")
          # checks for duplication
          if l_defrag[0] not in visited_urls:
              visited_urls.add(l_defrag[0])
              list.append(l_defrag[0])
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
  # checks for sites with replyto in url
  if "replyto" in url:
      return True
  # checks for sites with calendar in url
  if "calendar" in url: 
      return True
  # checks for sites with ?share= in url
  if "?share=" in url:
      return True
  # checks for sites with ?session= in url
  if "?session=" in url:
      return True
  # checks for sites with ?action= in url
  if "?action=" in url:
      return True
  # checks for YYYY/MM/DD in url
  if re.search('([0-2]{1}[0-9]{3})\/((0[1-9]{1})|(1[0-2]{1}))\/(0[1-9]{1}|[1-2][0-9]{1}|(3[0-1]{1}))', url) != None:
        return True

  return False

# tokenizer
def tokenize(soup):
  global longest_page
  text = soup.get_text()
  result = re.split("[^a-zA-Z0-9']", text)
  result = list(filter(None, result))
  # check and update longest_page
  if len(result) > longest_page:
    longest_page = len(result)
  return result
            
    
    
# Report Answers:
    # unique pages : http://www.ics.uci.edu#aaa and http://www.ics.uci.edu#bbb are the same
    # longest page in terms of words
    # 50 most common words (ignore stop words)
    # number of subdomains (print URL, number)
    
def create_report(url, links):
  # set of urls to avoid duplication of url with same domain and path
  global visited_urls 
  # dictionary to hold word frequencies
  global word_freq 
  # create new text file to store report results
  with open("Report.txt", mode="w") as f:
    f.write("Unique pages: " + str(len(visited_urls)))
    f.write("\nLongest page: " + str(longest_page) + " words")
    f.write("\nCommon words: \n")
    if len(word_freq) is not None:
      result = sorted(word_freq.items(), key=lambda x:x[1], reverse=True)
      count = 0
      for word, total in result:
        if count < 50:
          f.write("\t" + word + ", " + str(total) + "\n")
          count += 1
    
    f.write("\nSubdomains of " + url + ": ")
    
    # begin process to crawl each subdomain and find number of unique pages
    con = configparser.ConfigParser()  # use configparser to parse and read "config.ini" file
    con.read("config.ini")
    
    con = config.Config(con)
    con.cache_server = server_registration.get_cache_server(con, False) 
    
    for val, subdomain in enumerate(sorted(links)):
        visited_urls.clear()
          
        if subdomain != url:
            resp = download.download(subdomain, con)  # generate a response.py object to use for crawling 

            # list to store subdomain hyperlinks
            subdomain_links = []

            # checks that status code is 200
            if resp.status != 200:
                subdomain_links = []
            # checks that webpages have at least 250 words or less than 20000 words
            elif len(resp.raw_response.content) < 250 or len(resp.raw_response.content) > 45000:
                subdomain_links = []
            else:
                # use BeautifulSoup to extract links
                soup = BeautifulSoup(resp.raw_response.content, 'lxml')

                for link in soup.find_all('a'):
                    l = link.get('href')

                    # makes sure link is valid
                    if l is not None:
                      # remove url fragment
                      l_defrag = l.split('#')

                      # checks for duplication and if url can be crawled
                      if l_defrag[0] not in visited_urls and is_valid(l_defrag[0]):
                        visited_urls.append(l_defrag[0])
                        subdomain_links.append(l_defrag[0])

            f.write('\n' + subdomain + ", " + str(len(subdomain_links)))
 
