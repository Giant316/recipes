import scrapy
import itertools
import re 

class AkisRecipesSpider(scrapy.Spider):
	name = 'akis_recipes'
	allowed_domains = ['akispetretzikis.com']
	start_urls = ['https://akispetretzikis.com/en/']
	cookies = {
		"CookieConsent": "{stamp:%27gfFpaCDUYuyy8PQZK4Zo7ounw9OHRKA4QE2BDHAXVA47voDT8srZ+g==%27%2Cnecessary:true%2Cpreferences:false%2Cstatistics:false%2Cmarketing:false%2Cver:1%2Cutc:1606806646606%2Ciab2:%27CO9uzyhO9uzyhCGABBENBBCgAAAAAH_AAAAAAAAOJAJMNS-AizEscCSaNKoUQIQriQ6AEAFFCMLRNYQErgp2VwEfoIGACA1ARgRAgxBRiyCAAAAAJKIgJADwQCIAiAQAAgBUgIQAEaAILACQMAgAFANCwAigCECQgyOCo5TAgIkWignkrAEou9jDCEMooAaBAAAA.YAAAAAAAAAAA%27%2Cgacm:%271~%27%2Cregion:%27de%27}",
		"cp_total_cart_items": "0",
		"cp_total_cart_value": "0",
		"cpab": "90156eca-d6d6-4cf6-e90c-608f0ec9903f",
		"cp_shownnotscookie": "yes",
		"atuserid": "%7B%22name%22%3A%22atuserid%22%2C%22val%22%3A%2256f02c84-bcdd-464d-bc8b-6456baf5c661%22%2C%22options%22%3A%7B%22end%22%3A%222022-01-02T07%3A53%3A40.616Z%22%2C%22path%22%3A%22%2F%22%7D%7D",
		"atidvisitor": "%7B%22name%22%3A%22atidvisitor%22%2C%22val%22%3A%7B%22vrn%22%3A%22-612162-%22%7D%2C%22options%22%3A%7B%22path%22%3A%22%2F%22%2C%22session%22%3A15724800%2C%22end%22%3A15724800%7D%7D",
		"_eproductions.gr_session": "BAh7B0kiD3Nlc3Npb25faWQGOgZFVEkiJTc1YjgxOTA1NGZlZjAyOGIyMTFhMzI1ZjRhMzkyMDQ1BjsAVEkiEF9jc3JmX3Rva2VuBjsARkkiMVMyNTRYUHR5L3hWcEFKTzAzdUtWRWtHYjFBM3lXalJhLzd3bGRpc3RmaTg9BjsARg%3D%3D--f6fbf28a4d91ba49981a767bb30c42687e4d0512",
		"cp_sessionTime": "1606895261167"
	}
	headers = {
		"Connection": "keep-alive",
		"Accept": "*/*;q=0.5, text/javascript, application/javascript, application/ecmascript, application/x-ecmascript",
		"X-CSRF-Token": "nTQc+lc0ubArViX2mzdmrveYrWstyMu9uwq1IorqrH/WWmSmrEZGpUJWtkJF1fO8tgN5Zt+S/+dEtpBUocfSUA==",
		"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.67 Safari/537.36",
		"X-Requested-With": "XMLHttpRequest",
		"Sec-Fetch-Site": "same-origin",
		"Sec-Fetch-Mode": "cors",
		"Sec-Fetch-Dest": "empty",
		"Referer": "https://akispetretzikis.com/en/categories/glyka",
		"Accept-Language": "en-GB,en-US;q=0.9,en;q=0.8"
	}
	dyn_urls = []
	base_urls = []

	def parse(self, response):
		'''
			This is the entry point of the spider and it must be named as parse
		'''

		# extract href from the dropdown menu: https://akispetretzikis.com/en/categories/glyka 
		lis = response.css('.new-submenu > div > div > ul > li > a::attr(href)').extract()
		base_urls = ['https://akispetretzikis.com' + x for x in lis]
		self.base_urls = base_urls
		n = len(base_urls)
		
		# to generate the incremental page counter in the url: https://akispetretzikis.com/en/categories/glyka?page=40
		seq = list(itertools.chain.from_iterable(itertools.repeat(x, n) for x in range(1,40)))
		urls = [ y + "?=page" + str(x) for x, y in zip(seq, itertools.cycle(base_urls))]
		for url in urls: 
			# update the Referer in the headers
			# insert the header and cookies information here
			self.headers["Referer"] = url
			yield scrapy.Request(
				url=url,
				method='GET',
				dont_filter=True,
				cookies=self.cookies,
				headers=self.headers,
				callback = self.parse_pages
			)

	def parse_pages(self, response):
		# the returned response from the stimulated request is a bytes object which is then converted to a string object
		# extract the href tag using regex and save it to the global var
		search = re.findall(r'(?<=<a href=\\")[^"]*', response.body.decode(encoding='UTF-8'))
		urls = [ 'https://akispetretzikis.com' + x.replace("\\", "") for x in search]
		self.dyn_urls.append(list(dict.fromkeys(urls)))
		# use the base_urls stored earlier to scrape the url of the recipes shown (without clicking "show more")
		# e.g. orginal recipes shown in https://akispetretzikis.com/en/categories/glyka
		for url in self.base_urls:
			yield scrapy.Request(url = url, callback = self.parse_recipes)

	def parse_recipes(self, response):
		# retrieve all respective href of each recipes + the url retrieved from the dynamic request 
		lis = response.css('#recipes_cont > div > div > .recipe-card > div > h4 > a::attr(href)').extract()
		flatten = [val for sublist in self.dyn_urls for val in sublist]
		urls = ['https://akispetretzikis.com' + x for x in lis] + flatten
		for url in urls: 
			yield response.follow(url = url, callback = self.parse_contents)

	def parse_contents(self, response):
		# scrape the method, ingredients, name and category information of the recipes
		# save it as a dict and output them
		method = response.css('.method > div > div > .text > ul > li ::text').extract()
		name = response.css('.row > .col-md-12 > h1::text').extract()
		ingredients = response.css('.recipe-main > div > div > ul > li ::text').extract()
		category = response.css('.recipe-breadcrumb > a::text').extract()
		recipes = {
			'name': name,
			'method': method,
			'ingredients': ingredients,
			'category': category
		}
		yield recipes
