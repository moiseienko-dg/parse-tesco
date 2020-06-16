import scrapy


class TescoItems(scrapy.Item):
    description = scrapy.Field()
    name_and_address = scrapy.Field()
    return_address = scrapy.Field()
    net_contents = scrapy.Field()
    product_id = scrapy.Field()
    product_url = scrapy.Field()
    image = scrapy.Field()
    title = scrapy.Field()
    category = scrapy.Field()
    price = scrapy.Field()
    reviews = scrapy.Field()
    bought_next_prodicts = scrapy.Field()