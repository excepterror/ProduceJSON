import os
import re
import json
import requests
import logging
import time
from lxml import etree

GREEN = '\033[1;32m'
YELLOW = '\033[1;33m'
MAGENTA = '\033[1;35m'
RESET = '\033[0m'

logging.basicConfig(format='%(message)s',  level=logging.INFO)

latin_num = ('I', 'II', 'III', 'IV', 'V', 'VI', 'VII', 'VIII', 'IX', 'X', 'JR', 'Iv')

# --- Roster template ---
def initialize_roster():
    return {
        'ALBA Berlin': {},
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
        'Paris Basketball': {},
        'Zalgiris Kaunas': {},
        'Virtus Segafredo Bologna': {}
    }

# --- Normalize player name ---
def normalize_name(name_list):
    fixed_name = ''
    if len(name_list) == 2:
        name_list = name_list[::-1]
        fixed_name = ' '.join(_.capitalize() for _ in name_list)
    elif len(name_list) == 3:
        name_list = name_list[::-1]
        for n in name_list:
            if n in latin_num:
                suffix = n
                name_list.remove(n)
                fixed_name = ' '.join(_.capitalize() for _ in name_list) + f' {suffix}'
                break
        else:
            name_list[1], name_list[2] = name_list[2], name_list[1]
            fixed_name = ' '.join(_.capitalize() for _ in name_list)
    return fixed_name.strip()

# --- Construct player page URL ---
def build_player_url(fixed_name, code):
    dashed_name = fixed_name.lower().replace(' ', '-')
    return f'https://www.euroleaguebasketball.net/euroleague/players/{dashed_name}/{code}/'

# --- Extract photo URL from player's webpage ---
def extract_photo_url(page_content):
    tree = etree.HTML(page_content)
    photo_urls = tree.xpath('//div[@class="player-hero_inner__xxqLy side-gaps_sectionSideGaps__8hmjO"]'
                            '//div[@class="player-hero_imageWrap__OT5kR cover-contain_ofCover__PTqTb"]//img//@data-srcset')
    if not photo_urls:
        raise IndexError("No photo URL found")
    photo_url = photo_urls[0].split(',')[0]
    photo_url_fixed = re.search(r"(?P<url>https?://\S+)", photo_url).group("url")
    return photo_url_fixed.replace('=webp', '=png')

# --- Process a single JSON file ---
def process_json_file(filepath, roster, players_count):
    with open(filepath, encoding='utf8') as f:
        d = json.load(f)
        data = d['data']
        for item in data:
            person = item['person']
            name = person['name']
            code = person['code']
            club = item['club']['name']
            split_n = re.findall(r'\w+', name)

            fixed_name = normalize_name(split_n)
            base_url = build_player_url(fixed_name, code)
            players_count += 1

            try:
                response = requests.get(base_url, timeout=(30, 30))
                response.raise_for_status()
                photo_url = extract_photo_url(response.content)
            except Exception as e:
                logging.warning(f'\n[{YELLOW}WARNING{RESET}] {fixed_name}: Could not fetch photo or page. [ERROR] {e}\n')
                photo_url = ''

            roster[club][fixed_name] = base_url, photo_url
            logging.info(f'[{GREEN}INFO{RESET}] {club} - {fixed_name}: {base_url}, {photo_url}')

            time.sleep(0.5)  # Optional delay
    return players_count

# --- Main routine ---
def main():
    directory = 'C:\\Users\\Thomas\\Desktop\\JSONs\\2024-25'
    roster = initialize_roster()
    players_count = 0
    json_files = [f for f in os.listdir(directory) if f.endswith('.json')]

    logging.info(f'[{GREEN}INFO{RESET}] JSON files to be processed: {len(json_files)}\n')

    for idx, file in enumerate(sorted(json_files, key=lambda x: int(x.replace('.json', ''))), 1):
        filepath = os.path.join(directory, file)
        players_count = process_json_file(filepath, roster, players_count)
        logging.info(f'\n[{GREEN}INFO{RESET}] {MAGENTA}JSON file {idx} processed!{RESET}\n')

    logging.info(f'[{GREEN}INFO{RESET}] {YELLOW}Roster:{RESET}{roster}')
    logging.info(f'\n[{GREEN}INFO{RESET}] {MAGENTA}Players processed:{RESET} {players_count}')
    logging.info(f'[{GREEN}INFO{RESET}] JSON files processed: {len(json_files)}')

    with open(os.path.join(directory, 'roster.json'), "w", encoding='utf8') as outfile:
        json.dump(roster, outfile, indent=4, ensure_ascii=False)

if __name__ == '__main__':
    main()
