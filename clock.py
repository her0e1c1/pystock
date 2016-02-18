from logging import getLogger

from apscheduler.schedulers.blocking import BlockingScheduler

from stock import query
from stock import util

logger = getLogger(__name__)
sched = BlockingScheduler()


# @sched.scheduled_job('interval', minutes=1)
@sched.scheduled_job('cron', day_of_week='mon-fri', hour=4, minute=40)
def scheduled_scrape_japan():
    logger.info('CRON: Scrape and store stock')
    query.DayInfo.sets(each=True, ignore=True, last_date=util.last_date())


sched.start()
