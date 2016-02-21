# coding: utf-8
import logging
from logging import getLogger

from apscheduler.schedulers.blocking import BlockingScheduler

from stock import query
from stock import service


logging.basicConfig(level=logging.INFO)
logger = getLogger(__name__)
sched = BlockingScheduler()

# WARN: minus 9 if you want to use JST


# @sched.scheduled_job('interval', minutes=1)
@sched.scheduled_job('cron', day_of_week='mon-fri', hour=7, minute=0)
@sched.scheduled_job('cron', day_of_week='mon-fri', hour=15, minute=0)
@sched.scheduled_job('cron', day_of_week='mon-fri', hour=19, minute=0)
def scheduled_scrape_japan():
    logger.info('CRON: Scrape and store stock')
    query.DayInfo.sets(each=True, ignore=True, last_date=service.last_date())
    service.update_search_fields()


logger.info('CRON: Start ...')
sched.start()
