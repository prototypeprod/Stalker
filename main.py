from urllib.parse import urlencode, urlparse, parse_qs
from lxml.html import fromstring
import requests
from bs4 import BeautifulSoup
import re
import imghdr
import os
import json

linkgex = re.compile(
        r'^(?:http|ftp)s?://' # http:// or https://
        r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+(?:[A-Z]{2,6}\.?|[A-Z0-9-]{2,}\.?)|' #domain...
        r'localhost|' #localhost...
        r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})' # ...or ip
        r'(?::\d+)?' # optional port
        r'(?:/?|[/?]\S+)$', re.IGNORECASE)

#Start of program
name = "James Chen"

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

harvest = {}
with open('./output/harvested.json', 'w') as outfile:
    json.dump(harvest, outfile)

for i in range(3):
    r = 0
    for result in getpage(name, i).cssselect(".r a"):
        r = r + 1
        url = result.get("href")
        if url.startswith("/url?"):
            url = parse_qs(urlparse(url).query)['q']
        if re.match(linkgex, url[0]):
            try:
                imgurls = getimagesurl(url[0])
                y = 0
                for imgurl in imgurls:
                    y = y+1
                    print("---")
                    try:
                        if imgurl['src']:
                            parseurl = imgurl['src']
                            if 'http' not in imgurl['src']:
                                # sometimes an image source can be relative
                                if (imgurl['src'][0] == "//" or "\\\\") and (imgurl['src'][1] == "//" or "\\\\"):
                                    print("1")
                                    parseurl = "http://"+(imgurl['src'][2:])
                                elif imgurl['src'][0] == "/" or "\\":
                                    print("2")
                                    netloc = urlparse(url[0]).netloc
                                    parseurl = "http://"+netloc+str(imgurl['src'])
                                else:
                                    print("3")
                                    parseurl = url[0]+str(imgurl['src'])
                            print(url[0])
                            print(imgurl['src'])
                            print(parseurl)
                            response = requests.get(parseurl)
                            filename = str(i)+"-"+str(r)+"-"+str(y)
                            harvest[str(i)+"-"+str(r)+"-"+str(y)] = {"url": url[0], "img": imgurl['src'], "parsed": parseurl}
                            jsonf = open("./output/harvested.json", "w")
                            jsonf.write(json.dumps(harvest, indent=4, sort_keys=True))
                            jsonf.close()
                            with open("./output/"+filename+".check", 'wb') as f:
                                f.write(response.content)
                            itype = imghdr.what("./output/"+filename+".check")
                            if not itype:
                                # Cases where cannot read image type. Most of the times it's SVG
                                itype = "svg"
                            os.rename("./output/"+filename+".check", "./output/"+filename+"."+itype)
                    except Exception as e:
                        print(e)
                        pass
            except Exception as e:
                print(e)
                pass
