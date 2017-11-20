# -*- coding: utf-8 -*-
import scrapy
import re

from locations.items import GeojsonPointItem


class MontessoriSchoolSpider(scrapy.Spider):
    name = "montessori_school"
    allowed_domains = ["www.montessori.com"]
    start_urls = (
        'https://www.montessori.com/montessori-schools/find-a-school/',
    )

    def parse(self, response):
        for state_path in response.xpath('//map[@id="USMap"]/area/@href'):
            yield scrapy.Request(
                response.urljoin(state_path.extract()),
                callback=self.parse_state,
            )

    def parse_state(self, response):
        for school_elem in response.xpath('//div[@class="locationCard"]'):

            addr_elem = school_elem.xpath('.//a[@class="addrLink addrLinkToMap"]/span[@class="addr"]')
            city_state_str = addr_elem.xpath('.//span[@class="cityState"]/text()').extract_first()
            (city, state, postcode) = re.search(r'^(.*), ([A-Z]{2}) (\d{5})$', city_state_str).groups()

            properties = {
                'ref': school_elem.xpath('@data-school-id')[0].extract(),
                'name': school_elem.xpath('.//a[@class="schoolNameLink"]/text()').extract_first(),
                'addr:full': addr_elem.xpath('.//span[@class="street"]/text()').extract_first().strip(),
                'addr:city': city,
                'addr:state': state,
                'addr:postcode': postcode,
            }

            lon_lat = [
                float(addr_elem.xpath('.//@data-longitude').extract_first()),
                float(addr_elem.xpath('.//@data-latitude').extract_first()),
            ]

            yield GeojsonPointItem(
                properties=properties,
                lon_lat=lon_lat,
            )