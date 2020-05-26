from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from six.moves import urllib
import requests
import time
import re
from itertools import chain
from datetime import datetime
from googlesearch import search
import string
import config
from config import item


def return_best_resale_options():
    queries = create_search_queries(config.BRANDS_TO_CHECK)
    print("QUERIES \n", queries)
    items = run_queries(queries)
    print("ITEMS \n", items)
    # for item in items:
    #     item.print_vals()
    # grailed_links = get_grailed_queries(items)
    stockx_queries = get_stockx_queries(items)
    # print(grailed_links)
    print("STOCKX QUERIES \n", stockx_queries)
    # price_list = collect_grailed_prices(grailed_links)
    price_list = collect_stockx_prices(stockx_queries)
    print(price_list)
    # append_prices_to_items(price_list, items)
    # for item in items:
    #     item.print_vals()

""" given a list of brands of type (str), return [] of concatonated query
strings """
def create_search_queries(brands):
    queries = []
    front = 'https://www.ebay.com/sch/i.html?_from=R40&_nkw='
    end = '&_sacat=1059&rt=nc&LH_Auction=1'
    for brand in brands:
        address = front + brand + end
        queries.append(address)
    return queries


""" compile items from eBay based on given brands, return the list of items """
def run_queries(brand_links):
    item_list = create_item_list(brand_links)

    items = [None]*25 # change this

    count = 0
    index = 0
    for brand in item_list:
        for link in brand[:5]: # changed index
            items[count] = ebay_info_to_item(link, config.BRANDS_TO_CHECK[index])
            count += 1
        index += 1
    return items

""" given list of urls corresponding to brand-biased ebay searches, collects
links and instantiate items with them, return the list of items """
def create_item_list(brand_links):
    item_list = []
    keep = 0
    for link in brand_links:
        request = urllib.request.Request(link, None, config.USER_AGENT)
        urlfile = urllib.request.urlopen(request)
        page = urlfile.read()
        soup = BeautifulSoup(page, 'html.parser')
        item_links = soup.find_all(class_='s-item__link')
        temp_list = []
        for thelink in item_links:
            try:
                temp_list.append(thelink.get('href'))
            except:
                pass
        keep += len(temp_list)
        item_list.append(temp_list)
    return item_list

""" complile initial ebay information into an item(class) """
def ebay_info_to_item(link, brand):
    request = urllib.request.Request(link, None, config.USER_AGENT)
    urlfile = urllib.request.urlopen(request)
    page = urlfile.read()
    soup = BeautifulSoup(page, 'html.parser')
    title = soup.find('span', {'class' : "u-dspn"}).get_text()
    for current_type in config.clothing_types:
        for name in current_type:
            if name in title.lower():
                temp_type = name
            else:
                temp_type = "N/A"
    price = soup.find('span', {'class' : "notranslate"}).get_text()
    price = float(price.replace('US $', ''))
    return item(brand, title, price, temp_type)

""" evade bot detection by using google site search with query (<item title>
site:grailed.com), return average price """
def get_grailed_queries(list_items):
    # print(list_items)
    domain = 'grailed.com'
    grailed_queries = []
    for current in list_items:
        if current is not None:
            temp_title = current.title
            temp_q = temp_title + ' site:' + domain
            grailed_queries.append(temp_q)
    return grailed_queries

""" evade bot detection by using google site search with query (<item title>
site:stockx.com), return average price """
def get_stockx_queries(list_items):
    # print(list_items)
    domain = 'stockx.com'
    stockx_queries = []
    for current in list_items:
        if current is not None:
            temp_title = current.title
            temp_q = temp_title + ' site:' + domain
            stockx_queries.append(temp_q)
    return stockx_queries


""" given list[] of grailed url's of type(str), return list[] of average
prices """
def collect_grailed_prices(grailed_queries):
    av_prices = []
    for search in grailed_queries:
        # print(search)
        urls = search_google(search)
        # print(urls[:5])
        average = get_average_price_grailed(urls)
        av_prices.append(average)
    return av_prices

""" given list[] of stockx url's of type(str), return list[] of average
prices """
def collect_stockx_prices(stockx_queries):
    av_prices = []
    for search in stockx_queries:
        print(search)
        urls = search_google(search)
        # print(urls[:5])
        average = get_average_price_grailed(urls)
        av_prices.append(average)
    return av_prices

""" return search list[] of urls of type(string) given query string """
def search_google(query):
    num_results = config.NUM_RESULTS
    urls = search(str(query), stop=num_results)
    search_results = [url for url in urls]
    return search_results

""" Create list[] by going to each url, collecting sold price if available,
listing price if not. Return average of values of type(int) """
def get_average_price_grailed(urls):
    price_sum = 0
    count = 0
    for url in urls:
        page = requests.get(url)
        soup = BeautifulSoup(page.text, 'html.parser')
        try:
            price = soup.find(class_='-price _sold').get_text()
            price = float(re.sub("[^0-9]", "", price))
            price_sum += price
            count += 1
        except:
            pass
    if count != 0:
        return price_sum/count
    return 0

def get_price_stockx(urls):
    price = 0

    page = requests.get(urls[0])
    soup = BeautifulSoup(page.text, 'html.parser')
    try:
        price = soup.find(class_='en-us stat-value stat-small').get_text()
        price = float(re.sub("[^0-9]", "", price))
    except:
        pass
    return price

""" append prices to respective items in item(class) """
def append_prices_to_items(prices, items):
    index = 0
    items = items[:len(prices)]
    for current in items:
        current.resale_price = prices[index]
        index += 1
        current.differential = current.resale_price - current.listing_price



def compare_stockx(list_items):
    # TODO: create function that finds product id given title --> get first id --> us id to average_price

    base_url = 'https://stockx.com/search?s='
    temp_brand = ''
    temp_type = ''
    query_url = ''
    urls = []
    for current in list_items:
        # current.print_vals()
        temp_brand = current.brand
        temp_type = current.clothing_type
        query_url = base_url + temp_brand
        query = current.clothing_type
        for element in query.split():
            query_url += '%20'
            query_url += element
        urls.append(query_url)
    average_price = [None]*len(urls)
    index = 0
    driver = webdriver.Chrome()
    driver.maximize_window()
    for link in urls[1:]:
        time.sleep(2)
        driver.implicitly_wait(30)
        driver.get(link)
        count = 1
        sum = 0
        iter = 1
        while iter <= 5:
            time.sleep(2)
            temp_price = driver.find_element_by_xpath('//*[@id="search-wrapper"]/div[3]/div[' +str(iter)+ ']/div/a/div[1]/div').text.replace('$', '')
            # print('temp_price', temp_price)
            sum += int(temp_price)
            iter += 1
        average_price[urls.index(link)] = sum/5
        print(average_price[urls.index(link)])
    driver.quit()
    #     for price_now in prices:
    #         price_list.append(price_now.get_text().replace('$', ''))
    #     sum = 0
    #     print(price_list)
    #     for price in price_list[:5]:
    #         sum += int(price)
    #     average_price[index] = sum/5
    #     index += 1
    # print(average_price)


return_best_resale_options()
