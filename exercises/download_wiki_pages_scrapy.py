import os
import scrapy


class TestSpider(scrapy.Spider):
    name = "test"

    start_urls = [
        "https://en.wikipedia.org/wiki/Alexei_Abrikosov_(physicist)",
    ]

    def parse(self, response):
        filename = response.url.split("/")[-1] + '.html'
        filepath = os.path.expanduser(f'~/data/wikipedia/theoretical_physicists_pages/{filename}')
        with open(filepath, 'wb') as f:
            f.write(response.body)
