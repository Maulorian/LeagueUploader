import json
import logging
from io import BytesIO

import PIL
import cassiopeia
import requests
from cassiopeia import get_champion, Region
from PIL import Image, ImageDraw, ImageFilter, ImageFont

import lib.managers.upload_manager as upload_manager

FLAGS_PATH = upload_manager.PROJECT_PATH + '/assets/flags/'
TIER_PATH = upload_manager.PROJECT_PATH + '/assets/tiers/'
SUMMONERS_PATH = upload_manager.PROJECT_PATH + '/assets/summoners/'
RUNES_PATH = upload_manager.PROJECT_PATH + '/assets/runes/'
TREES_PATH = 'trees/'
ITEMS_PATH = upload_manager.PROJECT_PATH + '/assets/items/'
SPLASH_PATH = 'splash_art.jpeg'
FONT_PATH = upload_manager.PROJECT_PATH + '/fonts/thumbnail_font.ttf'

RUNES_URL = 'http://ddragon.leagueoflegends.com/cdn/10.19.1/data/en_US/runesReforged.json'
DRAGON_URL = 'https://ddragon.leagueoflegends.com/cdn/img/'

STROKE_WIDTH = 3
ALPHA_VALUE = 200
logger = logging.getLogger(upload_manager.LOG_NAME)


def save_champion_splashart(champion, skin_name):
    logger.info(f'[{__name__.upper()}] - Retrieving splash art for {champion} skin {skin_name}')

    champion = get_champion(champion, Region.europe_west)
    skins = champion.skins
    skin = next(skin_data for skin_data in skins if skin_data.name == skin_name)
    with open(SPLASH_PATH, 'wb') as f:
        skin.splash.save(f)


def get_flag_image(region):
    flag = Image.open(f'{FLAGS_PATH}{region}.png')

    return flag


