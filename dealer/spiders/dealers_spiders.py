import scrapy
import os
import sys
from scrapy.selector import Selector

class DealerSpider(scrapy.Spider):
    name = 'dealers'
    base_url = 'https://www.supralift.com'
    start_urls = [
        'https://www.supralift.com/uk/dealer-overview?_cid=640bdaf9-4c0f-42eb-93aa-38b8ed2f1d3c'
    ]
    TMP_FILE = os.path.join(os.path.dirname(sys.modules['dealer'].__file__), 'tmp/dealer.csv')
    custom_settings = {
        'FEED_FORMAT': 'csv',
        'FEED_URI': TMP_FILE,
        'DOWNLOAD_DELAY': 8,
        'CONCURRENT_REQUESTS': 1,
        'CONCURRENT_REQUESTS_PER_DOMAIN': 1,
    }

    def parse(self, response):
        rows = response.css('div > div > div.col-md-5.border_right.maxhelem.clickable > a::attr(href)').extract()
        for link in rows:
            dealer_profile = response.urljoin(link)
            yield scrapy.Request(dealer_profile, callback=self.dealerparse)

        pagination = response.css(
            'div.content_element.elem_row > form > div:nth-child(4) > div > a::attr(href)').extract_first()
        next_page_link = response.urljoin(pagination)
        yield scrapy.Request(next_page_link, callback=self.parse)


    def dealerparse(self, response):
        company_info = response.css('div.merchant > div:nth-child(1) > div.row > div.col-md-9 > div > h3::text, '
                                    'div.merchant > div:nth-child(1) > div.row > div.col-md-9 > div > p::text').re(r'[A-Za-z0-9].+')

        website = response.css(
            'div.content_element.elem_row.clearfix > div.elem_col.width_75.full_width_mobile > a::attr(href)').extract()
        brands = response.xpath('//div[3]/div/div[2]/div[2]/text()').re(r'[A-Za-z0-9].+')
        contact_info = response.css(
            'div.merchant > div.content_element.contact_person.margin_bottom_none.padding_bottom_medium > div:nth-child(2) > h3::text,'
            'div.merchant > div.content_element.contact_person.margin_bottom_none.padding_bottom_medium > div > h3::text,'
            'div.merchant > div.content_element.contact_person.margin_bottom_none.padding_bottom_medium > div:nth-child(2) > div > p::text,'
            'div.merchant > div.content_element.contact_person.margin_bottom_none.padding_bottom_medium > div > div > p::text').extract()

        yield {
            'url': response.url,
            'company name': company_info[0],
            'address': company_info[1],
            'city': company_info[2].split(' ')[1],
            'postal': company_info[2].split(' ')[0],
            'country': company_info[3],
            'website': website,
            'brands': brands,
            'contact': contact_info

        }
