import re
import json
import requests
import logging
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
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
          'Cazoo Baskonia Vitoria-Gasteiz': {},
          'Crvena Zvezda Meridianbet Belgrade': {},
          'Partizan Mozzart Bet Belgrade': {},
          'FC Barcelona': {},
          'FC Bayern Munich': {},
          'Fenerbahce Beko Istanbul': {},
          'LDLC ASVEL Villeurbanne': {},
          'Maccabi Playtika Tel Aviv': {},
          'Olympiacos Piraeus': {},
          'Panathinaikos Athens': {},
          'Real Madrid': {},
          'Valencia Basket': {},
          'Zalgiris Kaunas': {},
          'Virtus Segafredo Bologna': {}}

latin_num = ('I', 'II', 'III', 'IV', 'V', 'VI', 'VII', 'VIII', 'IX', 'X')

for index in range(1, 14):
    with open(f'C:\\Users\\Thomas\\Desktop\\JSONs\\{index}.json', encoding='utf8') as f:
        d = json.load(f)
        data = d['data']
        for i in range(len(data)):
            person = data[i]['person']
            name = person['name']
            code = person['code']
            club = data[i]['club']['name']
            split_n = name.split(',')
            _ = split_n[1].split(' ')[1]
            split_n[1] = _
            split_n[0], split_n[1] = split_n[1], split_n[0]
            name = split_n

            n = ''
            r = re.compile(r"[^\W\d]+")
            for j in range(len(name)):
                for _ in r.findall(name[j]):
                    if _ not in latin_num:
                        _ = _.title()
                        n += _ + ' '
                    else:
                        n += _
            fixed_name = n.rstrip()
            dashed_name = fixed_name.lower().replace(' ', '-')
            base_url = f'https://www.euroleaguebasketball.net/euroleague/players/{dashed_name}/{code}/'

            try:
                session = requests.Session()
                retry = Retry(connect=3, backoff_factor=0.5)
                adapter = HTTPAdapter(max_retries=retry)
                session.mount('http://', adapter)
                session.mount('https://', adapter)
                response = session.get(base_url)
            except requests.exceptions.HTTPError as http_error:
                logging.warning('HTTP error occurred: {}'.format(http_error))
            except requests.exceptions.ConnectTimeout as conn_timeout:
                logging.warning('Connection timed-out: {}'.format(conn_timeout))
            except Exception as e:
                logging.warning(e)
            else:
                tree = etree.HTML(response.content)
                photo_urls = tree.xpath('//div[@class="player-hero_inner__1-bR2 side-gaps_sectionSideGaps__1ylL0"]'
                                        '//div[@class="player-hero_imageWrap__161BQ cover-contain_ofCover__3K_IS"]//img//@data-srcset')
                try:
                    photo_url = photo_urls[0].split(',')[0]
                except IndexError as idx_err:
                    logging.warning(f' {fixed_name}:' + ' Url probably non-existent: [ERROR] {}'.format(idx_err))
                else:
                    photo_url_fixed = re.search("(?P<url>https?://[^\s]+)", photo_url).group("url")
                    photo_url_fixed = photo_url_fixed.replace('=webp', '=png')
                # print(photo_url_fixed)
                    roster[club][fixed_name] = base_url, photo_url_fixed
    print(f'JSON file {index} processed!')
print(roster)

with open("roster.json", "w") as outfile:
    json.dump(roster, outfile, indent=4)

# with open('roster.json') as json_file:
#     data = json.load(json_file)
