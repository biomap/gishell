from arcgis import GIS
from configparser import ConfigParser


# Load the configuration file
cfg = ConfigParser()
cfg.read("agol_command/test-config.conf")

def basic(url=cfg['agol']['url'],
          username=cfg['agol']['username'],
          password=cfg['agol']['password']):
    connection = GIS(url=url, username=username, password=password)
    return connection
