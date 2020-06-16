import os
import logging
from dotenv import load_dotenv, find_dotenv


BOT_NAME = 'src'

SPIDER_MODULES = ['spiders']
NEWSPIDER_MODULE = 'spiders'

USER_AGENT = 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/81.0.4044.122 Safari/537.36'

ROBOTSTXT_OBEY = False

load_dotenv(find_dotenv())
LOG_LEVEL = os.environ.get('LOG_LEVEL', 'ERROR')
LOG_FILE = os.environ.get('LOG_FILE', 'log.txt')

ITEM_PIPELINES = {
    'pipelines.tesco_pipeline.TescoPipeline': 300,
}