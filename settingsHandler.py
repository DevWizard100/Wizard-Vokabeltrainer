import configparser

# schreibe eine Funktion um erstmal eine settings.ini Datei zu erstellen mit dem inhalt germanToEnglish = True aber nur wenn diese Datei noch nicht existiert
import os

def createSettingsFileIfNotExists():
    if not os.path.exists('settings.ini'):
        config = configparser.ConfigParser()
        config['Settings'] = {'germanToEnglish': 'True'}
        with open('settings.ini', 'w') as configfile:
            config.write(configfile)

# schreibe eine Funktion um jetzt in der settings.ini germanToEnglish auf true oder false zu setzen
def setGermanToEnglish(value: bool):

    createSettingsFileIfNotExists()

    config = configparser.ConfigParser()
    config.read('settings.ini')
    if 'Settings' not in config:
        config['Settings'] = {}
    config['Settings']['germanToEnglish'] = str(value)
    with open('settings.ini', 'w') as configfile:
        config.write(configfile)

def getGermanToEnglish() -> bool:
    config = configparser.ConfigParser()
    config.read('settings.ini')
    try:
        return config.getboolean('Settings', 'germanToEnglish')
    except (configparser.NoSectionError, configparser.NoOptionError):
        return True  # Standardwert, wenn nicht gesetzt