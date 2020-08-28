import json
from pprint import pprint
import pymysql
import urllib.request
import time

def to_database():
    try:
        creds = {'rds_host': '', 'dbusername': '',
                    'password': '', 'db_name': ''}
        connection = pymysql.connect(  creds['rds_host'], user = creds['dbusername'],
                                            passwd = creds['password'], db = creds['db_name'], 
                                            connect_timeout = 5, charset = 'utf8')
    except Exception as e:
        print(e)

    with open('cards.json', 'r') as f:
        data = json.load(f)

    cursor = connection.cursor()
    i = 0
    cards = {}
    dup = ['Skill Card', 'Spell Card', 'Spirit Monster', 'Synchro Monster',
            'Toon Monster', 'Tuner Monster']
    img = []
    for card in data['data']:
        i += 1
        if card['type'] in dup:
            c_ty = card['type'].lower().split(' ')
            c_typ = c_ty[0][0:2]
            c_type = ''.join(c_typ) + ''.join(x[0] for x in c_ty[1:])
        else:
            c_ty = card['type'].lower().split(' ')
            c_type = ''.join([x[0] for x in c_ty])
        if c_type in cards:
            cards[c_type] += 1
        else:
            cards[c_type] = 1
        # make id of card -- type-number
        card_id = '{}-{}'.format(c_type, cards[c_type])
        name = card['name']
        card_type = card['type']
        desc = card['desc']
        attack = card['atk'] if 'atk' in card else None
        defense = card['def'] if 'def' in card else None
        level = card['level'] if 'level' in card else None
        race = card['race']
        attribute = card['attribute'] if 'attribute' in card else None
        sets = []
        # cards have different rarity depending on the set it appears on
        # so included in sets -- set #{rarity}
        if 'card_sets' in card:
            for s in card['card_sets']:
                sets.append(s['set_name'] + ' #' + s['set_rarity'])
            sets = '|'.join(sets)
        else:
            sets = None
        images = len(card['card_images']) # some have multiple 
        if images > 1:
            x = 1
            for image in card['card_images']:
                img.append({'id': '{}_{}'.format(card_id, x), 'url': image['image_url']})
                cursor.execute('''insert into yugioh(id, name, card_type, description,
                            atk, def, card_level, race, card_attribute, card_sets) 
                            values(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)''', 
                            ['{}_{}'.format(card_id, x), name, card_type, desc, attack, defense,
                            level, race, attribute, sets])
                connection.commit()
                x += 1
        else:
            img.append({'id': card_id, 'url': card['card_images'][0]['image_url']})
            cursor.execute('''insert into yugioh(id, name, card_type, description,
                            atk, def, card_level, race, card_attribute, card_sets) 
                            values(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)''', 
                            [card_id, name, card_type, desc, attack, defense,
                            level, race, attribute, sets])
            connection.commit()

if __name__ == '__main__':
    # to_database()
    with open('img.json', 'r') as f:
        data = json.load(f)
    images = data[10000:]
    broken = []
    for image in images:
        try:
            urllib.request.urlretrieve(image['url'], r'yugioh\{}.jpg'.format(image['id']))
        except:
            broken.append(image)
            print(image)
        time.sleep(0.2)
    with open('broken.json', 'a') as f:
        json.dump(broken, f)
        f.write('\n')