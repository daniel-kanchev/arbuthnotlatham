import scrapy
from scrapy.loader import ItemLoader
from itemloaders.processors import TakeFirst
from datetime import datetime
from arbuthnotlatham.items import Article


class ArbutSpider(scrapy.Spider):
    name = 'arbut'
    start_urls = ['https://www.arbuthnotlatham.co.uk/insights']

    def parse(self, response):
        links = response.xpath('//h3/parent::a/@href').getall()
        yield from response.follow_all(links, self.parse_article)

    def parse_article(self, response):
        item = ItemLoader(Article())
        item.default_output_processor = TakeFirst()

        title = response.xpath('//h1//text()').get()
        if title:
            title = title.strip()

        date = response.xpath('//p[@class="article-header__metacontent"]/text()').get()
        if date:
            date = date.split()
            date[0] = date[0][:-2]
            date = " ".join(date)
            date = datetime.strptime(date.strip(), '%d %B %Y')
            date = date.strftime('%Y/%m/%d')

        content = response.xpath('//div[@class="field field--name-field-sections field--type-entity-reference-revisions'
                                 ' field--label-hidden field__items"]//text()').getall()

        content = [text for text in content if text.strip()]
        content = "\n".join(content).strip()

        item.add_value('title', title)
        item.add_value('date', date)
        item.add_value('link', response.url)
        item.add_value('content', content)

        return item.load_item()
