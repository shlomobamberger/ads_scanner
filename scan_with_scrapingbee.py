import asyncio
import json
import os
import urllib.request
import requests
from telethon import TelegramClient
from datetime import datetime
import re
import time

now = datetime.now()
current_time_int = int(now.strftime("20%y%m%d"))
mission_name = 'items'
NEAR_CITY_FILE = "near_cities.txt"
FULL_DB_FILE = rf"{mission_name}_full_scan_db.json"
HOURLY_DB_FILE = rf"{mission_name}_hourly_scan_db.json"
NEW_ADS_FILE = rf"{mission_name}_new_ads.json"
LOG_FILE = rf"{mission_name}_log file.txt"
HTML_FILE = rf"{mission_name}_html_file.html"
URLS_TO_SCAN = rf"{mission_name}_urls_to_scan.txt"
IMAGES_FOLDER = rf"{mission_name}_images"
DEFAULT_NUM_PAGES_TO_SCAN = 1
TELEGRAM_USERS = ('',)  ## CHANGE ME
api_id = int ## CHANGE ME
api_hash = 'str'  ## CHANGE ME
bot_api = 'str'   ## CHANGE ME
client = TelegramClient('', api_id, api_hash)  ## CHANGE ME
scrapingbee_token = 'str'  ## CHANGE ME
###########################################################################################

bot = TelegramClient('bot', api_id, api_hash).start(bot_token=bot_api)
all_data_dict = {}
num_new_ads = 0
num_ads_to_scan = 0


def log_helper(text):
    now = datetime.now()
    current_time = now.strftime("[%Y-%m-%d]   [%H:%M:%S]")
    log_line = current_time + '   ' + str(text) + '\n'
    with open(LOG_FILE, 'a', encoding='utf-8') as f:
        f.write(log_line)


def check_nececry_files():
    if not os.path.exists(f'{mission_name}_images'):
        log_helper('create images folder')
        os.makedirs(f'{mission_name}_images')
    if not os.path.exists(FULL_DB_FILE):
        log_helper(f'create {FULL_DB_FILE}')
        with open(FULL_DB_FILE, 'a') as f:
            f = json.dump({'empty': 'empty'}, f)


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
            ad_details(HTML_FILE)
            return True


def ad_details(filename):
    id_and_ad = {}
    with open(filename, 'r', encoding='utf-8') as html:
        html = html.read()
        content = "".join(re.findall(r'orderPlaceholder(.+?)seoText', html))
        content = content.replace(',{id:', ',\n{id:')
        with open(rf"{mission_name}_dict.json", 'w', encoding='utf-8') as s:
            s.write(content)
    with open(rf"{mission_name}_dict.json", 'r', encoding='utf-8') as d:
        for line in d:
            ad_dict = {}
            privet_or_seller = "פרטי"
            if 'merchant_name' in line:
                privet_or_seller = 'עסקי'
            id_ad = "".join(re.findall(r'{id:"(.+?)",data:', line))
            coordinates = "".join(re.findall(r'coordinates:{(.+?)"},row_1:', line))
            title = "".join(re.findall(r'row_1:"(.+?)",title_1:', line))
            description = "".join(re.findall(r'title_1:"(.+?)",title_2:', line))
            city = "".join(re.findall(r',row_2:"(.+?)",row_3', line))
            product_condition = "".join(re.findall(r',line_2:"(.+?)",external', line))
            category_name = "".join(re.findall(r'SalesSubCatID_text:"(.+?)",ManufacturID_text', line))
            contact_name = "".join(re.findall(r'contact_name:"(.+?)",', line))
            price = "".join(re.findall(r'price:"(.+?)"', line))
            ad_number = "".join(re.findall(r'ad_number:(.+?),area_id', line))
            record_id = int("".join(re.findall(r'record_id:(.+?),', line)))
            img_url = "".join(re.findall(r'img_url:"(.+?)",', line)).replace('u002F', '')
            img_url = img_url.replace('\\', '/')
            all_item_images = "".join(re.findall(r'images:\[(.+?)],images_urls', line)).replace('u002F', '')
            all_item_images = all_item_images.replace('\\', '/').split(',')

            join_date_noneread = "".join(re.findall(r'_20.+?.jp', img_url))[1:-3]
            join_date_year = join_date_noneread[:4].rstrip()
            join_date_month = join_date_noneread[4:6].rstrip()
            join_date_day = join_date_noneread[6:8].rstrip()
            join_date_hour = join_date_noneread[8:10].rstrip()
            join_date_minute = join_date_noneread[10:12].rstrip()
            join_date_second = join_date_noneread[12:14].rstrip()
            join_date = "".join(join_date_year + '-' + join_date_month + '-' + join_date_day)
            join_date_int = join_date_year + join_date_month + join_date_day
            join_time = ''.join(join_date_hour + ':' + join_date_minute + ':' + join_date_second)
            ad_entry_time = join_date + ' ' + join_time

            ad_dict['privet_or_seller'] = privet_or_seller
            ad_dict['coordinates'] = coordinates
            ad_dict['title'] = title
            ad_dict['privet_or_seller'] = privet_or_seller
            ad_dict['city'] = city
            ad_dict['id'] = id_ad
            ad_dict['product_condition'] = product_condition
            ad_dict['direct_link'] = r'https://www.yad2.co.il/item/' + id_ad
            ad_dict['description'] = description
            ad_dict['price'] = price
            ad_dict['ad_number'] = ad_number
            ad_dict['category_name'] = category_name
            ad_dict['contact_name'] = contact_name
            ad_dict['ad_entry_time'] = ad_entry_time
            ad_dict['all_item_images'] = all_item_images
            ad_dict['img_url'] = img_url
            id_and_ad[id_ad] = ad_dict
    all_data_dict.update(id_and_ad)
    json_data = json.dumps(all_data_dict, ensure_ascii=False)
    with open(HOURLY_DB_FILE, 'w', encoding='utf-8') as file:
        file.write(json_data)
    find_new_ads(FULL_DB_FILE, HOURLY_DB_FILE)


