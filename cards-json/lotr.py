# lord of the rings ccg
import json
from pprint import pprint
import pymysql
import urllib.request
import time
import os

def to_database():
    try:
        creds = {'rds_host': '', 'dbusername': '',
                    'password': '', 'db_name': ''}
        connection = pymysql.connect(  creds['rds_host'], user = creds['dbusername'],
                                            passwd = creds['password'], db = creds['db_name'], 
                                            connect_timeout = 5, charset = 'utf8')
    except Exception as e:
        print(e)
    cursor = connection.cursor()

    with open('lotr.json', 'r') as f:
        data = json.load(f)
    packs = {}
    amt = 0
    for card in data:
        if 'imagesrc' not in card:
            continue
        if card['pack_code'].lower() in packs:
            packs[card['pack_code'].lower()] += 1
        else:
            packs[card['pack_code'].lower()] = 1
        pack_code = card['pack_code'].lower()
        card_id = '{}-{}'.format(pack_code, packs[pack_code])
        name = card['name']
        pack_name = card['pack_name'] if 'pack_name' in card else None
        attack = int(card['attack']) if 'attack' in card else None
        health = int(card['health']) if 'health' in card else None
        defense = int(card['defense']) if 'defense' in card else None
        flavor = card['flavor'] if 'flavor' in card else None
        illustrator = card['illustrator'] if 'illustrator' in card else None
        sphere_name = card['sphere_name'] if 'sphere_name' in card else None
        text = card['text'] if 'text' in card else None
        threat = int(card['threat']) if 'threat' in card else None
        traits = card['traits'] if 'traits' in card else None
        type_name = card['type_name'] if 'type_name' in card else None
        willpower = int(card['willpower']) if 'willpower' in card else None
        cursor.execute('''insert into lotr(id, name, pack_name, pack_code, attack, health, defense, flavor, illustrator,
                                            sphere_name, card_text, threat, traits, type_name, willpower) 
                                            values(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)''',
                                            [card_id, name, pack_name, pack_code,attack, health, defense, flavor, illustrator,
                                            sphere_name, text, threat, traits, type_name, willpower])
        amt += 1
        if amt % 250 == 0:
            connection.commit()
    connection.commit()

if __name__ == '__main__':
    # 988 total cards
    # 971 with images
    #to_database()
    with open('images.json', 'r') as f:
        data = json.load(f)
    data = data[100:]
    broken = []
    for card in data:
        card_id = card['id']
        image = card['image']
        BASE = 'https://ringsdb.com'
        site = '{}{}'.format(BASE, image)
        try:
            urllib.request.urlretrieve(site, r'lotr\{}.png'.format(card_id))
        except Exception as e:
            broken.append(card_id)
            print(site)
            print(e)
        time.sleep(0.3)
    with open('broken.json', 'a') as f:
        json.dump(broken, f)
        f.write('\n')
