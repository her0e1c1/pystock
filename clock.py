# coding: utf-8
# TODO: use celery
from apscheduler.schedulers.blocking import BlockingScheduler

# from stock import service

import logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
sched = BlockingScheduler()


# WARN: minus 9 if you want to use JST
# @sched.scheduled_job('interval', minutes=1)
@sched.scheduled_job('cron', day_of_week='mon-fri', hour=7, minute=0)
@sched.scheduled_job('cron', day_of_week='mon-fri', hour=15, minute=10)  # 0:10 (JST)
@sched.scheduled_job('cron', day_of_week='mon-fri', hour=19, minute=0)
def scheduled_scrape_japan():
    # ldate = service.util.last_date()
    logger.info('CRON: Scrape and store stock at ...')
    # logger.info('CRON: Scrape and store stock at %s' % ldate)
    # service.company.update_copmany_list(each=True, ignore=True, last_date=ldate)
    # service.search_field.update_search_fields()


logger.info('CRON: Start ...')
sched.start()
