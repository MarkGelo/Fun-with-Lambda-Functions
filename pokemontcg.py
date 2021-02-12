import urllib.request
import os
import json
import pymysql
import time
from pprint import pprint
from dateutil import parser
import shutil
import requests
from os import listdir
from pokemontcgsdk import Card
from pokemontcgsdk import Set
from pokemontcgsdk import Type
from pokemontcgsdk import Supertype
from pokemontcgsdk import Subtype
from PIL import Image
from os import listdir

creds = {}
creds['rds_host'] = 'firstdatabase.criup5fig9lz.us-east-1.rds.amazonaws.com'
creds['dbusername'] = 'admin'
creds['password'] = 'Uv1qUXCFUVmRHScCn7DQ'
creds['db_name'] = 'cards'
# connect to rds
try:
    conn = pymysql.connect(creds['rds_host'], user=creds['dbusername'], passwd=creds['password'], db=creds['db_name'], 
                            connect_timeout=5, charset = 'utf8')
except pymysql.MySQLError as e:
    print('fail to connect')
except:
    print('fail to connect')

def new_set(set_):
    new_set_ = Set.where(name = set_)
    cards = Card.where(set = set_)
    for card in cards:
        input_card(card)

def input_card(card): # add card to db
    try:
        db = conn.cursor()
        pc_id = card.id
        name = card.name
        national_pokedex_number = card.national_pokedex_number
        if card.types: # can be none, error when trying to join
            types = ','.join(card.types)
        else:
            types = card.types
        sub_type = card.subtype
        super_type = card.supertype
        if card.hp and card.hp != 'None':
            hp = int(card.hp)
        else:
            hp = None
        if card.number:
            pc_number = card.number
        else:
            pc_number = None
        artist = card.artist
        rarity = card.rarity
        series = card.series
        pc_set = card.set
        set_code = card.set_code
        if card.retreat_cost: # can be none
            retreat_cost = ','.join(card.retreat_cost)
        else:
            retreat_cost = card.retreat_cost
        converted_retreat_cost = card.converted_retreat_cost
        if card.text:
            pc_text = '\n'.join(card.text)
        else:
            pc_text = card.text
        if card.attacks:
            # doesnt necessarily have to have dmg
            if 'damage' in card.attacks:
                if 'text' in card.attacks:
                    attacks = '\n'.join(['{}-{}-{}\n{}'.format(','.join(attack['cost']), attack['name'], attack['damage'], attack['text']) for attack in card.attacks])
                else:
                    attacks = '\n'.join(['{}-{}-{}'.format(','.join(attack['cost']), attack['name'], attack['damage']) for attack in card.attacks])
            else:
                if 'text' in card.attacks:
                    attacks = '\n'.join(['{}-{}\n{}'.format(','.join(attack['cost']), attack['name'], attack['text']) for attack in card.attacks])
                else:
                    attacks = '\n'.join(['{}-{}'.format(','.join(attack['cost']), attack['name']) for attack in card.attacks])
        else:
            attacks = card.attacks
        if card.weaknesses:
            weakness = ','.join(['{} {}'.format(weak['type'], weak['value']) for weak in card.weaknesses])
        else:
            weakness = card.weaknesses
        if card.resistances:
            resistances = ','.join(['{} {}'.format(resist['type'], resist['value']) for resist in card.resistances])
        else:
            resistances = card.resistances
        if card.ability:
            # doesnt necessarily have a type.. how about texT?
            if 'type' in card.ability:
                ability = '{} {}\n{}'.format(card.ability['type'], card.ability['name'], card.ability['text']) # only one ability so no need for new line at end
            else:
                ability = '{}\n{}'.format(card.ability['name'], card.ability['text'])
        else:
            ability = card.ability
        if card.ancient_trait:
            ancient_trait = '{}\n{}'.format(card.ancient_trait['name'], card.ancient_trait['text']) # only one trait so no need for new line at end
        else:
            ancient_trait = card.ancient_trait
        evolves_from = card.evolves_from
        image_url = card.image_url
        image_url_hi_res = card.image_url_hi_res
        db.execute('''insert into pokemon(    id, name, national_pokedex_number, types, sub_type, super_type, hp, pc_number,
                                                    artist, rarity, series, pc_set, set_code, retreat_cost, converted_retreat_cost,
                                                    pc_text, attacks, weakness, resistances, ability, ancient_trait, evolves_from,
                                                    image_url, image_url_hi_res)
                            values (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)''',
                                                    [   pc_id, name, national_pokedex_number, types, sub_type, super_type, hp, pc_number,
                                                        artist, rarity, series, pc_set, set_code, retreat_cost, converted_retreat_cost,
                                                        pc_text, attacks, weakness, resistances ,ability, ancient_trait, evolves_from,
                                                        image_url, image_url_hi_res])
        conn.commit()
        # download image, check if hi res or not,
        time.sleep(0.5)
        if image_url_hi_res:
            response = requests.get(image_url_hi_res, stream=True)
            with open(r'new\{}.png'.format(pc_id), 'wb') as out_file:
                shutil.copyfileobj(response.raw, out_file)
            del response
        elif image_url:
            response = requests.get(image_url, stream=True)
            with open(r'new\{}.png'.format(pc_id), 'wb') as out_file:
                shutil.copyfileobj(response.raw, out_file)
            del response
        else:
            print('error - {}'.format(pc_id))
    except Exception as e:
        print(e)
        print('ERROR - {}'.format(card.id))
        file1 = open('error.txt', 'a')
        file1.write('{}\n'.format(card.id))
        file1.close()
    except:
        print('error - {}'.format(card.id))

def get_all_id(): # get all ids of cards from db
    db = conn.cursor()
    db.execute('select id from pokemon_cards')
    ids = []
    for row in db:
        ids.append(row[0])
    return ids

def get_images(): # get all card id from images -- to make sure got one image for each card
    files = []
    for fileName in listdir('{}\img'.format(os.getcwd())):
        files.append(fileName.replace('.png', ''))
    return files

if __name__ == '__main__':
    '''
    sets = Set.all()
    sets = [x.name for x in sets]
    #test = len(sets[:30]) + len(sets[30:60]) + len(sets[60:90]) + len(sets[90:])
    for card_set in sets[90:]:
        new_set(card_set)
    '''
    for fileName in listdir('new/'):
        try:
            im1 = Image.open('new/{}'.format(fileName))
            im1.save(f"new_webp/{fileName.replace('png', 'webp')}")
            im1.close()
        except Exception as e:
            print(fileName, e)
    
    

