#!/usr/bin/env python

import os
import json
from bs4 import BeautifulSoup
from urllib.parse import urljoin

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from selenium.common.exceptions import TimeoutException, NoSuchElementException, StaleElementReferenceException

class MicrosoftScraper(object):
	"""docstring for MicrosoftScraper"""
	def __init__(self):
		super(MicrosoftScraper, self).__init__()
		## Create folder to store results
		self.data_dir = '/scripts/data'
		if not os.path.exists(self.data_dir):
			os.makedirs(self.data_dir)

		## https://careers.microsoft.com/students/apply?rg=US&jf=9&el=2&jt=1
		self.base_url = 'https://careers.microsoft.com/students/apply?'

		## Start remote web driver
		self.driver = webdriver.Remote(command_executor='http://172.20.0.1:4444/wd/hub',
			desired_capabilities=DesiredCapabilities.CHROME)

	def start_crawl_microsoft(self):
		""" Crawler for Microsoft career sites"""
		self.driver.get(self.base_url)
		
		options_values = self.fetch_form_groups()
		summary_page_urls = self.get_summary_page_urls(options_values[0], 
			options_values[1], options_values[2], options_values[3])
		print("# of summary page urls: "+str(len(summary_page_urls)))

		all_job_details = []
		for url in summary_page_urls:
			## Find the job urls, and pop up window frames
			print(url)
			all_job_details+=self.crawl_job_details(url)

		# print(json.dumps(all_job_details, indent=4, sort_keys=True))
		self.dump_to_json(all_job_details, self.data_dir+'/microsoft_jobs.json')
		print('Microsoft jobs done!')

		## Close driver after finishing the tasks
		self.driver.close()

	def dump_to_json(self, all_job_details, file_path):
		""" Write all jobs out to a json file """
		with open(file_path, 'w') as outfile:
			json.dump(all_job_details, outfile)


	def crawl_job_details(self, summary_page_url):
		""" Fetch part of job details and the url of the detail pop-up window """
		jobs = []
		self.driver.get(summary_page_url)
		try:
			table_xpath = '//table[@class="table table-striped table-condensed"]'
			WebDriverWait(self.driver, 5).until(
				EC.visibility_of_element_located((By.XPATH, table_xpath)))
			table = self.driver.find_element_by_xpath(table_xpath)
		
			head_row = table.find_elements_by_tag_name('th')
			ncols = len(head_row)
			
			table_rows_xpath = '//tbody/tr'
			WebDriverWait(self.driver, 5).until(
				EC.visibility_of_all_elements_located((By.XPATH, table_rows_xpath)))
			table_rows = table.find_elements_by_xpath(table_rows_xpath)
	
			for row in table_rows:
				job_details = row.find_elements_by_tag_name('td')
				job_info = {}
				job_info['company'] = 'Microsoft'
				for i in range(ncols):
					job_info[(head_row[i]).text] = (job_details[i]).text
				
				details_btn = job_details[4].find_element_by_link_text('Details')
				job_info['description']=self.get_job_descriptions(details_btn)
				jobs.append(job_info)
			
		except (NoSuchElementException, TimeoutException):
			print('No postion match!')
		
		return(jobs)

	def get_job_descriptions(self, details_btn):
		""" Click button to get job descriptions """
		
		MODAL_BODY_XPATH = '//div[@class="modal-body"]'
		details_btn.click()
		WebDriverWait(self.driver, 5).until(
			EC.visibility_of_element_located((By.XPATH, MODAL_BODY_XPATH)))

		job_description = self.driver.find_element_by_xpath(MODAL_BODY_XPATH).text

		WebDriverWait(self.driver, 5).until(
			EC.visibility_of_element_located((By.XPATH, '//button[@type="button"][@class="close"]')))
		(self.driver.find_element_by_xpath('//button[@type="button"][@class="close"]')).click()

		return(job_description)
		

	def get_summary_page_urls(self, country_codes, focus_areas, edu_levels, job_types):
		""" Get urls for summary pages, based on the difference combinations of the options. """
		summary_page_urls = []
		
		el_paras = '&el='.join(edu_levels)
		jt_paras = '&jt='.join(job_types)
		for code in country_codes:
			for area in focus_areas:
				summary_page_urls.append(self.base_url+"rg="+code+"&jf="+area+el_paras+jt_paras)
		return(summary_page_urls)

	def fetch_form_groups(self):
		""" Load the base url to fetch values of the four form groups (rg, jf, el, jt) """
		country_codes = self.fetchDropdownOptions('SelectedCountry')
		focus_areas = self.fetchDropdownOptions('SelectedJobFamily')
		edu_levels = self.fetchCheckboxOptions('elgroup')
		job_types = self.fetchCheckboxOptions('jtgroup')
		
		print("# of codes: "+str(len(country_codes)))
		print("# of focus_areas: "+str(len(focus_areas)))
		return([country_codes, focus_areas, edu_levels, job_types])


	def fetchDropdownOptions(self, id_):
		""" Get the values of all options in the drop down list. """
		element = Select(self.driver.find_element_by_id(id_))
		all_options = [
			'%s' % option.get_attribute('value')
				for option in
					element.options]
		return(all_options)

	def fetchCheckboxOptions(self, id_):
		""" Get the values of all options of the checkbox list. """
		element = self.driver.find_element_by_id(id_)
		all_options = [
			'%s' % checkbox.get_attribute('value')
				for checkbox in 
					element.find_elements_by_xpath('//input[@type="checkbox"]')]
		return(all_options)

if __name__ == '__main__':
	scraper = MicrosoftScraper()
	scraper.start_crawl_microsoft()
