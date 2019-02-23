from urllib.parse import urlencode, urlparse, parse_qs
from lxml.html import fromstring
import requests
from bs4 import BeautifulSoup
import re
linkgex = re.compile(
        r'^(?:http|ftp)s?://' # http:// or https://
        r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+(?:[A-Z]{2,6}\.?|[A-Z0-9-]{2,}\.?)|' #domain...
        r'localhost|' #localhost...
        r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})' # ...or ip
        r'(?::\d+)?' # optional port
        r'(?:/?|[/?]\S+)$', re.IGNORECASE)

#Start of program
name = "SJI Singapore"

def getpage(query, page=0):
    encoded = urlencode({'q':query, 'start':page*10})
    raw = requests.get("https://www.google.com/search?"+str(encoded)).text
    page = fromstring(raw)
    return page

def getimagesurl(site):
    response = requests.get(site)

    soup = BeautifulSoup(response.text, 'html.parser')
    img_tags = soup.find_all('img')

    urls = [img for img in img_tags]

    return urls


for i in range(1000):
    for result in getpage(name, i).cssselect(".r a"):
        url = result.get("href")
        if url.startswith("/url?"):
            url = parse_qs(urlparse(url).query)['q']
        if re.match(linkgex, url[0]):
            try:
                imgurls = getimagesurl(url[0])

                for imgurl in imgurls:
                    print("---")
                    try:
                        if imgurl['src']:
                            parseurl = imgurl['src']
                            filename = re.search(r'/([\w_-]+[.](jpg|gif|png))$', imgurl['src'])
                            if ('http' or 'https') not in imgurl['src']:
                                # sometimes an image source can be relative
                                if imgurl['src'][0] == "/"or'\\':
                                    netloc = urlparse(url).netloc
                                    parseurl = netloc+url[0]+str(imgurl['src'])
                                else:
                                    parseurl = url[0]+str(imgurl['src'])
                            print(parseurl)
                            response = requests.get(parseurl)
                            with open("./output/"+filename.group(1), 'wb') as f:
                                f.write(response.content)
                    except Exception as e:
                        print(e)
            except:
                pass
