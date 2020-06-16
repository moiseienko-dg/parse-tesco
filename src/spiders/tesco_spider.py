import scrapy
import json

from items import TescoItems


class TescoSpider(scrapy.Spider):
    name = "tesco"

    def start_requests(self):
        urls = [
            'https://www.tesco.com/groceries/en-GB/shop/household/kitchen-roll-and-tissues/all',
            'https://www.tesco.com/groceries/en-GB/shop/pets/cat-food-and-accessories/all'
        ]
        for url in urls:
            yield scrapy.Request(url=url, callback=self.parse_pagination)

    def parse_pagination(self, response):
        urls_raw = response.xpath("//script[@type='application/ld+json']").get()
        urls_clean = json.loads(urls_raw[35:-9])
        for i in urls_clean[2]['itemListElement']:
            yield scrapy.Request(url=i['url'], callback=self.parse_review)

        next_page = response.xpath("//link[@rel='next']/@href").get()
        if next_page is not None:
            yield scrapy.Request(next_page, callback=self.parse_pagination)

    def parse_info(self, response, reviews, response_origin):
        item = TescoItems()
        info_raw = response.xpath("//script[@type='application/ld+json']").get()
        info_clean = json.loads(info_raw[35:-9])
        item['product_id'] = int(info_clean[2]['sku'])
        item['product_url'] = response_origin
        item['image'] = info_clean[2]['image']
        item['title'] = info_clean[2]['name']
        item['category'] = info_clean[2]['@type']
        item['price'] = float(info_clean[2]['offers']['price'])
        description = response.xpath("//div[@id='product-marketing']//li/text()").getall()
        description_1 = response.xpath("//div[@id='brand-marketing']//li/text()").getall()
        description_2 = response.xpath("//div[@id='other-information']//li/text()").getall()
        description_3 = response.xpath("//div[@id='pack-size']//li/text()").getall()
        description += description_1 + description_2 + description_3
        item['description'] = "".join(description)
        name_and_address = response.xpath("//div[@id='manufacturer-address']//li/text()").getall()
        item['name_and_address'] = "".join(name_and_address)
        return_address = response.xpath("//div[@id='return-address']//li/text()").getall()
        item['return_address'] = "".join(return_address)
        net_contents = response.xpath("//div[@id='net-contents']//p/text()").getall()
        item['net_contents'] = "".join(net_contents)
        item['reviews'] = reviews
        bought_next_products = {}
        count_bought_next = len(
            response.xpath("//div[@class='recommender__wrapper']/div[@class='product-tile-wrapper']")
            )
        for i in range(1, count_bought_next + 1):
            title = response.xpath(
                f"//div[@class='recommender__wrapper']//div[@class='product-tile-wrapper'][{i}]//h3/a/text()"
                ).get()
            url = response.xpath(
                f"//div[@class='recommender__wrapper']//div[@class='product-tile-wrapper'][{i}]//h3/a/@href"
                ).get()
            bought_next_products[i] = {
            'title': title,
            'url': 'https://www.tesco.com' + url
            }
        item['bought_next_prodicts'] = bought_next_products
        return item

    def parse_review(self, response):
        reviews = response.meta.get('reviews', {})
        count_total = response.meta.get('count_total', 0)
        response_origin = response.meta.get('response_origin', None)
        if response_origin is None:
            response_origin = response.url
        count_reviews = len(
            response.xpath(
                "//div[@id='review-data']//article[@class='content']//section[@class='sc-dNLxif dUMnMc']"
                )
            )
        for i in range(1, count_reviews + 1):
            title = f"//div[@id='review-data']//article[@class='content']//section[{i}]/h4/text()"
            author = f"//div[@id='review-data']//article[@class='content']//section[{i}]/p[1]/span[1]/text()"
            date = f"//div[@id='review-data']//article[@class='content']//section[{i}]/p[1]/span[2]/text()"
            text = f"//div[@id='review-data']//article[@class='content']//section[{i}]/p[2]/text()"
            stars = f"//div[@id='review-data']//article[@class='content']//section[{i}]//div[1]//span[1]/text()"
            if response.xpath(author).get() is None:
                author = f"//div[@id='review-data']//article[@class='content']//section[{i}]/p[1]/text()"
            if response.xpath(date).get() is None:
                date = f"//div[@id='review-data']//article[@class='content']//section[{i}]/p[2]/span/text()"
            if response.xpath(text).get() is None:
                text = f"//div[@id='review-data']//article[@class='content']//section[{i}]/p[3]/text()"
            if response.xpath(stars).get() is not None:
                stars = int("".join(filter(str.isdigit, response.xpath(stars).get())))
            else:
                stars = ''
            reviews[i+count_total] = {
            'title': response.xpath(title).get(),
            'author': response.xpath(author).get(),
            'date': response.xpath(date).get(),
            'text': response.xpath(text).get(),
            'stars': stars,
            }
        next_page = response.xpath(
            "//a[@class='sc-ktHwxA iYjymA styled__TextButtonLink-ipdqot-0 GMOgz']/@href"
            ).get()
        if next_page is not None:
            count_total += count_reviews
            next_page = 'https://www.tesco.com' + next_page
            yield response.follow(
                next_page,
                callback=self.parse_review,
                meta={
                'reviews': reviews,
                'count_total': count_total,
                'response_origin': response_origin
                }
                )
        else:
            yield self.parse_info(response, reviews, response_origin)
        