import requests
import io
from bs4 import BeautifulSoup
from cassiopeia import GameMode, Queue
from unidecode import unidecode

from urllib.parse import unquote
import cassiopeia as cass
import spectator

LADDER_URL = 'https://euw.op.gg/ranking/ladder/'


def get_top100_challengers():
    r = requests.get(LADDER_URL)
    html = r.text
    with io.open('opgg_response.html', "w", encoding="utf-8") as f:
        f.write(html)

    soup = BeautifulSoup(html, "html.parser")
    challengers = soup.findAll("a")
    challengers = list(map(lambda link: link['href'], challengers))
    challengers = list(filter(lambda href: '//euw.op.gg/summoner/userName=' in href, challengers))
    challengers = list(map(lambda href: href.split('=')[1], challengers))
    challengers = list(map(lambda challenger: challenger.replace('+', ' '), challengers))
    challengers = list(map(lambda challenger: unidecode(unquote(challenger)), challengers))
    return challengers


def get_top_challenger():
    challengers = get_top100_challengers()
    for summoner_name in challengers:
        summoner = cass.get_summoner(name=summoner_name)
        match = spectator.get_current_match(summoner)
        if match is None:
            continue
        print(match.queue)
        if match.queue != Queue.ranked_solo_fives:
            continue

        return summoner_name
