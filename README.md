# Create a Web Crawler using Scrapy 

This project is to crawl recipes from [Akis’s Website](https://akispetretzikis.com/) by using scrapy. Scrapy is a powerful libray in Python that allows us to create a customized and easy-to-scale spider. I would like to scrape more recipes from other website but for now the “spider” created only crawl within one domain. Within this one domain, it navigates through several pages to extract recipes according to the category. Information such as `name` , `method` and `ingredients` of the recipe are then extracted and output as `CSV` file.

## To start a scrapy project

+ After installing the scrapy library, go to the directory where we want to locate the project in the command prompt, run `scrapy start project recipes`  and navigate to the created project directory to start the project `scrapy genspider akis_recipes akispetretzikis.com/en` 
+ a python file `akis_recipes` will be generated within the project folder `spiders` and here is where I customize my own spider! 
+ The overview of how to create a web crawler can be grasped through [this blogpot](https://www.datacamp.com/community/tutorials/making-web-crawlers-scrapy-python) or [this Datacamp course](https://learn.datacamp.com/courses/web-scraping-with-python)

## Dealing with “Show more” button

On this particular website, more recipes will be only loaded when the “Show more” button is clicked. Since I would like to scrape as many recipes as possible from the website, the key challenge that I have to face in this project is to deal with the dynamic request sent by the browser. In this particular case, the response returned is not a JSON object but rather a `JQuery`-like text: 

> $('#recipes_cont').append("<div class=\'row\'>\n<div class=\'col-md-4 col-sm-4 col-xs-12\' id=\'chalvas-me-mantarini-kai-sokolata\'>\n<div class=\'v_box recipe-card\'>\n<a href=\"/en/categories/glyka/chalvas-me-mantarini-kai-sokolata\"><img class=\"img-responsive ipad_img recipe-box-img\" src=\"https://d3fch0cwivr6nf.cloudfront.net/system/uploads/medium/data/11521/recipe_thumb_halvas-mantarini-sokolata-site.jpg\" alt=\"Recipe thumb halvas mantarini sokolata site\" />\n<\/a><div class=\'texts\'>\n<h4>\n<a href=\"/en/categories/glyka/chalvas-me-mantarini-kai-sokolata\">Chocolate and tangerine halvah\n<\/a><\/h4>\n<\/div>\n
> ....

So I couldn’t manage to handle the request URL `https://akispetretzikis.com/en/categories/glyka?page=2` easily by parsing the JSON object to extract the data needed as suggested by the [documentation](https://docs.scrapy.org/en/latest/topics/developer-tools.html?highlight=curl%20docu) in scrapy. 

### To stimulate requests sent by clicking “Show more” button

The workaround I used is to add `headers` and `cookies` information to the `scrapy.Request` in order to stimulate a similar request sent when the user clicks the “show more” button. In order to retrieve the necessary headers and cookies information, I am using the following trick: 

1. Nagivate through the developer tool for “View Source Page” of the browser to look for `XHR` in `Network` 
2. Click on the “Show more” button to see the request generated, in this case `glyka?page=2` xhr file is generated but not JSON object so I export the request in `cURL` format 
   ![cURL code](../blob/master/cURL code.png?raw=true)
3. Then I translate the `cURL` command into a Scrpay request by using [curl2scrapy](https://michael-shub.github.io/curl2scrapy/) and incorporate the cookies and headers information in my code

## Output the extracted info to CSV

To output the data as csv, I need to add these two lines in the `settings.py`

+ `FEED_FORMAT = ‘csv’ `
+ `FEED_URI = ‘akis_recipes.csv’`



### References

+ https://docs.scrapy.org/en/latest/topics/developer-tools.html?highlight=curl%20docu

