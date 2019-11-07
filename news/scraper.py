from bs4 import BeautifulSoup
import requests
requests.packages.urllib3.disable_warnings()
import re

def scrape():
    session = requests.Session()
    session.headers = {"User-Agent":"Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/51.0.2704.103 Safari/537.36 "}
    url = 'https://www.theonion.com/'
    content = session.get(url, verify=False).content
    soup = BeautifulSoup(content, "html.parser")

    posts = soup.find_all('div',{'class':'curation-module__item'})
    
    for i in posts:
        link = i.find('section',{'class':'content-meta__headline__wrapper'}).a['href']
        title = i.find('section',{'class':'content-meta__headline__wrapper'}).a['title']
        image_source = i.find('img')['srcset']
        image_source = [x.strip() for x in re.split(r' .[0-9]*[w][,]| .[0-9]*[w]', image_source)] # this splits the url and removes '1600w' from url fetched and removes whitespaces also
        image_source = image_source[:len(image_source)-1]
        image_source = image_source[1]
