import logging
import datetime


def config():
    logging.basicConfig(filename=f"./logs/{datetime.date.today()}_logfile.log", encoding='utf-8', level=logging.INFO,
                        format='%(asctime)s %(message)s', datefmt='%I:%M:%S %p')


def info(msg):
    logging.info(msg)


def error(msg):
    logging.error(msg)


def warning(msg):
    logging.warning(msg)