def paste_with_center_coords(img, to_paste, x, y):
    img.paste(to_paste, (int(x - to_paste.width // 2), int(y - to_paste.height // 2)), mask=to_paste.convert("RGBA"))


def get_rank_image(rank_info_area, tier, lp):
    rank_info_area_width = rank_info_area.width // 2
    rank_info_area_height = rank_info_area.height
    rank_info_area = Image.new('RGBA', (rank_info_area_width, rank_info_area_height), (0, 0, 0))
    rank_info_area.putalpha(0)

    tier_image = get_tier_image(rank_info_area, tier)
    lp_image = get_lp_image(rank_info_area, lp)

    paste_with_center_coords(rank_info_area, tier_image, rank_info_area_width / 2, rank_info_area_height * 0.375)

    paste_with_center_coords(rank_info_area, lp_image, rank_info_area_width / 2, rank_info_area_height * 0.825)
    return rank_info_area


def get_rank_region_info_area(info_area, match_info):
    tier = match_info['tier']
    lp = match_info['lp']
    region = match_info['region']

    rank_info_area_width = info_area.width
    rank_info_area_height = int(0.35 * info_area.height)

    rank_info_area = Image.new('RGBA', (rank_info_area_width, rank_info_area_height), (0, 0, 0))
    rank_info_area.putalpha(ALPHA_VALUE)

    rank_image = get_rank_image(rank_info_area, tier, lp)


    width = int(rank_info_area.width * 0.3)
    maxsize = (width, width)
    region_image = get_flag_image(region)
    region_image = region_image.resize(maxsize, Image.ANTIALIAS)

    paste_with_center_coords(rank_info_area, rank_image, (rank_info_area_width / 4) * 1, rank_info_area_height / 2)
    paste_with_center_coords(rank_info_area, region_image, (rank_info_area_width / 4) * 3, rank_info_area_height / 2)

    return rank_info_area

def get_tier_image(rank_info_area, tier):
    tier = Image.open(f'{TIER_PATH}{tier}.png')
    aspect_ratio = tier.width / tier.height
    tier_height = int(rank_info_area.height * 0.7)
    tier_width = int(tier_height * aspect_ratio)
    maxsize = (tier_width, tier_height)
    tier = tier.resize(maxsize, Image.ANTIALIAS)
    # paste_with_center_coords(info_area, tier, info_area.width / 2, info_area.width / 2)

    return tier


def get_champion_name_image(info_area, champion_name: str, role):
    champion_name_height = info_area.height

    champion_name_image = Image.new('RGBA', (info_area.width, champion_name_height), (0, 0, 0))
    champion_name_image.putalpha(0)

    draw = ImageDraw.Draw(champion_name_image)

    text = f'{champion_name.upper()}'

    font = ImageFont.truetype(FONT_PATH, int(info_area.width * 0.16))
    w, h = draw.textsize(text, font=font)

    draw.text(((info_area.width - w) / 2, (champion_name_height - h) / 2), text, (255, 255, 255), font=font, stroke_width=STROKE_WIDTH, stroke_fill=(0, 0, 0))
    return champion_name_image


def get_lp_image(info_area, lp):
    lp_image_height = int(info_area.height * 0.5)

    lp_image = Image.new('RGBA', (info_area.width, lp_image_height), (0, 0, 0))
    lp_image.putalpha(0)

    draw = ImageDraw.Draw(lp_image)

    font = ImageFont.truetype(FONT_PATH, int(info_area.width * 0.2))
    w, h = draw.textsize(f'{lp} LP', font=font)

    draw.text(((info_area.width - w) / 2, (lp_image_height - h) / 2), f'{lp} LP', (255, 255, 255), font=font, stroke_width=STROKE_WIDTH, stroke_fill=(0, 0, 0))
    return lp_image


def get_summoner_spell(summoner_name):
    summoner_spells = cassiopeia.get_summoner_spells(region=Region.europe_west)
    summoner_spell = next(summoner for summoner in summoner_spells if summoner.name in summoner_name)
    return summoner_spell.image.image


def get_summoners_spell_together(summoner_one_image, summoner_two_image):
    width = summoner_one_image.width + summoner_two_image.width
    height = summoner_one_image.height
    runes_image = Image.new('RGBA', (width, height), (0, 0, 0))
    runes_image.paste(summoner_one_image, (0, 0))
    runes_image.paste(summoner_two_image, (width//2, 0))
    return runes_image

def get_runes_image(info_area, match_info):
    runes = match_info['runes']
    summonerSpells = match_info['summonerSpells']
    role = match_info['role']
    summoner_one = summonerSpells[0]
    summoner_two = summonerSpells[1]

    runes_image_height = info_area.height
    runes_image_width = info_area.width
    keystone = runes['keystone']
    secondaryRuneTree = runes['secondaryRuneTree']

    runes_width = int(info_area.width*0.2)
    maxsize = (runes_width, runes_width)
    primary_image = get_rune_image(keystone)
    primary_image = primary_image.resize(maxsize, Image.ANTIALIAS)

    runes_width = int(info_area.width*0.15)
    maxsize = (runes_width, runes_width)
    secondary_image = get_tree_image(secondaryRuneTree)
    secondary_image = secondary_image.resize(maxsize, Image.ANTIALIAS)


    runes_width = int(info_area.width*0.15)
    maxsize = (runes_width, runes_width)
    summoner_one_image = get_summoner_spell(summoner_one)
    summoner_one_image = summoner_one_image.resize(maxsize, Image.ANTIALIAS)

    runes_width = int(info_area.width*0.15)
    maxsize = (runes_width, runes_width)
    summoner_two_image = get_summoner_spell(summoner_two)
    summoner_two_image = summoner_two_image.resize(maxsize, Image.ANTIALIAS)

    runes_image = Image.new('RGBA', (runes_image_width, runes_image_height), (0, 0, 0))
    runes_image.putalpha(0)

    summoners_spell_image = get_summoners_spell_together(summoner_one_image, summoner_two_image)

    # draw = ImageDraw.Draw(runes_image)
    #
    # text = f'{role.upper()}'
    #
    # font = ImageFont.truetype(FONT_PATH, int(info_area.width * 0.1))
    # w, h = draw.textsize(text, font=font)

    # draw.text(((runes_image.width - w) / 2, ((runes_image.height - h) / 2) - 10), text, (255, 255, 255), font=font,
    #           stroke_width=STROKE_WIDTH, stroke_fill=(0, 0, 0))
    paste_with_center_coords(runes_image, summoners_spell_image, (runes_image_width / 6) * 1.8, runes_image_height / 2)
    # paste_with_center_coords(runes_image, summoner_two_image, (runes_image_width / 6) * 2, runes_image_height / 2)


    paste_with_center_coords(runes_image, primary_image, (runes_image_width / 6) * 3.8, runes_image_height / 2)
    paste_with_center_coords(runes_image, secondary_image, (runes_image_width / 6) * 4.8, runes_image_height / 2)
    return runes_image


def get_item_image(item_id):
    items = cassiopeia.get_items(region=Region.europe_west)
    item = next(item for item in items if item.id == item_id)
    return item.image.image


def get_items_image(info_area, items):
    item_width = int(info_area.width*0.15)
    items_image = []
    for item in items:
        maxsize = (item_width, item_width)
        item_image = get_item_image(item)
        if not item_image:
            continue
        item_image = item_image.resize(maxsize, Image.ANTIALIAS)
        items_image.append(item_image)

    items_image_height = item_width
    items_image_width = len(items_image) * item_width

    image = Image.new('RGBA', (items_image_width, items_image_height), (0, 0, 0))
    for index, item_image in enumerate(items_image):
        image.paste(item_image, (index * item_width, 0))
    return image


def get_player_info_area(info_area, match_info):
    player_champion = match_info['player_champion']
    role = match_info['role']
    items = match_info['items']

    info_area_width = info_area.width
    info_area_height = int(info_area.height * 0.55)

    player_info_area = Image.new('RGBA', (info_area_width, info_area_height), (0, 0, 0))
    player_info_area.putalpha(ALPHA_VALUE)

    champion_name_image = get_champion_name_image(player_info_area, player_champion, role)
    runes_image = get_runes_image(player_info_area, match_info)
    items_image = get_items_image(player_info_area, items)

    paste_with_center_coords(player_info_area, champion_name_image, player_info_area.width / 2, (player_info_area.height / 6) * 1)
    paste_with_center_coords(player_info_area, runes_image, player_info_area.width / 2, (player_info_area.height / 6) * 3)
    paste_with_center_coords(player_info_area, items_image, player_info_area.width / 2, (player_info_area.height / 6) * 5)

    draw = ImageDraw.Draw(player_info_area)
    draw.line((player_info_area.width * 0.1, (player_info_area.height / 6) * 4, player_info_area.width * 0.9, (player_info_area.height / 6) * 4), fill=(255, 255, 255), width=3)


    return player_info_area

def create_info_area(match_info, splash_art):



    info_area_width = int(0.4 * splash_art.width)
    info_area_height = int(0.9 * splash_art.height)
    info_area = Image.new('RGBA', (info_area_width, info_area_height), (0, 0, 0))
    info_area.putalpha(0)

    rank_info_area = get_rank_region_info_area(info_area, match_info)
    # rank_info_area.save('rank_info_area.png', quality=100)

    player_info_area = get_player_info_area(info_area, match_info)
    # player_info_area.save('player_info_area.png', quality=100)


    paste_with_center_coords(info_area, rank_info_area, info_area.width / 2, info_area.height * 0.2)
    paste_with_center_coords(info_area, player_info_area, info_area.width / 2, info_area.height * 0.7)

    # info_area = add_flag(info_area, region)
    info_area.save('info_area.png', quality=100)
    return info_area


def add_details_to_splashart(match_info):
    # splash_art = Image.open('splash_art_backup.jpg')
    splash_art = Image.open(SPLASH_PATH)

    info_area = create_info_area(match_info, splash_art)
    upper_margin = (splash_art.height - info_area.height) // 2

    splash_art.paste(info_area, (upper_margin, upper_margin), info_area)
    splash_art.save(SPLASH_PATH, quality=95)


# for spell in cassiopeia.get_summoner_spells(region=Region.europe_west):
#     logger.info(spell.name)
#     with open(SUMMONERS_PATH + spell.image.full, 'wb') as f:
#         spell.image.image.save(f)
# for rune in cassiopeia.get_runes(region=Region.europe_west):
#     logger.info(rune.name)
#     with open(f'{RUNES_PATH}{rune.path.name}.png', 'wb') as f:
#         rune.image.image.save(f)
def get_rune_image(rune_id):
    runes = cassiopeia.get_runes(region=Region.europe_west)
    rune = next(rune for rune in runes if rune.id == rune_id)
    return rune.image.image


def get_tree_image(tree_id):
    with open(f'{RUNES_PATH}{TREES_PATH}{tree_id}.png', 'rb') as f:
        return Image.open(BytesIO(f.read()))


