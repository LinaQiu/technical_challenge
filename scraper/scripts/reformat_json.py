#!/usr/bin/env python

import json

class Reformat(object):
	"""docstring for Reformat"""
	def __init__(self):
		super(Reformat, self).__init__()
		self.ROOT = '/scripts/data'
		self.ID = 1

	def reformat(self):
		f = open(self.ROOT+'/all_jobs.txt',"a")
		google_json = self.read_json('/google_jobs.json')
		microsoft_json = self.read_json('/microsoft_jobs.json')

		self.reformat_google_to_txt(google_json, f)
		self.reformat_microsoft_to_txt(microsoft_json, f)

		f.close()
		print('Done.')

	def read_json(self, input_path):
		# Reading data back
		with open(self.ROOT+input_path, 'r') as f:
			data = json.load(f)
		return(data)

	# MySQL table format:
	# | id          | smallint(5) unsigned | NO   | PRI | NULL    | auto_increment |
	# | company     | varchar(255)         | YES  |     | NULL    |                |
	# | title       | varchar(255)         | YES  |     | NULL    |                |
	# | location    | varchar(255)         | YES  |     | NULL    |                |
	# | description | text                 | YES  |     | NULL    |                |
	# 
	def reformat_google_to_txt(self, json_str, f):
		
		for item in json_str:
			title = item['title']
			company = item['company'].replace(' ','')
			location = item['location']
			description = 'description-section: '+item['description-section']+';'+\
				'description-section text: '+item['description-section text']+';'+\
				'description-section text with-benefits: '+item['description-section text with-benefits']

			f.write(str(self.ID)+'\t'+company+'\t'+title+'\t'+location+'\t'+description+'\n')
			self.ID+=1

	def reformat_microsoft_to_txt(self, json_str, f):
		
		for item in json_str:
			title = ','.join([item['Focus area'], item['Education level'], item['Job type']])
			company = item['company'].replace(' ','')
			location = item['Location']
			description = item['description'].replace('\n',' ')
			f.write(str(self.ID)+'\t'+company+'\t'+title+'\t'+location+'\t'+description+'\n')
			self.ID+=1

if __name__ == '__main__':
	formater = Reformat()
	formater.reformat()
