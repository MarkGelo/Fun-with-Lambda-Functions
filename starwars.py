# star wars ccg
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
    with open('starwars.json', 'r') as f:
        data = json.load(f)
    sets = {}
    amt = 0
    for card in data:
        if 'image_url' not in card:
            continue
        set_code = card['set_code']
        if set_code in sets:
            sets[set_code] += 1
        else:
            sets[set_code] = 1
        card_id = '{}-{}'.format(set_code, sets[set_code])
        ability = int(card['ability']) if 'ability' in card and not isinstance(card['ability'],type(None)) else None
        armor = int(card['armor']) if 'armor' in card and not isinstance(card['armor'], type(None)) else None
        characteristics = card['characteristics'] if 'characteristics' in card else None
        defense_value = card['defense_value'] if 'defense_value' in card else None
        defense_value_name = card['defense_value_name'] if 'defense_value_name' in card else None
        deploy = int(card['deploy']) if 'deploy' in card and not isinstance(card['deploy'], type(None)) else None
        destiny = int(card['destiny']) if 'destiny' in card and not isinstance(card['destiny'], type(None)) else None
        ferocity = card['ferocity'] if 'ferocity' in card else None
        force_aptitude = card['force_aptitude'] if 'force_aptitude' in card else None
        forfeit = int(card['forfeit']) if 'forfeit' in card and not isinstance(card['forfeit'], type(None)) else None
        card_text = card['gametext'] if 'gametext' in card else None
        icon = card['icon'] if 'icon' in card else None
        label = card['label'] if 'label' in card else None
        hyperspeed = card['hyperspeed'] if 'hyperspeed' in card else None
        landspeed = card['landspeed'] if 'landspeed' in card else None
        lore = card['lore'] if 'lore' in card else None
        maneuver = int(card['maneuver']) if 'maneuver' in card and not isinstance(card['maneuver'], type(None)) else None
        model_type = card['model_type'] if 'model_type' in card else None
        name = card['name'].strip()
        politics = int(card['politics']) if 'politics' in card and not isinstance(card['politics'], type(None)) else None
        position = int(card['position']) if 'position' in card and not isinstance(card['position'], type(None)) else None
        power = int(card['power']) if 'power' in card and not isinstance(card['power'], type(None)) else None
        rarity = card['rarity_name'] if 'rarity_name' in card else None
        set_name = card['set_name']
        side = card['side_name'] if 'side_name' in card else None
        subtype_name = card['subtype_name'] if 'subtype_name' in card else None
        type_name = card['type_name'] if 'type_name' in card else None
        cursor.execute('''insert into starwars(id,name,ability,armor,card_characteristics,defense_value,defense_value_name,deploy,destiny,
                                                ferocity,force_aptitude,forfeit,card_text,icon,label,hyperspeed,landspeed,lore,maneuver,
                                                model_type,politics,card_position,card_power,rarity,set_name,set_code,side,subtype_name,type_name) 
                                                values(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)''',
                                                [card_id, name, ability, armor, characteristics, defense_value, defense_value_name, deploy,
                                                destiny, ferocity, force_aptitude, forfeit, card_text, icon, label, hyperspeed, landspeed,
                                                lore, maneuver, model_type, politics, position, power, rarity, set_name, set_code, side,
                                                subtype_name, type_name])
        amt += 1
        if amt % 250 == 0:
            connection.commit()
    connection.commit()


if __name__ == '__main__':
    # 2517 cards
    # 2517 cards with images
    #to_database()
    with open('images.json', 'r') as f:
        data = json.load(f)
    data = data[1000:]
    broken = []
    for card in data:
        try:
            urllib.request.urlretrieve(card['image'], r'starwars\{}.jpg'.format(card['id']))
        except Exception as e:
            broken.append(card['id'])
            print(card['image'])
            print(e)
        time.sleep(0.3)
    with open('broken.json', 'a') as f:
        json.dump(broken, f)
        f.write('\n')