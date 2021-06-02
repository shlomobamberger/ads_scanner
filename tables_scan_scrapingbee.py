import asyncio
import json
import os
import urllib.request
import requests
from bs4 import BeautifulSoup as bf
from telethon import TelegramClient
from datetime import datetime


###########################################################################################
mission_name = ''  # CHANGE IT
FULL_DB_FILE = r"full_scan_db.json"  # CHANGE IT
HOURLY_DB_FILE = r"tables_hourly_scan_db.json"  # CHANGE IT
NEW_ADS_FILE = r"new_ads.json" # CHANGE IT
LOG_FILE = r"log file.txt" # CHANGE IT
HTML_FILE = r"html_file.txt" # CHANGE IT
URL_TO_SCAN = r'https://www.yad2.co.il' # CHANGE IT
IMAGES_FOLDER = r"images"  # CHANGE IT
PAGES_TO_SCAN = 10  # CHANGE IT
TELEGRAM_USERS = ('',)  # CHANGE IT
api_id = 0   # CHANGE IT
api_hash = '' # CHANGE IT
bot_api = ''  # CHANGE IT
client = TelegramClient('', api_id, api_hash)  # CHANGE IT
scrapingbee_token = '' # CHANGE IT
###########################################################################################


bot = TelegramClient('bot', api_id, api_hash).start(bot_token=bot_api)
all_data_dict = {}

def log_helper(text):
    now = datetime.now()
    current_time = now.strftime("[%Y-%m-%d]   [%H:%M:%S]")
    log_line = current_time + '   ' + str(text) + '\n'
    with open(LOG_FILE, 'a', encoding='utf-8') as f:
        f.write(log_line)


def get_id():
    with open(HTML_FILE, mode='r', encoding='utf-8') as r:
        if r'assets.yad2.co.il/yad2site/y2assets/images/pages/feed/no-results-feed.png' in r:
            log_helper("no-results for this url")
            return False
        elif 'Are you for real' in r:
            log_helper('site blocked you')
            return False
        elif 'העמוד לא נמצא' in r:
            log_helper('There are no results for your search')
            return False
        else:
            result = bf(r, 'html.parser')
            ad_details(HTML_FILE)
    return result


def ad_details(filename='current.html'):
    id_and_ad = {}
    with open(filename, mode='r', encoding='utf-8') as f:
        content = f.read()
        soup = bf(content, 'html.parser')
        try:
            business_ads = soup.find('h2', attrs={'id': 'item_title_183'})
            ads = business_ads.find_all_previous("div", attrs={'class': 'feeditem table'})
        except:
            ads = soup.find_all("div", attrs={'class': 'feeditem table'})
        for ad in ads:
            ad_dict = {}
            if ad.find("div", attrs={'class': 'merchant merchant_name'}):  #ads from store
                pass
            else:  #ads from people
                id_of_ad = ad.find("div", attrs={'item-id': True}).get('item-id')
                direct_link = r"https://www.yad2.co.il/item/" + id_of_ad
                text = "".join(ad.find(attrs={'class': 'row-1'}).contents).strip()
                city = "".join(ad.find(attrs={'class': 'val'}).text).strip()
                price = "".join(ad.find(attrs={'class': 'price'}).text).strip()
                image = "".join(ad.find(attrs={'class': 'feedImage'}).get('src')).strip()
                if image == r'//assets.yad2.co.il/yad2site/y2assets/images/pages/feed/feed_img_placeholder_small.jpg':
                    image = 'https://assets.yad2.co.il/yad2site/y2assets/images/pages/feed/feed_img_placeholder_small.jpg'
                file_size_in_url = r'?l=7&c=3&w=195&h=117'
                if file_size_in_url in image:
                    image = image.replace(file_size_in_url, "")
                ad_dict['id'] = id_of_ad
                ad_dict['text'] = text.rstrip()
                ad_dict['direct_link'] = direct_link.strip()
                ad_dict['city'] = city.rstrip()
                ad_dict['price'] = price.strip()
                ad_dict['image'] = image.strip()
                id_and_ad[id_of_ad] = ad_dict
    all_data_dict.update(id_and_ad)
    return id_and_ad


