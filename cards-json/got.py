# game of thrones ccg
import json
from pprint import pprint
import pymysql
import urllib.request
import time
import os
import requests
import shutil

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
    with open('got.json', 'r') as f:
        data = json.load(f)
    packs = {}
    amt = 0
    for card in data:
        if card['image_url'] == 'None' or card['image_url'] is None:
            continue
        pack_code = card['pack_code'].lower()
        if pack_code in packs:
            packs[pack_code] += 1
        else:
            packs[pack_code] = 1
        card_id = '{}-{}'.format(pack_code, packs[pack_code])
        ci = int(card['ci']) if 'ci' in card and not isinstance(card['ci'], type(None)) else None
        claim = int(card['claim']) if 'claim' in card and not isinstance(card['claim'], type(None)) else None
        cost = int(card['cost']) if 'cost' in card and not isinstance(card['cost'], type(None)) else None
        designer = card['designer'] if 'designer' in card and not isinstance(card['designer'], type(None)) else None
        faction_name = card['faction_name'] if 'faction_name' in card and not isinstance(card['faction_name'], type(None)) else None
        flavor = card['flavor'] if 'flavor' in card and not isinstance(card['flavor'], type(None)) else None
        illustrator = card['illustrator'] if 'illustrator' in card and not isinstance(card['illustrator'], type(None)) else None
        income = int(card['income']) if 'income' in card and not isinstance(card['income'], type(None)) else None
        initiative = int(card['initiative']) if 'initiative' in card and not isinstance(card['initiative'], type(None)) else None
        label = card['label'] if 'label' in card else None
        name = card['name']
        pack_name = card['pack_name']
        reserve = int(card['reserve']) if 'reserve' in card and not isinstance(card['reserve'], type(None)) else None
        si = int(card['si']) if 'si' in card and not isinstance(card['si'], type(None)) else None
        strength = int(card['strength']) if 'strength' in card and not isinstance(card['strength'], type(None)) else None
        text = card['text'] if 'text' in card and not isinstance(card['text'], type(None)) else None
        traits = card['traits'] if 'traits' in card and not isinstance(card['traits'], type(None)) else None
        type_name = card['type_name'] if 'type_name' in card and not isinstance(card['type_name'], type(None)) else None
        cursor.execute('''insert into got(id,name,pack_code,pack_name,ci,claim,cost,designer,faction_name,flavor,illustrator,income,
                                            initiative,label,reserve,si,strength,card_text,traits,type_name) 
                                            values(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)''', 
                                            [card_id, name, pack_code, pack_name, ci, claim, cost, designer, faction_name, flavor,
                                            illustrator, income, initiative, label, reserve, si, strength, text, traits, type_name])
        amt += 1
        if amt % 250 == 0:
            connection.commit()
    connection.commit()

if __name__ == '__main__':
    # 1413 cards
    # 1383 cards with images
    #to_database()
    with open('images.json', 'r') as f:
        data = json.load(f)
    data = data[1000:]
    broken = []
    for card in data:
        r = requests.get(card['image'], stream = True)
        if r.status_code == 200:
            with open('got\{}.jpg'.format(card['id']), 'wb') as f:
                r.raw.decode_content = True
                shutil.copyfileobj(r.raw, f)
        else:
            print('error')
            broken.append(card['id'])
        time.sleep(0.3)
        '''
        try:
            urllib.request.urlretrieve(card['image'], r'got\{}.jpg'.format(card['id']))
        except Exception as e:
            broken.append(card['id'])
            print(card['image'])
            print(e)
        time.sleep(0.3)
        '''
        pass
    with open('broken.json', 'a') as f:
        json.dump(broken, f)
        f.write('\n')