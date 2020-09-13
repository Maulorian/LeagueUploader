
from cassiopeia import get_champion


def save_champion_splashart(champion, skinName):

    print(f'[{__name__.upper()}] - Retrieving splash art for {champion} skin {skinName}')

    champion = get_champion(champion)
    skins = champion.skins
    skin = next(item for item in skins if item.name == skinName)
    with open(f'splash_art.jpeg', 'wb') as f:
        skin.splash.save(f)
