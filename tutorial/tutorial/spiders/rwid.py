import scrapy


class RwidSpider(scrapy.Spider):
    name = 'rwid'
    allowed_domains = ['192.168.100.11']
    start_urls = ['http://192.168.100.11:9999/']

    def parse(self, response):
        self.logger.info(response.headers.getlist("Set-Cookie"))
        url = 'http://192.168.100.11:9999/login'
        yield scrapy.FormRequest(url, formdata={'username': '1', 'password': '1'},
                                 meta={'dont_redirect': True, 'handle_httpstatus_list': [302]},
                                 callback=self.afterlogin)
        self.logger.info(response.headers.getlist("Set-Cookie"))

    def afterlogin(self, response):
        yield scrapy.Request('http://192.168.100.11:9999', callback=self.redirect)

    def redirect(self, response):
        title_page_links = response.css('.card-title a')
        yield from response.follow_all(title_page_links, self.parse_detail)

        pagination_links = response.css('.pagination a.page-link')
        yield from response.follow_all(pagination_links, self.redirect)

    def parse_detail(self, response):
        def extract_with_css(query):
            return response.css(query).get(default='').strip()

        image = '.card-img-top::attr(src)'
        title = '.card-title::text'
        stock = '.card-stock::text'
        description = '.card-text::text'

        return {
            'image': extract_with_css(image),
            'title': extract_with_css(title),
            'stock': extract_with_css(stock),
            'desc': extract_with_css(description),
        }

