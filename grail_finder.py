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







## TODO:
    # create config
    # get size
    # make place bid function
    # make highest bid functiono






def main():
    BRANDS_TO_CHECK = [
    'comme+des+garcons',
    'raf+simmons',
    'kith',
    ]

    queries = create_search_queries(BRANDS_TO_CHECK)
    # print(queries)
    items = run_queries(queries)
    print(items)
    # for item in items:
    #     item.print_vals()
    grailed_links = get_grailed_queries(items)
    # print(grailed_links)
    price_list = collect_grailed_prices(grailed_links)
    # print(price_list)
    append_prices_to_items(price_list, items)
    for item in items:
        item.print_vals()



def create_search_queries(brands):
    queries = []
    front = 'https://www.ebay.com/sch/i.html?_from=R40&_nkw='
    end = '&_sacat=1059&rt=nc&LH_Auction=1'
    for brand in brands:
        address = front + brand + end
        queries.append(address)
    return queries

def run_queries(links):
    t_shirts = ['shirt', 't shirt', 'tee', 't-shirt']
    ls_shirts = ['ls shirt', 'longsleeve', 'long sleeve shirt']
    crewneck = ['crew', 'crewneck']
    sweatshirt = ['sweatshirt']
    pants = ['pants']
    coats = ['peacoat', 'anorak', 'raincoat', 'windbreaker', 'coat']

    clothing_types = [t_shirts, ls_shirts, crewneck, sweatshirt, pants, coats]
    BRANDS_TO_CHECK = [
        'comme+des+garcons',
        'raf+simmons',
        'kith',
        # 'palace',
        # 'aime+leon+dore',
        # 'supreme'
    ]
    base_url = 'https://www.ebay.com'
    item_list = []
    keep = 0
    for link in links:
        request = urllib.request.Request(link, None, {'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3626.121 Safari/537.36'})
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
        # print('temp links: ', temp_list)
        keep += len(temp_list)
        item_list.append(temp_list)
    items = [None]*25 # * change this ish
    count = 0
    index = 0
    temp_type = ''
    # print('item_list ', item_list)
    # print(item_list)

    for brand in item_list:
        # print('BRAND::::', brand)
        for link in brand[:5]: # changed index
            # print(link)
            request = urllib.request.Request(link, None, {'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3626.121 Safari/537.36'})
            urlfile = urllib.request.urlopen(request)
            page = urlfile.read()
            soup = BeautifulSoup(page, 'html.parser')
            # BRAND
            spec_brand = BRANDS_TO_CHECK[index]
            # TITLE
            title = soup.find('span', {'class' : "u-dspn"}).get_text()
            # TYPE
            for that_type in clothing_types:
                for name in that_type:
                    if name in title.lower():
                        temp_type = name
            # PRICE not including shipping
            price = soup.find('span', {'class' : "notranslate"}).get_text()
            price = float(price.replace('US $', ''))
            # print(price)
            # price = int(price)
            # SIZE
            # try:
            #     size = soup.find(class_='itemAttr').find(class_='attrLabels').get_text()
            # except:
            #     size = 'unknown'

            # items[count] = item(spec_brand, title, price, size, temp_type)
            items[count] = item(spec_brand, title, price, temp_type)
            count += 1
        # print('index: ', index)
        index += 1
    # for n_dex in items:
    #     n_dex.print_vals()
    #     print('--------------------------------')
    return items

def compare_stockx(list_items):
    # # TODO: create function that finds product id given title --> get first id --> us id to average_price

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

    print('made it here')

    print('stockx urls::::::')
    print(urls)
    average_price = [None]*len(urls)
    index = 0
    driver = webdriver.Chrome()
    driver.maximize_window()
    for link in urls[1:]:
        time.sleep(2)
        print(link)

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



# search on google query: item site:grailed.com, average price breakdown, return. include differential in class
def get_grailed_queries(list_items):
    # print(list_items)
    domain = 'grailed.com'
    temp_brand = ''
    temp_type = ''
    query_url = ''
    grailed_queries = []
    for current in list_items:
        if current is not None:
            temp_title = current.title
            temp_brand = current.brand
            temp_type = current.clothing_type
            temp_q = temp_title + ' site:' + domain
            grailed_queries.append(temp_q)
    return grailed_queries

def search_google(query):
    num_results = 5
    print(query)
    urls = search(str(query), stop=num_results)


    # yield all the results from the generator
    search_results = [url for url in urls]
    # print('search results', search_results)
    return search_results


def get_average_price(urls): # go to each url, collect sold price if available, listing price if not. average them all. return average
    price_sum = 0
    count = 0
    print('urls:::::  ' ,urls)
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
    try:
        return price_sum/count
    except:
        return 0

def collect_grailed_prices(grailed_queries):
    av_prices = []
    for search in grailed_queries:
        # print(search)
        urls = search_google(search)
        # print(urls[:5])
        average = get_average_price(urls)
        av_prices.append(average)
    return av_prices

def append_prices_to_items(prices, items):
    index = 0
    items = items[:len(prices)]
    for current in items:
        current.resale_price = prices[index]
        index += 1
        current.differential = current.resale_price - current.listing_price

class item:
    # def __init__(self, brand, title, listing_price, size, clothing_type):
    def __init__(self, brand, title, listing_price, clothing_type):
        self.brand = brand
        self.title = title
        self.listing_price = listing_price
        # self.size = size
        self.clothing_type = clothing_type
        self.differential = 0
        self.resale_price = 0
    def print_vals(self):
        print('-----------------')
        print('brand, ', self.brand)
        print('title, ', self.title)
        # print('size, ', self.size)
        print('price, ', self.listing_price)
        print('clothing type, ', self.clothing_type)
        print('resale_price, ', self.resale_price)
        print('DIFFERENTIAL, ', self.differential)
        print('-----------------')


main()
