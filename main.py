import logging
import sys
from logging.handlers import RotatingFileHandler

from data.espn import EspnFantasy
from data.yahoo import YahooFantasy
from version import __version__


def main():
    if '--espn' in sys.argv:
        fantasy = EspnFantasy()
        fantasy.print()
    elif '--yahoo' in sys.argv:
        fantasy = YahooFantasy()
        fantasy.print()
    else:
        SystemExit('Platform not supported')


if __name__ == '__main__':
    if '--debug' in sys.argv:
        LOG_LEVEL = logging.DEBUG
        sys.argv.remove('--debug')
    else:
        LOG_LEVEL = logging.WARNING

    logger = logging.getLogger('')
    logger.setLevel(LOG_LEVEL)
    handler = RotatingFileHandler(filename='nfl-fantasy.log',
                                  maxBytes=5 * 1024 * 1024,  # 5MB
                                  backupCount=4)
    handler.setFormatter(logging.Formatter(fmt='%(asctime)s %(levelname)s: %(message)s',
                                           datefmt='%m/%d/%Y %I:%M:%S %p'))
    logger.addHandler(handler)

    try:
        main()
    except Exception as e:
        logging.exception(SystemExit(e))
