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
	def extract_content(this, url):
		obj = {}
		try:
			f = urllib2.urlopen(url)
			html_text = f.read()
			logging.info(html_text)
			title = this.extract_title(html_text)
			publisher = this.extract_publisher(url)
			obj['title'] = title
			obj['publisher'] = publisher

			main_content = this.extract_main_content(html_text)
			obj['main_content'] = main_content

			image = this.extract_images(html_text)
			obj['image'] = image

			f.close()
			return obj
		except:
			obj['title'] = "false"
			obj['publisher'] = "false"
			obj['main_content'] = "false"
			obj['image'] = "false"
			return obj

	def extract_main_content(this, html_text):
		test_string = r"<.*?>(.*?)<.*?>"
		p = re.compile(test_string, re.IGNORECASE)
		content_list = p.findall(str(html_text))
		if len(content_list) > 0:
			for content in content_list:
				if len(content) > 500:
					# only send back first main content candidate for now
					content = content[0:500]
					logging.info(content)
					return str(content)
		return "false"

	def extract_title(this, html_text):
		try:
			test_string = r"<title>.*title>"
			p = re.compile(test_string, re.IGNORECASE)
			titles_list = p.findall(str(html_text))
			if len(titles_list) > 0:
				title = titles_list[0].replace("<title>", "")
				title = title.replace("</title>", "")
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

	def extract_images(this, html_text):
		try:
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
				logging.info(str(title))
				return title
		except:
			return "false"