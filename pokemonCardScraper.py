from bs4 import BeautifulSoup
import requests
import urllib.request
import os
import boto3
import botocore
import json
import pymysql
import time
import csv
import time
from PIL import Image
from os import listdir
import imagehash
from pprint import pprint

#rds settings
rds_host  = ''
name = ''
password = ''
db_name = ''
# connect to rds
try:
    conn = pymysql.connect(rds_host, user=name, passwd=password, db=db_name, connect_timeout=5)
    cur = conn.cursor()
except pymysql.MySQLError as e:
    print('fail')
except:
    print('fail')

def scrape_and_input(currentID, db):
    source = requests.get('https://www.tcgcollector.com/cards/{}'.format(currentID)).text
    soup = BeautifulSoup(source, 'lxml')

    image = soup.find('div', id = 'card-image-container').img['src'] # get image url
    name = soup.find('h1', id = 'page-header-title').text # get card name
    if_poke = soup.find('span', id = 'card-box-title')
    if if_poke: # get card box title for pokemon
        if if_poke.a:
            cardBoxTitle = if_poke.a.text
        else:
            cardBoxTitle = if_poke.text.strip()
    else:
        cardBoxTitle = ''
    evolvesFrom = ''
    evolveData = soup.find('span', id = 'card-box-evolves-from') # gets evovles from, if on card
    if evolveData:
        evolvesFrom = evolveData.a.em.text
    if_hp = soup.find('span', id = 'card-box-hp')
    hp = ''
    if if_hp:
        hp = if_hp.text.replace('HP', '').replace(' ', '') # gets the hp

    energyTypesData = soup.find('span', id = 'card-box-energy-types') # can have multiple types
    energyTypes = []
    if energyTypesData:
        for types in energyTypesData.find_all('img'):
            energyTypes.append(types['alt'])

    effect = {} # afaik only one card effect like ability or held item
    effectData = soup.find('div', class_='card-box-effect')
    if effectData:
        effect['name'] = effectData.h3.text
        effect['description'] = effectData.p.text

    description = [] # for non pokemon description
    for desc in soup.find_all('p', id = 'card-box-description'):
        description.append(desc.text.replace('\n', ''))

    attacks = [] # can have multiple attacks
    for move in soup.find_all('div', class_='card-box-attack'):
        attack = {}
        attack['name'] = move.find('h3', class_='card-box-attack-name').text
        if move.find('span', class_='card-box-attack-damage'):
            attack['damage'] = move.find('span', class_='card-box-attack-damage').text
        descriptionData = move.find('p', class_='card-box-attack-description')
        if descriptionData: # some attacks dont have descriptions
            attack['description'] = move.find('p', class_='card-box-attack-description').text
        attack['types'] = []
        for types in move.find('span', class_='card-box-attack-energy').find_all('img'):
            attack['types'].append(types['alt'])
        attacks.append(attack)

    rules = [] # can have rules, can also have multiple rules
    for rule in soup.find_all('li', class_='card-box-rule'):
        rules.append(rule.text)

    weakness = [] # gets the weakness
    get_weakness = soup.find('div', id = 'card-box-weakness')
    if get_weakness:
        for weak in get_weakness.div.find_all('div', class_='card-box-footer-item-entry'):
            weakType = weak.img['alt']
            weakAmt = weak.span.text
            weakness.append('{} {}'.format(weakType, weakAmt))

    resistance = [] # gets resistance
    get_resistance = soup.find('div', id = 'card-box-resistance')
    if get_resistance:
        for resist in get_resistance.div.find_all('div', class_='card-box-footer-item-entry'):
            resistType = resist.img['alt']
            resistAmt = resist.span.text
            resistance.append('{} {}'.format(resistType, resistAmt))

    retreatCost = [] # gets retreat
    get_retreatCost = soup.find('div', id = 'card-box-retreat-cost')
    if get_retreatCost:
        for retreat in get_retreatCost.div.find_all('div', class_='card-box-footer-item-entry'):
            retreatCost.append(retreat.img['alt'])

    expansion = []
    cardType = []
    rarity = []
    cardFormat = []
    illustrator = []
    for info in soup.find_all('div', class_='card-info-item'): # gets all relevant info from this scope
        if info.h2.text == 'Expansion':
            expData = info.span.text.replace('\n', '').split('-')
            expansion.append('{} - {}'.format(expData[0].strip(), expData[1].replace(' ', '')))
        elif info.h2.text == 'Card Type':
            for types in info.find_all('a'):
                cardType.append(types.text)
        elif info.h2.text == 'Rarity':
            rarity.append(info.span.a.text)
        elif info.h2.text == 'Format':
            for formats in info.find_all('a'):
                cardFormat.append(formats.text)
        elif info.h2.text == 'Illustrator':
            illustrator.append(info.span.a.text)
    
    notPokemon = [  'Energy ◇' , 'Basic Energy', 'Special Energy', 'Team Plasma Energy',
                    'Ace Spec', 'Full Art Trainer', 'Goldenrod Game Corner', 'Item',
                    'Pokémon Tool', 'Rainbow Trainer', "Rocket's Secret Machine", "Rocket's Secret Robot",
                    'Stadium', 'Supporter', 'Team Flare Gear', 'Team Flare Hyper Gear', 'Team Plasma Trainer',
                    'Technical Machine', 'Trainer', 'Trainer TAG TEAM', 'Trainer ◇']
    
    # check if pokemon or not
    if any(types in cardType for types in notPokemon):
        # check for values that may not exist, if htey dont then input None instead
        if not name:
            name = 'None'
        if not expansion:
            expansion = ['None']
        else:
            expansion = '-'.join(expansion)
        if not cardBoxTitle:
            cardBoxTitle = 'None'
        if not description:
            description = 'None'
        else:
            description = '\n'.join(description)
        if not rules:
            rules = 'None'
        else:
            rules = '\n'.join(rules)
        if not cardType:
            cardType = 'None'
        else:
            cardType = '-'.join(cardType)
        if not rarity:
            rarity = 'None'
        else:
            rarity = '-'.join(rarity)
        if not cardFormat:
            cardFormat = 'None'
        else:
            cardFormat = '-'.join(cardFormat)
        if not illustrator:
            illustrator = 'None'
        else:
            illustrator = '-'.join(illustrator)
        #input to not pokemon table
        db.execute('''insert into nonpokemon(   name, expansion, card_box_title, description, rules, card_type
                                                rarity, format, illustrator, tcg_id)
                            values(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)''', [ name, expansion, cardBoxTitle, description, rules,
                                                                        cardType, rarity, cardFormat, illustrator, int(currentID)])
        conn.commit()
        # get primary key for image naming
        query = 'select id, name from nonpokemon where tcg_id = %s'
        db.execute(query % currentID)
        for row in db:
            db_id = row[0]
            db_name = row[1]
    else:
        # check for values that may not exist, if htey dont then input None instead
        if not name:
            name = 'None'
        if not expansion:
            expansion = ['None']
        else:
            expansion = '-'.join(expansion)
        if not energyTypes:
            energyTypes = ['None']
        else:
            energyTypes = '-'.join(energyTypes)
        if not hp:
            hp = '0'
        if not cardBoxTitle:
            cardBoxTitle = 'None'
        if not evolvesFrom:
            evolvesFrom = 'None'
        if not effect:
            effect = 'None'
        else:
            effect = '{}\n{}'.format(effect['name'], effect['description'])
        inputAttacks = ''
        for attack in attacks:
            inputAttacks += '{}/{}'.format('-'.join(attack['types']), attack['name'])
            if 'damage' in attack:
                inputAttacks += '/{}\n'.format(attack['damage'])
            else:
                inputAttacks += '\n'
            if 'description' in attack:
                inputAttacks += '{}\n'.format(attack['description'])
        if not inputAttacks:
            inputAttacks = 'None'
        if not rules:
            rules = 'None'
        else:
            rules = '\n'.join(rules)
        if not weakness:
            weakness = 'None'
        else:
            weakness = '-'.join(weakness)
        if not resistance:
            resistance = 'None'
        else:
            resistance = '-'.join(resistance)
        if not retreatCost:
            retreatCost = 'None'
        else:
            retreatCost = '-'.join(retreatCost)
        if not cardType:
            cardType = 'None'
        else:
            cardType = '-'.join(cardType)
        if not rarity:
            rarity = 'None'
        else:
            rarity = '-'.join(rarity)
        if not cardFormat:
            cardFormat = 'None'
        else:
            cardFormat = '-'.join(cardFormat)
        if not illustrator:
            illustrator = 'None'
        else:
            illustrator = '-'.join(illustrator)
        
        # input to pokemon table
        db.execute('''insert into pokemon(    name, expansion, energy_types, hp, card_box_title, evolves_from, effect,
                                            attacks, rules, weakness, resistance, retreat_cost, card_type, rarity,
                                            format, illustrator, tcg_id) 
                    values(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)''', [name, expansion, energyTypes, int(hp), cardBoxTitle,
                                                                                    evolvesFrom, effect, inputAttacks, rules, weakness,
                                                                                    resistance, retreatCost, cardType, rarity, cardFormat,
                                                                                    illustrator, int(currentID)])
        conn.commit()
        # get primary key for image naming
        query = 'select id, name from pokemon where tcg_id = %s'
        db.execute(query % currentID)
        for row in db:
            db_id = row[0]
            db_name = row[1]
    # download image with the name with primary key and name of pokemon
    if image:
        urllib.request.urlretrieve(image, 'img\{}-{}.jpg'.format(db_id, db_name))