def find_new_ads(oldfile, newfile):
    global num_new_ads, num_ads_to_scan
    num_ads_to_scan = 0
    num_new_ads = 0
    new_ads_dict = {}
    loop = asyncio.get_event_loop()
    with open(oldfile, 'r', encoding='utf-8') as f:
        o = json.load(f)
    with open(newfile, 'r', encoding='utf-8') as f:
        n = json.load(f)
    with open(NEAR_CITY_FILE, 'r', encoding='utf-8') as city:
        city_list = city.read().replace('\n', '')
    for i in n:
        num_ads_to_scan += 1
        if (i not in o) and (n[i]['privet_or_seller'] == 'פרטי'):
            num_new_ads += 1
            if n[i]['city'] in city_list:
                n[i]['city'] += ' ✅ קרוב'
            else:
                n[i]['city'] += ' ❌ רחוק'
            label = n[i]['category_name'] + ' ב' + n[i]['city']
            new_ad_details = ('**' + label + '**' + '\n' +
                              'תיאור: ' + n[i]['title'] + '\n' +
                              '** מחיר: ' + n[i]['price'] + '**\n' +
                              'איש קשר: ' + n[i]['contact_name'] + '\n' +
                              'לפרטים: ' + n[i]['direct_link'])
            new_ads_dict[i] = n[i]
            for user in TELEGRAM_USERS:
                images_to_send = []
                if len(n[i]['all_item_images'][0]) > 0:  # todo fix that
                    # for image in n[i]['all_item_images']:
                    #    if n[i]['all_item_images'].index(image) < 3:
                    #       image_path = os.path.join(IMAGES_FOLDER, str(n[i]['all_item_images'].index(image)) + n[i]['id'] + ".jpg")
                    #       image_url = n[i]['all_item_images'][n[i]['all_item_images'].index(image)][1:-1]
                    #       urllib.request.urlretrieve(image_url, image_path)
                    #       images_to_send.append(image_path)
                    image_path = os.path.join(IMAGES_FOLDER, n[i]['id'] + ".jpg")
                    image_url = n[i]['all_item_images'][0]
                    urllib.request.urlretrieve(image_url[1:-1], image_path)
                    images_to_send.append(image_path)
                    loop.run_until_complete(send_image_to_telegram(user, images_to_send, caption=new_ad_details))
                else:
                    loop.run_until_complete(send_text_to_telegram(user, new_ad_details))
    n = open(NEW_ADS_FILE, 'w', encoding='utf-8')
    json.dump(new_ads_dict, n, ensure_ascii=False)
    n.close()
    update_db_file()


async def send_text_to_telegram(user, text):
    await bot.send_message(user, text)


async def send_image_to_telegram(user, file, caption=None):
    await bot.send_file(user, file, caption=caption)


def update_db_file():
    # read input file
    with open(FULL_DB_FILE, 'r', encoding='utf-8') as full_db:
        full = json.load(full_db)
    with open(HOURLY_DB_FILE, 'r', encoding='utf-8') as temp_db:
        temp = json.load(temp_db)
    combined = {**full, **temp}
    with open(FULL_DB_FILE, 'w', encoding='utf-8') as full_db:
        json.dump(combined, full_db, ensure_ascii=False)


def send_request(url):
    response = requests.get(
        url="https://app.scrapingbee.com/api/v1/",
        params={
            "api_key": scrapingbee_token,
            "url": url,
            "render_js": "False"
            # "premium_proxy": "true",
            # "country_code": "il"
        },
    )
    with open(HTML_FILE, 'w', encoding='utf-8') as f:
        f.write(response.text)


def create_urls_list():
    with open(URLS_TO_SCAN, 'r', encoding='utf-8') as f:
        urls_in_file = f.readlines()
    urls = []
    for line in urls_in_file:
        if '###' not in line:
            line = line.rstrip()
            line = line.split("(")
            url = line[0].rstrip()
            if len(line) > 1:
                num_pages_to_scan = int(line[1][:-1])
            else:
                num_pages_to_scan = DEFAULT_NUM_PAGES_TO_SCAN
            urls.append(url)  # always add the basic url to list
            if num_pages_to_scan > 1:
                for i in range(2, num_pages_to_scan + 1):
                    if "&page=" not in url:
                        urls.append(url + '&page=' + str(i))
                    else:
                        s = url.index('page=')
                        page_number = int(url[s + 5:]) + i - 1
                        urls.append(url[:s + 5] + str(page_number))
    return urls


def remove_files():
    for filename in os.listdir(IMAGES_FOLDER):
        file_path = os.path.join(IMAGES_FOLDER, filename)
        os.unlink(file_path)
    os.unlink(HTML_FILE)
    os.unlink(HOURLY_DB_FILE)
    os.unlink(rf"{mission_name}_dict.json")
    os.unlink(NEW_ADS_FILE)


def main():
    check_nececry_files()
    main.PAGES_TO_SCAN = 1
    for i in create_urls_list():
        send_request(i)
        print("working on " + i)
        get_id()
    log_helper(str(num_new_ads) + ' new ads were found out of ' + str(num_ads_to_scan) + ' scanned')
    remove_files()


if __name__ == '__main__':
    # while True:
    main()
    # time.sleep(30)
