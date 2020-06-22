import scrapy
import json
import re

from items import TescoItems


class TescoSpider(scrapy.Spider):
    name = "tesco"

    def start_requests(self):
        urls = [
            'https://www.tesco.com/groceries/en-GB/shop/household/kitchen-roll-and-tissues/all'
            'https://www.tesco.com/groceries/en-GB/shop/pets/cat-food-and-accessories/all'
        ]
        for url in urls:
            yield scrapy.Request(url=url, callback=self.parse_pagination)

    def parse_pagination(self, response):
        urls_raw = response.xpath("//script[@type='application/ld+json']").get()
        urls_clean = re.findall(r'https://www.tesco.com/groceries/en-GB/products/\d+', urls_raw)
        for url in urls_clean:
            yield scrapy.Request(url=url, callback=self.parse_info)

        next_page = response.xpath("//link[@rel='next']/@href").get()
        if next_page is not None:
            yield scrapy.Request(next_page, callback=self.parse_pagination)

    def parse_info(self, response):
        item = TescoItems()
        info_raw = response.xpath("//script[@type='application/ld+json']/text()").get()
        info_clean = json.loads("".join(info_raw))
        for i in info_clean:
            if i.get('sku', None) is not None:
                item['product_id'] = int(i['sku'])
                item['product_url'] = response.url
                item['image'] = i['image']
                item['title'] = i['name']
                item['category'] = i['@type']
                item['price'] = float(i['offers']['price'])
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
        return self.parse_review(response, item)

    def parse_review(self, response, item=None):
        count_total = response.meta.get('count_total', 0)
        if item is not None:
            item = item
            item['reviews'] = {}
        else:
            item = response.meta.get('item')
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
            item['reviews'][i+count_total] = {
            'title': response.xpath(title).get(),
            'author': response.xpath(author).get(),
            'date': response.xpath(date).get(),
            'text': response.xpath(text).get(),
            'stars': stars,
            }
        next_page = response.xpath("//a[contains(@href,'active-tab=product-reviews')]/@href").get()
        if next_page is not None:
            count_total += count_reviews
            next_page = 'https://www.tesco.com' + next_page
            yield response.follow(
                next_page,
                callback=self.parse_review,
                meta={
                'item': item,
                'count_total': count_total,
                }
                )
        else:
            yield item
