# from __future__ import unicode_literals
import scrapy

import json

import os

import scrapy

from scrapy.spiders import Spider

from scrapy.http import FormRequest

from scrapy.http import Request

from selenium import webdriver

from chainxy.items import ChainItem

from lxml import etree

from lxml import html

import time

import pdb

import gspread

from oauth2client.service_account import ServiceAccountCredentials

import arrow


class bridgestorage(scrapy.Spider):

	name = 'bridgestorage'

	domain = ''

	history = []

	def __init__(self):

		chrome_options = webdriver.ChromeOptions()

		chrome_options.add_argument("headless")

		self.driver = webdriver.Chrome(chrome_options=chrome_options)

	
	def start_requests(self):

		url = "https://bridgestorage.storageunitsoftware.com"

		yield scrapy.Request(url, callback=self.parse)
		

	def parse(self, response):

		scope = ['https://spreadsheets.google.com/feeds']

		creds = ServiceAccountCredentials.from_json_keyfile_name('./credentials.json', scope)

		client = gspread.authorize(creds)

		sh = client.open_by_url('https://docs.google.com/spreadsheets/d/14CfEYo5yf6_N2dUDf-MZI7KtwnGnO_kyI2-M5hgQYuQ/edit#gid=1941018770')

		sheet = sh.get_worksheet(1)

		origin_data = sheet.get_all_records()

		index = len(origin_data) + 2

		self.driver.get('https://bridgestorage.storageunitsoftware.com/login')

		self.driver.find_element_by_id('username').send_keys("loc")

		self.driver.find_element_by_id('password').send_keys("695812")

		self.driver.find_element_by_name('commit').click()

		self.driver.get('https://bridgestorage.storageunitsoftware.com/reports/rent_roll')

		source = self.driver.page_source.encode("utf8")

		tree = etree.HTML(source)

		rec_list = tree.xpath('//div[@class="report-body"]//tr')

		dump_data = []

		changes_data = []

		addtional_data = []

		transaction_sheet = sh.get_worksheet(3)

		changes_origin_data = transaction_sheet.get_all_records()

		today = arrow.now().format('DD/MM/YYYY')

		for rec in rec_list[1:]:

			item = ChainItem()

			try:

				data = self.eliminate_space(rec.xpath('.//td//text()'))

				if len(data) == 11:

					data.append('')

				for origin in origin_data:

					if str(origin['Unit']) == str(data[0]):

						if str(origin['Rental Rate']) != str(data[8]):

							new_che = [data[2],data[0], today, data[8]]

							if len(changes_origin_data) != 0:

								ch_flag = True

								for che in changes_origin_data:

									if str(che['Unit']) == str(data[0]):

										if str(che['NewRent']) != str(data[8]) and str(che['IncreaseDate']) != str(today):

											changes_data.append(new_che)

										ch_flag = False

								if ch_flag == True:

									changes_data.append(new_che)

							else :

								changes_data.append(new_che)

							addtional_data.append(data)

				dump_data.append(data)

			except:

				pass

		cell_list = sheet.range('A2:L'+str(len(dump_data)+1))

		row_num = 0

		col_num = 0

		for c_idx, cell in enumerate(cell_list):

			try:

				if c_idx > 2 and c_idx % 12 == 0:

					row_num += 1

					col_num = 0

				cell.value = dump_data[row_num][col_num].replace("'", '')

				col_num += 1

			except:

				pass


		sheet.update_cells(cell_list)

		changes_index = len(changes_origin_data) + 2

		changes_list = transaction_sheet.range('A'+str(changes_index)+':D'+str(len(changes_data)+changes_index))

		ch_row_num = 0

		ch_col_num = 0

		for ch_idx, change in enumerate(changes_list):

			try:

				if ch_idx > 2 and ch_idx % 4 == 0:

					ch_row_num += 1

					ch_col_num = 0

				change.value = changes_data[ch_row_num][ch_col_num].replace("'", '')

				ch_col_num += 1

			except:

				pass

		transaction_sheet.update_cells(changes_list)


	def validate(self, item):

		try:

			return item.replace('\n', '').replace('\t','').replace('\r', '').strip()

		except:

			pass


	def eliminate_space(self, items):

	    tmp = []

	    for item in items:

	        if self.validate(item) != '':

	            tmp.append(self.validate(item))

	    return tmp