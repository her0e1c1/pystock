import stock


class CrawlerPipeline(object):

    def process_item(self, item, spider):
        stock.query.bulk_insert(stock.model.DailyPrice, [item])
        return item
