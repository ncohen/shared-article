import logging
import re
import json
import cgi
import datetime
import urllib
import urllib2
import webapp2
import jinja2
import os

class ExtractionService():
	def extract_title(this, url):
		logging.info(this)
		logging.info(url)
		try:
			f = urllib2.urlopen(url)
			html_text = f.read()
			test_string = r"<title>.*title>"
			p = re.compile(test_string, re.IGNORECASE)
			titles_list = p.findall(str(html_text))
			if len(titles_list) > 0:
				title = titles_list[0].replace("<title>", "")
				title = title.replace("</title>", "")
				f.close()
				logging.info(str(title))
				return title
		except:
			return "false"

	def force_utf8(this, string):
		logging.info("got called!")
		if type(string) == str:
			return string
		else:
			return string.decode('utf-8')

	def extract_publisher(this, url):
		try:
			test_string = r"http://(.*?)/"
			p = re.compile(test_string, re.IGNORECASE)
			publishers_list = p.findall(str(url))
			logging.info(len(publishers_list))
			if len(publishers_list) > 0:
				publisher = publishers_list[0]
				logging.info(publisher)
				logging.info(type(publisher))
				publisher = this.force_utf8(publisher)
				logging.info(publisher)
				return str(publisher)
		except:
			publisher = "false"

	def extract_images(this, url):
		try:
			f = urllib2.urlopen(url)
			html_text = f.read()
			test_string = r'<img .*src="(.*\.jpg)"'
			test_string2 = r'<img .*src="(.*\.jpeg)"'
			test_string3 = r'<img .*src="(.*\.png)"'
			p = re.compile(test_string, re.IGNORECASE)
			titles_list = p.findall(str(html_text))
			
			p = re.compile(test_string2, re.IGNORECASE)
			titles_list2 = p.findall(str(html_text))
			
			p = re.compile(test_string3, re.IGNORECASE)
			titles_list3 = p.findall(str(html_text))

			titles_list = titles_list + titles_list2 + titles_list3

			logging.info("images: " + str(len(titles_list)))
			if len(titles_list) > 0:
				for title1 in titles_list:
					logging.info(title1)
				title = titles_list[0]
				f.close()
				logging.info(str(title))
				return title
		except:
			return "false"