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

# stores urls that have been crawled to avoid duplication
visited_urls = set()
# stores number of words from longest page
longest_page = 0
# stores words plus total frequency
word_freq = defaultdict(int)
# stores subdomains and total of unique pages
subdomains = defaultdict(int)

def scraper(url, resp):
  global visited_urls
  global word_freq
  global subdomains
  # extract other links from current link
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
  if resp.url not in visited_urls:
    visited_urls.add(resp.url)
  # keeps track of ics.uci.edu subdomains
  # found issue where www.informatics.uci.edu includes www and informatics includes "ics"
  if ".ics.uci.edu" in resp.url and "www.ics.uci.edu" not in resp.url:
    subdomains[resp.url] += 1
  # checks that webpages have important text (not too short, not too long)
  # https://wordcounter.net/words-per-page
  # https://wolfgarbe.medium.com/the-average-word-length-in-english-language-is-4-7-35750344870f 
  # 4.7 = average of letters per word
  # 250 words minimum
  # 20000 words maximum
  # use BeautifulSoup to extract links
  soup = BeautifulSoup(resp.raw_response.content, 'lxml')
  if len(soup.get_text().split()) < 250 or len(soup.get_text().split()) > 20000:
    return list
  # tokenize content of page
  tokens = tokenize(soup.get_text())
  # check and update word freqeuncies
  for word in tokens:
    if word not in stop_words:
      word_freq[word.lower()] += 1
  # extracting links from soup
  for link in soup.find_all('a'):
      l = link.get('href')
      # makes sure link is valid
      if l is not None:
          # remove url fragment
          l_defrag = l.split("#")
          # checks for duplication
          if l_defrag[0] not in visited_urls:
              list.append(l_defrag[0])
  return list

def is_valid(url):
  # Decide whether to crawl this url or not. 
  # If you decide to crawl it, return True; otherwise return False.
  # There are already some conditions that return False.
  try:
      parsed = urlparse(url)
      # checks if urls are traps
      if trap(url):
        return False
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
      
# check for traps
def trap(url):
  # checks for sites with ?replyto= in url
  if "?replyto=" in url: 
      return True
  # checks for sites with ?replytocom= in url
  if "?replytocom=" in url: 
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
    
  # checks for sites with calendar in url
  if "calendar" in url:
      return True
  # checks for YYYY/MM/DD in url
  if re.search('([0-2]{1}[0-9]{3})\/((0[1-9]{1})|(1[0-2]{1}))\/(0[1-9]{1}|[1-2][0-9]{1}|(3[0-1]{1}))', url) != None:
        return True

  return False

# tokenizer
def tokenize(soup):
  global longest_page
  text = soup
  # tokenizes words with apostrophes as 1 token (ie. "isn't")
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
  # create new text file to write report results
  with open("Report.txt", mode="w") as f:
    
    # print total amount of unique pages
    f.write("Unique pages: " + str(len(visited_urls)))
    # print longest page of words
    f.write("\nLongest page: " + str(longest_page) + " words")
    # print most common 50 words (word, total)
    f.write("\nCommon words: \n")
    if len(word_freq) is not None:
      result = sorted(word_freq.items(), key=lambda x:x[1], reverse=True)
      count = 0
      for word, total in result:
        if count < 50:
          f.write("\t" + word + ", " + str(total) + "\n")
          count += 1
    # print all subdomains of ics.uci.edu and total (url, total)
    f.write("\nSubdomains of ics.uci.edu: \n")
    for link, total in sorted(subdomains.items()):
      f.write("\t" + link + ", " + str(total) + "\n")
   
