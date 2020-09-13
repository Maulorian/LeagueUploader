import configparser

GAME_CFG_PATH = 'C:\\Riot Games\\League of Legends\\Config\\game.cfg'


def enable_settings():
    config = configparser.ConfigParser()
    config.read(GAME_CFG_PATH)
    config['Performance']['ShadowQuality'] = "4"
    config['General']['windowmode'] = "2"
    # config['General']['EnableReplayApi'] = "1"
    with open(GAME_CFG_PATH, 'w') as configfile:
        config.write(configfile)


def disable_settings():
    config = configparser.ConfigParser()
    config.read(GAME_CFG_PATH)
    config['Performance']['ShadowQuality'] = "0"
    config['General']['windowmode'] = "0"

    with open(GAME_CFG_PATH, 'w') as configfile:
        config.write(configfile)
