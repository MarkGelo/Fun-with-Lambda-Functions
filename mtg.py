import json
from pprint import pprint
import pymysql
import urllib.request
import time
from mtgsdk import Card
from mtgsdk import Set
from mtgsdk import Type
from mtgsdk import Supertype
from mtgsdk import Subtype
from mtgsdk import Changelog

def to_database():
    try:
        creds = {'rds_host': '', 'dbusername': '',
                    'password': '', 'db_name': ''}
        connection = pymysql.connect(  creds['rds_host'], user = creds['dbusername'],
                                            passwd = creds['password'], db = creds['db_name'], 
                                            connect_timeout = 5, charset = 'utf8')
        print('connected')
    except Exception as e:
        print(e)

    with open('cards.json', 'r', encoding="utf8") as f:
        data = json.load(f)
    ids = {}
    cursor = connection.cursor()
    amt = 0
    for card in data:
        # all have same vars
        artist = card['artist'] if card['artist'] else None
        cmc = card['cmc'] if card['cmc'] else None
        color_identity = '|'.join(card['color_identity']) if card['color_identity'] else None
        colors = '|'.join(card['colors']) if card['colors'] else None
        flavor = card['flavor'] if card['flavor'] else None
        hand = card['hand'] if card['hand'] else None
        life = card['life'] if card['life'] else None
        loyalty = card['loyalty'] if card['loyalty'] else None
        mana_cost = card['mana_cost'] if card['mana_cost'] else None
        name = card['name']
        names = '|'.join(card['names']) if card['names'] else None
        number = card['number'] if card['number'] else None
        printings = '|'.join(card['printings']) if card['printings'] else None
        original_type = card['original_type'] if card['original_type'] else None
        power = card['power'] if card['power'] else None
        rarity = card['rarity'] if card['rarity'] else None
        card_set = card['set'] if card['set'] else None
        card_set_name = card['set_name'] if card['set_name'] else None
        subtypes = '|'.join(card['subtypes']) if card['subtypes'] else None
        supertypes = '|'.join(card['supertypes']) if card['supertypes'] else None
        text = card['text'] if card['text'] else None
        toughness = card['toughness'] if card['toughness'] else None
        card_type = card['type'] if card['type'] else None
        types = '|'.join(card['types']) if card['types'] else None
        if '{}-{}'.format(card_set, number) in ids:
            temp = '{}-{}'.format(card_set, number)
            card_id = '{}-{}_{}'.format(card_set, number, ids[temp])
            ids[card_id] = 1
            ids[temp] += 1
        else:
            card_id = '{}-{}'.format(card_set, number)
            ids[card_id] = 1
        # add to db
        cursor.execute('''insert into mtg(  id, name, card_set_name, card_type, card_types, artist, cmc, sub_types, super_types, 
                                            rarity, card_set, card_number, printings, original_type, names, card_text, toughness, 
                                            color_identity, colors, flavor, hand, life, loyalty, mana_cost, card_power) 
                                            values(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)''', 
                                            [card_id, name, card_set_name, card_type, types, artist, cmc, subtypes, supertypes,
                                            rarity, card_set, number, printings, original_type, names, text, toughness, color_identity,
                                            colors, flavor, hand, life, loyalty, mana_cost, power])
        amt += 1
        if amt % 500 == 0:
            connection.commit()
    connection.commit()

if __name__ == '__main__':
    # https://github.com/MagicTheGathering/mtg-sdk-python
    # 51430 cards total cards
    # 38274 cards with images
    with open('images.json', 'r') as f:
        data = json.load(f)
    images = data[38270:]
    broken = []
    for image in images:
        try:
            urllib.request.urlretrieve(image['image'], r'mtg\{}.jpg'.format(image['id']))
        except Exception as e:
            broken.append(image)
            print(image['url'])
            print(e)
        time.sleep(0.3)
    with open('broken.json', 'a') as f:
        json.dump(broken, f)
        f.write('\n')