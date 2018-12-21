import scrapy
import os
import sys
from scrapy.selector import Selector

class DealerSpider(scrapy.Spider):
    name = 'dealers'
    start_urls = [
        'https://www.supralift.com/uk/Forklift-truck-dealers/A.-S.-Kriegel-GmbH-FrankfurtOder/554160ec5a06dcaa9c9b6125.html?_cid=fed2bca3-e415-49d2-8e9e-e64d45574360&&dealer.sortCrit=n&dealer.sortMod=asc&dealer.pageSize=10&dealer.pageNumber=0'
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

        pagination = response.css(
            'div:nth-child(2) > div > header > div > a.triangle.right.disabled::attr(href)').extract_first()
        if pagination is not None:
            next_page_link = response.urljoin(pagination)
            yield scrapy.Request(next_page_link, callback=self.parse)

        company_info = response.css('div.merchant > div:nth-child(1) > div.row > div.col-md-9 > div > h3::text, '
                                    'div.merchant > div:nth-child(1) > div.row > div.col-md-9 > div > p::text').re(
            r'[A-Za-z0-9].+')

        website = response.css(
            'div.content_element.elem_row.clearfix > div.elem_col.width_75.full_width_mobile > a::attr(href)').extract()
        brands = response.xpath('//div[3]/div/div[2]/div[2]/text()').re(r'[A-Za-z0-9].+')
        contact_info = response.css(
            'div.merchant > div.content_element.contact_person.margin_bottom_none.padding_bottom_medium > div:nth-child(2) > h3::text,'
            'div.merchant > div.content_element.contact_person.margin_bottom_none.padding_bottom_medium > div > h3::text,'
            'div.merchant > div.content_element.contact_person.margin_bottom_none.padding_bottom_medium > div:nth-child(2) > div > p::text,'
            'div.merchant > div.content_element.contact_person.margin_bottom_none.padding_bottom_medium > div > div > p::text').extract()

        yield {
            'company name': company_info[0],
            'address': company_info[1],
            'city': company_info[2].split(' ')[1],
            'postal': company_info[2].split(' ')[0],
            'country': company_info[3],
            'website': website,
            'brands': brands,
            'contact': contact_info,
            'url': response.url,

        }