def find_new_ads(oldfile, newfile):
    num_ads_to_scan = 0
    num_new_ads = 0
    new_ads_dict = {}
    loop = asyncio.get_event_loop()
    with open(r"C:\yad2scan\near_cities.txt", 'r', encoding='utf-8') as city:
        city_list = city.read().replace('\n', '')
    with open(oldfile, 'r', encoding='utf-8') as f:
        o = json.load(f)
    with open(newfile, 'r', encoding='utf-8') as f:
        n = json.load(f)
    for i in n:
        num_ads_to_scan += 1
        if i not in o:
            num_new_ads += 1
            image_path = os.path.join(IMAGES_FOLDER, n[i]['id'] + ".jpg")
            if n[i]['city'] in city_list:
                n[i]['city'] += ' ✅ קרוב'
            else: 
                n[i]['city'] += ' ❌ רחוק'
            new_ad_setails = (n[i]['direct_link'] + '\n' + n[i]['text'] + '\n' + n[i]['price']+ '\n' + n[i]['city'])
            urllib.request.urlretrieve(n[i]['image'], image_path)
            new_ads_dict[i] = n[i]
            for user in TELEGRAM_USERS:
                loop.run_until_complete(send_image_to_telegram(user, image_path, caption=new_ad_setails))
    log_helper(str(num_new_ads) + ' new ads')
    for user in TELEGRAM_USERS:
    #send telegram message if their new ads
        if num_new_ads > 2:
            loop.run_until_complete(send_text_to_telegram(user, str(num_new_ads) + ' מודעות חדשות נמצאו '))
    n = open(NEW_ADS_FILE, 'w', encoding='utf-8')
    json.dump(new_ads_dict, n,  ensure_ascii=False)
    n.close()
    update_db_file()

async def send_text_to_telegram(user, text):
    await bot.send_message(user, text)

async def send_image_to_telegram(user, file, caption=None):
    await bot.send_file(user, file, caption=caption)


def update_db_file():
    # read input file
    full = open(FULL_DB_FILE, "rt", encoding='utf-8')
    # read file contents to string
    data_full = full.read()
    # close the input file
    full.close()
    # read input file
    new = open(NEW_ADS_FILE, "rt", encoding='utf-8')
    # read file contents to string
    data_new = new.read()
    # replace all occurrences of the required string
    data_update = data_full + data_new
    while '}}{' in data_update:
        data_update = data_update.replace('}}{', '}, ')
    while '} }{' in data_update:
        data_update = data_update.replace('} }{', '}, ')
    if '}, }' in data_update[-10:]:
        data_update = data_update.replace('}, }', '} }')
    # close the input file
    new.close()
    # open the input file in write mode
    update_full = open(FULL_DB_FILE, "w", encoding='utf-8')
    # overrite the input file with the resulting data
    update_full.write(data_update)
    # close the file
    update_full.close()

def send_request(url):
    response = requests.get(
        url="https://app.scrapingbee.com/api/v1/",
        params={
            "api_key": scrapingbee_token,
            "url": url,
            "render_js": "False",
        },

    )
    with open(HTML_FILE, 'w', encoding='utf-8') as f:
        f.write(response.text)

def main():
    num_pages_to_scan = PAGES_TO_SCAN
    for i in range(1, num_pages_to_scan + 1):
        url_to_scan = URL_TO_SCAN
        if i == 1:
            send_request(url_to_scan)
            print("working on " + url_to_scan)
            get_id()
        else:
            url_to_scan += '&page=' + str(i)
            send_request(url_to_scan)
            print("working on " + url_to_scan)
            do_scan = get_id()
            if not do_scan:
                break
    json_data = json.dumps(all_data_dict, ensure_ascii=False)
    with open(HOURLY_DB_FILE, 'w', encoding='utf-8') as file:
        file.write(json_data)
    find_new_ads(FULL_DB_FILE, HOURLY_DB_FILE)


if __name__ == '__main__':
    main()
