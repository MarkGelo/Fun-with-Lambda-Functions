import json
from pprint import pprint
import pymysql
import urllib.request
import time
import os

def to_database(card_set):
    try:
        creds = {'rds_host': '', 'dbusername': '',
                    'password': '', 'db_name': ''}
        connection = pymysql.connect(  creds['rds_host'], user = creds['dbusername'],
                                            passwd = creds['password'], db = creds['db_name'], 
                                            connect_timeout = 5, charset = 'utf8')
    except Exception as e:
        print(e)
    cursor = connection.cursor()

    with open('set{}.json'.format(card_set), 'r', encoding="utf8") as f:
        data = json.load(f)

    for card in data:
        card_id = card['cardCode']
        name = card['name']
        region = card['region'] if card['region'] else None
        cost = int(card['cost'])
        attack = int(card['attack'])
        health = int(card['health'])
        description = card['descriptionRaw'] if card['descriptionRaw'] else None
        levelupdescription = card['levelupDescriptionRaw'] if card['levelupDescriptionRaw'] else None
        flavortext = card['flavorText'] if card['flavorText'] else None
        artist = card['artistName'] if card['artistName'] else None
        keywords = '|'.join(card['keywords']) if card['keywords'] else None
        spellspeed = card['spellSpeed'] if card['spellSpeed'] else None
        rarity = card['rarity'] if card['rarity'] else None
        subtypes = '|'.join(card['subtypes']) if card['subtypes'] else None
        supertype = card['supertype'] if card['supertype'] else None
        card_type = card['type'] if card['type'] else None
        collectible = card['collectible']
        
        cursor.execute('''insert into lor(id, name, card_set, region, cost, attack, health ,description, level_up_description,
                                        flavor_text, artistname, keywords, spell_speed, rarity, subtypes, supertype,
                                        card_type, collectible) values(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)''',
                                        [card_id, name, card_set, region, cost, attack, health, description, levelupdescription,
                                        flavortext, artist, keywords, spellspeed, rarity, subtypes, supertype, card_type, collectible])
        connection.commit()

if __name__ == '__main__':
    to_database(1)