from bs4 import BeautifulSoup
import requests
import urllib.request
import os
import json
import time
import shutil
from os import listdir
from PIL import Image
import pymysql

def scrape_set(link, series, set_id):
    jp_set = {series: []}
    source = requests.get(link).text
    soup = BeautifulSoup(source, 'lxml')

    links = []
    card_base_link = 'https://jp.pokellector.com'
    # get all card links
    for card in soup.find_all('div', class_ = 'card'):
        links.append(card_base_link + card.a['href'])

    num = 1
    for l in links:
        try:
            source = requests.get(l).text
            soup = BeautifulSoup(source, 'lxml')
            card_name = soup.find('h1', class_ = 'icon set').text
            info = soup.select_one('div[class="infoblurb"]').find_all('div')
            rarity = None
            card_set = None
            numbe = None
            number = None
            for inf in info:
                if 'Rarity:' in inf.text:
                    rarity = inf.text.replace('Rarity: ', '').strip()
                elif 'Set:' in inf.text:
                    card_set = inf.text.replace('Set: ', '').strip()
                elif 'Card:' in inf.text:
                    numbe = inf.text.replace('Card: ', '').strip()
            number = numbe[:numbe.find('/')] if numbe else str(num)
            num += 1
            rarity = rarity if rarity else ''
            card_set = card_set if card_set else ''
            card_id = f'jp-{set_id}-{number}'
            card_name = card_name[:card_name.find('#') if '#' in card_name else len(card_name)].strip()
            try:
                image = soup.find('div', class_ = 'content cardinfo').div.img['src']
            except:
                image = ''
                print(card_name, 'no image')
            # TODO change rarities cuz some are different, Secret Rare instead of Rare Secret
            rarities = ['Common', 'LEGEND', 'None', 'Rare', 'Rare ACE', 'Rare BREAK', 'Rare Holo', 'EX',
                        'GX', 'Rare Prime', 'Rare Promo', 'Rare Rainbow', 'Rare Secret',
                        'Rare Ultra', 'Shining', 'Uncommon', 'V', 'VM', 'Amazing Rare']
            changed = {'Secret Rare': 'Rare Secret', 'Ultra Rare': 'Rare Ultra', 'Prism Star': 'Rare'} # tf is prism star -- just made them rare
            if card_name.endswith(' EX'):
                rarity = 'EX'
            elif card_name.endswith(' GX'):
                rarity = 'GX'
            elif card_name.endswith(' BREAK'):
                rarity = 'Rare BREAK'
            elif card_name.endswith(' V'):
                rarity = 'V'
            elif card_name.endswith(' VMAX'):
                rarity = 'VM'
            if rarity not in rarities:
                rarity = changed[rarity]
            jp_set[series].append({'id': card_id, 'name': card_name, 'series': series,
                                    'set': card_set, 'rarity': rarity, 'set_code': set_id,
                                    'image': image, 'types': '', 'super_type': 'Pokémon'})
            time.sleep(1)
        except Exception as e:
            print(e)
    with open('jp_cards.json', 'w', encoding = 'utf-8') as f:
        json.dump(jp_set, f, indent = 4, ensure_ascii = False)

def get_images():
    with open('jp_cards.json', 'r') as f:
        data = json.load(f)
    for sets in data: # in case multiple sets in json
        cards = data[sets]
        for card in cards:
            time.sleep(0.5)
            if card['image']:
                response = requests.get(card['image'], stream=True)
                with open(r'pics\{}.png'.format(card['id']), 'wb') as out_file:
                    shutil.copyfileobj(response.raw, out_file)
                del response
            else:# no card image -- use back card
                im1 = Image.open('back.webp')
                im1.save('cards\{}.webp'.format(card['id']))
                im1.close()
    # change them to webp
    for fileName in listdir('pics/'):
        im1 = Image.open('pics/{}'.format(fileName))
        im1.save(f"cards/{fileName.replace('png', 'webp')}")
        im1.close()

def read_db_credentials(): # reads rds db credentials from a text file
    creds = {}
    with open('db_credentials.txt', 'r') as f:
        lines = f.readlines()
        creds['rds_host'] = lines[0][:len(lines[0])-1] # remove \n at end
        creds['dbusername'] = lines[1][:len(lines[1])-1]
        creds['password'] = lines[2][:len(lines[2])-1]
        creds['db_name'] = lines[3]
    return creds

def into_database():
    try:
        creds = read_db_credentials()
        connection = pymysql.connect(  creds['rds_host'], user = creds['dbusername'],
                                            passwd = creds['password'], db = creds['db_name'], 
                                            connect_timeout = 5, charset = 'utf8')
    except Exception as e:
        print('Unable to connect to database -- {}'.format(e))
        return

    with open('jp_cards.json', 'r', encoding = 'utf-8') as f:
        data = json.load(f)
    for sets in data:
        cards = data[sets]
        cursor = connection.cursor()
        # insert set
        set_info = cards[0]
        cursor.execute('''insert into pokemon_cards_set(name, code, series, total_cards) 
                        values(%s,%s,%s,%s)''', ['JP ' + set_info['set'], set_info['set_code'], set_info['series'], len(cards)])
        connection.commit()
        # insert cards
        for card in cards:
            card_id = card['id']
            name = card['name'].strip()
            series = card['series']
            card_set = 'JP ' + card['set']
            rarity = card['rarity']
            set_code = card['set_code']
            types = card['types'] if card['types'] else None
            super_type = card['super_type']
            cursor.execute('''insert into pokemon_cards(id, name, types, super_type, rarity, series, pc_set, set_code, obtainable) 
                                values(%s,%s,%s,%s,%s,%s,%s,%s,%s)''', [card_id, name, types, super_type, rarity, series, card_set, set_code, 'no'])
        connection.commit()

if __name__ == '__main__':
    link = 'https://jp.pokellector.com/sets/S4-Electrifying-Tackle'
    series = 'Sword & Shield' # change series if changing to another seires
    set_code = 's4' # change setcode for each link
    #scrape_set(link, series, set_code)
    #get_images()
    #into_database()

    # TODO find rainbow cards using PIL, detect if similar to rainbow

    # TODO check if pokecollector logo on card, then switch to a diff picture
    # can use pokemon official card but in ajpanese vpn for the card images

    # TODO get Sword and shield promos, at end of series
    