def scrape1_input(site, insert):
    source = requests.get(site).text
    soup = BeautifulSoup(source, 'lxml')
    cards = soup.find_all('article', class_ = 'card card-list-item')
    for card in cards:
        tcg_id = card.get('id').replace('card-', '')
        name = card.find('div', class_='card-list-item-entry card-list-item-name').a.text
        number1 = card.find('div', class_='card-list-item-entry card-list-item-number').span.text
        if '/' in number1:
            number = number1[:number1.find('/')]
        else:
            number = number1
        expansion = card.find('div', class_='card-list-item-entry card-list-item-expansion').span.text
        card_type1 = card.find('div', class_='card-list-item-entry card-list-item-card-type').span.text.replace('\n', '').strip().split('-')
        card_type2 = [x.strip() for x in card_type1]
        card_type = '-'.join(card_type2)
        rarity = card.find('div', class_='card-list-item-entry card-list-item-rarity').span.text.strip()
        if insert:
            cur.execute('''insert into cards(name, expansion, card_number, card_type, rarity, tcg_id)
                            values(%s,%s,%s,%s,%s,%s)''', [name, expansion, number, card_type, rarity, tcg_id])
            conn.commit()
        else:
            print('{}-{}-{}-{}-{}-{}'.format(name, number, expansion, card_type, rarity, tcg_id))
    print(len(cards))

