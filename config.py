USER_AGENT = {'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.149 Safari/537.36'}
NUM_RESULTS = 5

BRANDS_TO_CHECK = [
    'comme+des+garcons',
    'raf+simmons',
    'kith'
]


t_shirts = ['shirt', 't shirt', 'tee', 't-shirt']
ls_shirts = ['ls shirt', 'longsleeve', 'long sleeve shirt']
crewneck = ['crew', 'crewneck']
sweatshirt = ['sweatshirt']
pants = ['pants']
coats = ['peacoat', 'anorak', 'raincoat', 'windbreaker', 'coat']

clothing_types = [t_shirts, ls_shirts, crewneck, sweatshirt, pants, coats]

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
