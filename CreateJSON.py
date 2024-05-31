import os
import re
import json
import requests
import logging
from lxml import etree

# from json2html import *

logging.getLogger().setLevel(logging.INFO)

# with open('C:\\Users\\Thomas\\Desktop\\JSONs\\2.json', encoding='utf8') as f:
#     d = json.load(f)
#     e = json2html.convert(json=d)
#     g = ("C:\\Users\\Thomas\\Desktop\\JSONs\\2.html")
#     with open(g, "w") as file:
#         file.write(str(e))
#         print("yes") #to see if the code worked

roster = {'ALBA Berlin': {},
          'Anadolu Efes Istanbul': {},
          'AS Monaco': {},
          'EA7 Emporio Armani Milan': {},
          'Baskonia Vitoria-Gasteiz': {},
          'Crvena Zvezda Meridianbet Belgrade': {},
          'Partizan Mozzart Bet Belgrade': {},
          'FC Barcelona': {},
          'FC Bayern Munich': {},
          'Fenerbahce Beko Istanbul': {},
          'LDLC ASVEL Villeurbanne': {},
          'Maccabi Playtika Tel Aviv': {},
          'Olympiacos Piraeus': {},
          'Panathinaikos AKTOR Athens': {},
          'Real Madrid': {},
          'Valencia Basket': {},
          'Zalgiris Kaunas': {},
          'Virtus Segafredo Bologna': {}}

latin_num = ('I', 'II', 'III', 'IV', 'V', 'VI', 'VII', 'VIII', 'IX', 'X', 'JR', 'Iv')
players_count = 0
json_files_count = 0

for root, dirs, files in os.walk('C:\\Users\\Thomas\\Desktop\\JSONs\\2023-24'):
    for file in files:
        if file.endswith('.json'):
            json_files_count += 1

print(f'\nJSON files to be processed: {json_files_count}\n')

for index in range(1, json_files_count + 1):
    with open(f'C:\\Users\\Thomas\\Desktop\\JSONs\\2023-24\\{index}.json', encoding='utf8') as f:
        d = json.load(f)
        data = d['data']
        for i in range(len(data)):
            person = data[i]['person']
            name = person['name']
            code = person['code']
            club = data[i]['club']['name']
            split_n = re.findall(r'\w+', name)
            name = split_n

            suffix = str()
            fixed_name = str()
            log = bool(False)
            if len(name) == 2:
                name = name[::-1]
                for _ in name:
                    if _ not in latin_num:
                        fixed_name += _.capitalize() + " "
            if len(name) == 3:
                name = name[::-1]
                for _ in name:
                    if _ in latin_num:
                        suffix = _
                        log = True
                        fixed_name = str()
                        break
                if log:
                    name.pop(name.index(suffix))
                    for k in name:
                        fixed_name += k.capitalize() + " "
                    fixed_name += suffix
                if not log:
                    name[1], name[2] = name[2], name[1]
                    for k in name:
                        fixed_name += k.capitalize() + " "

            fixed_name = fixed_name.rstrip()
            dashed_name = fixed_name.lower().replace(' ', '-')
            base_url = f'https://www.euroleaguebasketball.net/euroleague/players/{dashed_name}/{code}/'
            players_count += 1

            try:
                response = requests.get(base_url, timeout=(30, 30))
            except requests.exceptions.HTTPError as http_error:
                logging.warning('HTTP error occurred: {}'.format(http_error))
            except requests.exceptions.ConnectTimeout as conn_timeout:
                logging.warning('Connection timed-out: {}'.format(conn_timeout))
            except Exception as e:
                logging.warning(e)
            else:
                tree = etree.HTML(response.content)
                photo_urls = tree.xpath('//div[@class="player-hero_inner__rwwR_ side-gaps_sectionSideGaps__v5CKj"]'
                                        '//div[@class="player-hero_imageWrap__h_4aj cover-contain_ofCover__PuYyp"]//img//@data-srcset')
                try:
                    photo_url = photo_urls[0].split(',')[0]
                except IndexError as idx_err:
                    logging.warning(f' {fixed_name}:' + ' Photo url probably non-existent: [ERROR] {}'.format(idx_err))
                    photo_url_fixed = ''
                    roster[club][fixed_name] = base_url, photo_url_fixed
                    print(roster[club][fixed_name])
                else:
                    photo_url_fixed = re.search(r"(?P<url>https?://\S+)", photo_url).group("url")
                    photo_url_fixed = photo_url_fixed.replace('=webp', '=png')
                    roster[club][fixed_name] = base_url, photo_url_fixed
    print(f'\nJSON file {index} processed!\n')
print(roster)
print(f'\nPlayers processed: {players_count}')
print(f'JSON files processed: {json_files_count}')

with open('C:\\Users\\Thomas\\Desktop\\JSONs\\2023-24\\roster.json', "w") as outfile:
    json.dump(roster, outfile, indent=4)

# with open('roster.json') as json_file:
#     data = json.load(json_file)
