# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

from scrapy.item import Item, Field


class ChainItem(Item):

    unit = Field()

    type = Field()

    name = Field()

    moved_in = Field()

    billing_day = Field()

    tax_exempt = Field()

    security_deposit = Field()

    standard_rate = Field()

    rental_rate = Field()

    variance = Field()

    charge_balance = Field()

    paid_to = Field()

