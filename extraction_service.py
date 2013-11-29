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
	def get_size(this, url):
		logging.info("get_size")
		logging.info("get_size" + str(url))
		fil = urllib2.urlopen(url)
		bits = fil.read()
		size = len(bits)
		fil.close()
		return size	

	def extract_content(this, url):
		obj = {}
		try:
			f = urllib2.urlopen(url)
			html_text = f.read()
			logging.info(html_text)
			f.close()

			try:
				title = this.extract_title(html_text)
				obj['title'] = title
			except:
				obj['title'] = "false"

			try:
				main_content = this.extract_main_content(html_text)
				obj['main_content'] = main_content
			except:
				obj['main_content'] = "false"

			try:
				image = this.extract_images(html_text)
				obj['image'] = image
			except:
				obj['image'] = "false"

			try:
				publisher = this.extract_publisher(url)
				obj['publisher'] = publisher
				logging.info("FIRST LETTER " + str(obj['image'][0]))
				logging.info(str(obj['image']))
				if obj['image'][0] == "/":
					logging.info("Found the /")
					obj['image'] = publisher + obj['image']
					logging.info(obj['image'])
			except:
				obj['image'] = "false"

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

		test_string2 = r"(\s)"
		q = re.compile(test_string2, re.IGNORECASE)

		main_cont = ""

		if len(content_list) > 0:
			cnt = 0
			logging.info(len(content_list))
			for content in content_list:
				cnt2 = len(content)
				if cnt2 > cnt:
					content_list2 = q.findall(str(content))

					logging.info(str(len(content)) + " / " + str(len(content_list2)))
					if len(content_list2) > 0:
						whitespace_ratio = (len(content) / len(content_list2))
						logging.info("WHITESPACE RATIO " + str(whitespace_ratio))
						logging.info("LENGTH " + str(len(content)))
						if whitespace_ratio < 10 and len(content) > 100:
							logging.info(len(content))
							logging.info(content)
							main_cont = content[0:250]
							cnt = cnt2

			logging.info("MAIN CONTENT " + str(main_cont))

			if len(main_cont) > 99:
				logging.info(main_cont)
				return str(main_cont)
		if len(main_cont) <= 99:
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
				string = title.split('|')
				title = string[0]
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
			test_string = r'<img .*src="(.*\.jpg).*"'
			test_string2 = r'<img .*src="(.*\.jpeg).*"'
			test_string3 = r'<img .*src="(.*\.png).*"'
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
					try:
						logging.info("Trying...")
						size = this.get_size(title1)
						logging.info("SIZE: " + str(size))
					except:
						logging.info("SIZE DID NOT WORK")

				title = titles_list[0]
				logging.info(str(title))
				return title
		except:
			return "false"