
from cassiopeia import get_champion


def save_champion_splashart(champion, skin_id):
    print(f'[{__name__.upper()}] - Retrieving splash art')
    champion = get_champion(champion)
    skins = champion.skins
    skin = next(item for item in skins if item.number == skin_id)
    with open(f'splash_art.jpeg', 'wb') as f:
        skin.splash.save(f)
