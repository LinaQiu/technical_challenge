#!/usr/bin/env python

import os
import re
import json
from bs4 import BeautifulSoup

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from selenium.common.exceptions import TimeoutException

class GoogleGraper(object):
	"""docstring for GoogleGraper"""
	def __init__(self):
		super(GoogleGraper, self).__init__()
		## Create folder to store results
		self.data_dir = '/scripts/data'
		if not os.path.exists(self.data_dir):
			os.makedirs(self.data_dir)

		## Start remote web driver
		self.driver = webdriver.Remote(command_executor='http://172.20.0.1:4444/wd/hub',
			desired_capabilities=DesiredCapabilities.CHROME)

	def start_crawl_google(self):
		"""	Crawl google career sites """
		
		## Get urls for all pages that contain job summaries
		next_page_urls = self.fetch_next_page_urls(self.driver, "https://careers.google.com/jobs#t=sq&q=j&li=20&l=false&jlo=en-US&")
		print("# of total pages: " + str(len(next_page_urls)))

		## Get urls for all jobs from each job summary page
		job_urls = []
		for page_url in next_page_urls:
			job_urls += self.fetch_job_urls(self.driver, page_url)
		print("# of total jobs: " + str(len(job_urls)))

		## Crawl each job page, to get job details
		all_job_details = []
		for url in job_urls:
			job_details = self.crawl_google_job_page(self.driver, url)
			all_job_details.append(job_details)
		print(len(all_job_details))
		
		## Here, I aggregate details for all jobs in a list, and then write out to a json file.
		self.dump_to_json(all_job_details, self.data_dir+'/google_jobs.json')
		print('Google jobs done!')

		## Close driver after finishing the tasks
		self.driver.close()

	def dump_to_json(self, all_job_details, file_path):
		""" Write all jobs out to a json file """
		with open(file_path, 'w') as outfile:
			json.dump(all_job_details, outfile)

	def fetch_next_page_urls(self, first_page_url):
		""" Fetch urls for all root job pages """
		
		next_page_urls = [first_page_url]
		
		self.driver.get(first_page_url)
		next_page_btn = self.locate_next_page_btn(self.driver)

		while next_page_btn is not None:
			next_page_btn.click()
			next_page_urls.append(self.driver.current_url)
			next_page_btn = self.locate_next_page_btn(self.driver)
		next_page_urls.pop()	# Remove last link, since that page is an empty page

		return(next_page_urls)

	def locate_next_page_btn(self):
		""" Locate the next page button for Google career sites """
		NEXT_PAGE_BUTTON_XPATH = '//button[@type="button"][@aria-label="Next page"]'
		try:
			WebDriverWait(self.driver, 5).until(
				EC.element_to_be_clickable((By.XPATH, NEXT_PAGE_BUTTON_XPATH)))
			return(self.driver.find_element_by_xpath(NEXT_PAGE_BUTTON_XPATH))
		except TimeoutException:
			print("Last page!")
		
	def fetch_job_urls(self, next_page_url):
		""" Fetch urls for <=20 jobs at root job page """
		job_elements = []
		job_urls = []
		
		self.driver.get(next_page_url)
		# Wait for the dynamically loaded elements to show up
		WebDriverWait(self.driver, 5).until(
	    	EC.visibility_of_all_elements_located((By.XPATH, '//a[@class="GXRRIBB-vb-e"]')))
		job_elements += self.driver.find_elements_by_xpath('//a[@class="sr-title text"]') 
		
		for element in job_elements:
			job_urls.append(element.get_attribute('href'))

		return(job_urls)

	def crawl_google_job_page(self, job_url):
		""" Crawl each job page to get detailed information """
		job_details = {}
		self.driver.get(job_url)
		WebDriverWait(self.driver, 5).until(
			EC.visibility_of_element_located((By.XPATH, '//div[@class="job-disclaimer caption secondary-text item"]')))
		soup = BeautifulSoup(self.driver.page_source, 'html.parser')

		company = (soup.find('div', 'company-name-panel')).text
		title = (soup.find('a', 'title text')).text
		location = (soup.find('a', 'details-location body1 secondary-text')).text

		job_details.update({'company': company, 'title': title, 'location': location})
		for description in soup.find_all('div', re.compile('^description-section(\s)?(.)*')):
			job_details[' '.join((description.attrs)['class'])] = description.text
		return(job_details)

if __name__ == '__main__':
	scraper = GoogleGraper()
	scraper.start_crawl_google()