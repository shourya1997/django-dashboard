from django.shortcuts import render, redirect
import re
from bs4 import BeautifulSoup
import requests
requests.packages.urllib3.disable_warnings()

import shutil
import os
from .models import Headline, UserProfile
from datetime import timedelta, timezone, datetime

def news_list(request):
    # user can scrape once in 24 hours
    user_p = UserProfile.objects.filter(user=request.user).first()
    now = datetime.now(timezone.utc)
    time_diff = now - user_p.last_scrape
    time_diff_hrs = time_diff / timedelta(minutes=60)
    next_scrape = 24 - time_diff_hrs
    if time_diff_hrs <= 24:
        hide_me = True
    else:
        hide_me = False


    headlines = Headline.objects.all()
    context = {
        'object_list':headlines,
        'hide_me':hide_me,
        'next_scrape':int(next_scrape)
    }
    return render(request, "news/home.html", context=context)

def scrape(request):
    user_p = UserProfile.objects.filter(user=request.user).first()
    user_p.last_scrape = datetime.now(timezone.utc)
    user_p.save()

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

        media_root = 'media/'
        if not image_source.startswith(("data:image","javascript")):
            local_filename = image_source.split('/')[-1].split("?")[0]
            r = session.get(image_source, stream=True, verify=False)
            with open(local_filename, 'wb') as f:
                for chunk in r.iter_content(chunk_size=1024):
                    f.write(chunk)
            
            current_img_abs_path = os.path.abspath(local_filename)
            shutil.move(current_img_abs_path, media_root)


        new_headline = Headline()
        new_headline.title = title
        new_headline.url = link
        new_headline.image = local_filename
        new_headline.save()
    
    return redirect('/home/')