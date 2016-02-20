import sqlalchemy as sql

from stock import query
from stock import models

from logging import getLogger
logger = getLogger(__name__)


def update_copmany_list():
    # check company_id is valid
    session = query.session()
    c = query.Company.all(last_date=last_date, session=session)
    if not c:
        logger.info("SKIP: company(id=%s)" % company_id)
        return
    session.close()
