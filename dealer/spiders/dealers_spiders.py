import scrapy
import os
import sys

from scrapy.crawler import CrawlerProcess


class DealerSpider(scrapy.Spider):
    """
    dealer class that will get all the
    details from dealer profile on the
    supralift profile last updated 12/20/18
    """
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


class GrayedDealersSpider(scrapy.Spider):
    """
    class that will pull the profiles of the dealer accounts
    that have been grayed out on the supralift website
    last updated 1/8/19
    """
    name = 'grayed'
    start_urls = [
        'https://www.supralift.com/uk/forklift-truck-dealers/country-list'
    ]
    TMP_FILE = os.path.join(os.path.dirname(sys.modules['dealer'].__file__), 'tmp/grayeddealer.csv')
    custom_settings = {
        'FEED_FORMAT': 'csv',
        'FEED_URI': TMP_FILE,
        'DOWNLOAD_DELAY': 8,
        'CONCURRENT_REQUESTS': 1,
        'CONCURRENT_REQUESTS_PER_DOMAIN': 1,
    }

    def parse(self, response):
        countries_link = response.xpath('//*[@id="main_wrapper"]/main/div/div/div/div/div/div/div/div/div[2]/div/p/a/@href').extract()
        # loop through elements in the list to pass country and link to dealer profile function
        for link in countries_link:
            page_url = response.urljoin(link)
            yield scrapy.Request(page_url, callback=self.dealerprofile)

    def dealerprofile(self, response):
        company_list = response.xpath(
            '//*[@id="main_wrapper"]/main/div/div/div/div[4]/div/div/div[2]/div[2]/div/div/div/div/div/div/h3'
            '[@class="font_grey"]/text()').extract()
        address_list = response.xpath(
            '//*[@id="main_wrapper"]/main/div/div/div/div[4]/div/div/div[2]/div[2]/div/div/div/div/div/div[1]'
            '/text()').re(r'[0-9A-z].+')
        # get the url
        country_url = str(response.url)
        # split the url into a list to extract the country from the url
        country_list = country_url.split('/')
        # loop through each element in the list
        for company, address in zip(company_list, address_list):
            yield {
                'company': company,
                'address': address.replace(u'\xa0', ' '),
                'country': country_list[-1].replace('.html', '')

            }


# process = CrawlerProcess()
# process.crawl(DealerSpider)
# process.crawl(GrayedDealersSpider)
# process.start()
