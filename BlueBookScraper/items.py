# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class BluebookscraperItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    crn = scrapy.Field()
    semester = scrapy.Field()
    course_label = scrapy.Field()
    instructor = scrapy.Field()
    course_title = scrapy.Field()
    ins_eval = scrapy.Field()
    ins_eval_student_num = scrapy.Field()
    cr_eval = scrapy.Field()
    cr_eval_student_num = scrapy.Field()
    description = scrapy.Field()
    enrollment = scrapy.Field()
    pass
