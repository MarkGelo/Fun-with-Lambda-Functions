import json
from pprint import pprint
import pymysql
import time
import os
from os import listdir

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
    with open('hearthstone.json', 'r', encoding = 'utf8') as f:
        data = json.load(f)
    files = []
    for fileName in listdir('{}/hearthstone'.format(os.getcwd())):
        files.append(fileName.replace('.png', ''))
    amt = 0
    change_sets = {'BOOMSDAY': 'BD', 'BRM': 'BRM', 'CORE': 'CO', 'DALARAN': 'DA', 'EXPERT1': 'EX', 'GANGS': 'GA',
                    'GILNEAS': 'GI', 'GVG': 'GVG', 'HERO_SKINS': 'HERO', 'HOF': 'HOF', 'ICECROWN': 'ICE', 
                    'KARA': 'KARA', 'LOE': 'LOE', 'LOOTAPALOOZA': 'LOO', 'NAXX': 'NAXX', 'OG': 'OG',
                    'TGT': 'TGT', 'TROLL': 'TR', 'ULDUM': 'UL', 'UNGORO': 'UN'}
    sets = {}
    cursor = connection.cursor()
    for card in data:
        if str(card['dbfId']) in files:
            card_set_id = change_sets[card['set']]
            if card_set_id in sets:
                sets[card_set_id] += 1
            else:
                sets[card_set_id] = 1
            card_id = '{}-{}'.format(card_set_id, sets[card_set_id])
            name = card['name']
            rarity = card['rarity'] if 'rarity' in card else None
            card_set = card['set']
            card_type = card['type']
            card_class = card['cardClass']
            attack = int(card['attack']) if 'attack' in card else None
            cost = int(card['cost']) if 'cost' in card else None
            health = int(card['health']) if 'health' in card else None
            dbf_id = card['dbfId']
            artist = card['artist'] if 'artist' in card else None
            flavor = card['flavor'] if 'flavor' in card else None
            race = card['race'] if 'race' in card else None
            text = card['text'] if 'text' in card else None
            mechanics = '|'.join(card['mechanics']) if 'mechanics' in card else None
            referenced_tags = '|'.join(card['referencedTags']) if 'referencedTags' in card else None
            targeting_arrow_text = card['targetingArrowText'] if 'targetingArrowText' in card else None
            # insert in to db
            cursor.execute('''insert into hearthstone(id,name,rarity,card_set,card_type,card_class,attack,
                                                    cost,health,dbf_id,artist,flavor,race,card_text,mechanics,
                                                    referenced_tags,targeting_arrow_text) 
                                                    values(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)''', 
                                                    [card_id, name, rarity, card_set, card_type, card_class, attack,
                                                    cost, health, dbf_id, artist, flavor, race, text, mechanics,
                                                    referenced_tags, targeting_arrow_text])
            amt += 1
            if amt % 500 == 0:
                connection.commit()
    connection.commit()

def change_images_names_to_ids():
    with open('hearthstone.json', 'r', encoding = 'utf8') as f:
        data = json.load(f)
    files = []
    for fileName in listdir('{}/hearthstone'.format(os.getcwd())):
        files.append(fileName.replace('.png', ''))
    amt = 0
    change_sets = {'BOOMSDAY': 'BD', 'BRM': 'BRM', 'CORE': 'CO', 'DALARAN': 'DA', 'EXPERT1': 'EX', 'GANGS': 'GA',
                    'GILNEAS': 'GI', 'GVG': 'GVG', 'HERO_SKINS': 'HERO', 'HOF': 'HOF', 'ICECROWN': 'ICE', 
                    'KARA': 'KARA', 'LOE': 'LOE', 'LOOTAPALOOZA': 'LOO', 'NAXX': 'NAXX', 'OG': 'OG',
                    'TGT': 'TGT', 'TROLL': 'TR', 'ULDUM': 'UL', 'UNGORO': 'UN'}
    sets = {}
    for card in data:
        if str(card['dbfId']) in files:
            amt += 1
            card_set_id = change_sets[card['set']]
            if card_set_id in sets:
                sets[card_set_id] += 1
            else:
                sets[card_set_id] = 1
            card_id = '{}-{}'.format(card_set_id, sets[card_set_id])
            # change names of images to card_id
            os.rename(r'hearthstone\{}.png'.format(card['dbfId']), r'hearthstone\{}.png'.format(card_id))

if __name__ == '__main__':
    # 20 sets
    # 2947 cards
    change_images_names_to_ids()