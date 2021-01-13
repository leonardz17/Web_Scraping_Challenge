from splinter import Browser
from bs4 import BeautifulSoup
from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager

import time
import requests
import pymongo

conn = "mongodb://localhost:27017"
client = pymongo.MongoClient(conn)

db = client.mars_db

def init_browser():
    executable_path = {'executable_path': ChromeDriverManager().install()}
    return Browser("chrome", **executable_path, headless=False)

def scrape_info():
    browser = init_browser() 
    mars_all = {}   

    # First website to scrape for news title and paragraph
    url = "https://mars.nasa.gov/news/?page=0&per_page=40&order=publish_date+desc%2Ccreated_at+desc&search=&category=19%2C165%2C184%2C204&blank_scope=Latest"
    browser.visit(url)

    html = browser.html
    soup = BeautifulSoup(html, "html.parser")

    results = soup.find_all('ul',class_='item_list')
    for result in results:

        news_title = result.find('div',class_='content_title').text
        mars_all["news_title"] = news_title

        news_p = result.find('div',class_='article_teaser_body').text
        mars_all["news_p"] = news_p

    # Second website to scrape for image
    url = "https://www.jpl.nasa.gov"

    browser.visit(url)

    xpath = '/html/body/div/div/div/header/div[1]/div[3]/div/nav/div[1]/div[4]/button/span'
    browser.find_by_xpath(xpath).click()

    time.sleep(1)
    xpath = '/html/body/div/div/div/header/div[1]/div[3]/div/nav/div[1]/div[4]/div/div/div/div/div[1]/div/div/div/a/p[1]'
    browser.find_by_xpath(xpath).click()

    xpath = '/html/body/div/div/div/main/div/div[2]/div/div/div[2]/button/span'
    browser.find_by_xpath(xpath).click()


    html = browser.html
    soup = BeautifulSoup(html, 'html.parser')
    # results = soup.body.main.find_all('img')
    results = soup.find_all('div', class_='BaseLightbox__slide__img')

    for result in results:
        mars_all["featured_image_url"] = result.img['src']
    
    # Third website to scrape for image url and title of the 4 hemispheres
    url = "https://astrogeology.usgs.gov/search/map/Mars/Viking/cerberus_enhanced"
    

    ## List containing the names of the 4 hemispheres
    mars_hemispheres = ['cerberus', 'schiaparelli', 'syrtis_major', 'valles_marineris']
    response = requests.get(url)
    soup = BeautifulSoup(response.text, "html.parser")

    for hemisphere in mars_hemispheres:
        mars_url = f'https://astrogeology.usgs.gov/search/map/Mars/Viking/{hemisphere}_enhanced'
        response = requests.get(mars_url)
        soup = BeautifulSoup(response.text, "html.parser")
        results = soup.find_all("img", class_='wide-image')
    
        for result in results:
            img_url = result.get('src')
            title = soup.find("h2", class_='title').text
            title = title.replace(' Enhanced',"")
            mars_all[f"{hemisphere}_title"] = title
            mars_all[f"{hemisphere}_img_url"] = "https://astrogeology.usgs.gov" + img_url
    
    db.mars_info.insert_one(mars_all)

    browser.quit()
    
    return mars_all

