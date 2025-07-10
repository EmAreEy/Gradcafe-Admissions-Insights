# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class GradcafeItem(scrapy.Item):
    university = scrapy.Field()
    program = scrapy.Field()
    degree = scrapy.Field()
    date_posted = scrapy.Field()
    decision_raw = scrapy.Field()
    season = scrapy.Field()
    status = scrapy.Field()
    score1_raw = scrapy.Field()
    score2_raw = scrapy.Field()
    score3_raw = scrapy.Field()
    score4_raw = scrapy.Field()
    notes_raw = scrapy.Field()