def download_images(cards):
    for card in cards:
        source = requests.get('https://www.tcgcollector.com/cards/{}'.format(card['tcg_id'])).text
        soup = BeautifulSoup(source, 'lxml')
        image = soup.find('div', id = 'card-image-container').img['src'] # get image url
        # download image with the name with primary key and name of pokemon
        if image:
            urllib.request.urlretrieve(image, 'images\{}-{}.jpg'.format(card['expansion'], card['number']))
        time.sleep(0.2)

def read_csv(file):
    i = 0
    cards = []
    with open(file, 'r') as f:
        reader = csv.reader(f, delimiter=',')
        for row in reader:
            if i == 0: # first line
                i += 1
            else:
                cards.append({'expansion':row[0], 'number':row[1], 'tcg_id':row[2]})
    return cards

def get_wrong_broken_images():
        hash1 = imagehash.average_hash(Image.open('back.jpg'))
        cutoff = 5
        similar = []
        broken = []
        for fileName in listdir('{}/images'.format(os.getcwd())):
                try:
                        hash2 = imagehash.average_hash(Image.open('images/{}'.format(fileName)))
                        if hash1 - hash2 < cutoff:
                                similar.append(fileName)
                                print('image similar -- {}'.format(fileName))
                except:
                        broken.append(fileName)
                        print('image broken -- {}'.format(fileName))

        print('Similar:')
        pprint(similar)
        print(len(similar))
        return similar

def delete_from_table(broken):
    for card in broken:
        card_i = card.split('-')
        expansion = card_i[0]
        number = card_i[1].replace('.jpg', '')
        cur.execute('delete from good_cards where expansion = %s and card_number = %s', [expansion, number])
        conn.commit()

if __name__ == '__main__':
    #in https://www.tcgcollector.com/expansions#expansion-series-19
    # didnt include unnumbered promos, box toppers, swordshield/teamup/sunmoon/diamondpearl energies

    # 602 broken cards deleted from cards, resulting is in good_cards
    pass