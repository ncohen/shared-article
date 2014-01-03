from extraction_service import ExtractionService
import cgi
import re
import datetime
import urllib
import urllib2
import webapp2
import jinja2
import os
import logging
import random
import calendar
import email
import json

from google.appengine.api import channel
from google.appengine.api import users
from google.appengine.api import images
from google.appengine.ext import blobstore
from google.appengine.ext import webapp
from google.appengine.ext.webapp.util import run_wsgi_app

from google.appengine.ext import db
from google.appengine.api import mail
from google.appengine.ext.webapp.mail_handlers import InboundMailHandler

extract = ExtractionService()

jinja_environment = jinja2.Environment(
    loader=jinja2.FileSystemLoader(os.path.dirname(__file__)))

class ProposedOuting(db.Model):
	outing_id = db.StringProperty()
	link = db.StringProperty()
	participants = db.StringListProperty()
	article_title = db.StringProperty()
	publisher = db.StringProperty()
	originator = db.UserProperty()
	post_text = db.TextProperty()
	proposed_date = db.DateTimeProperty()
	timestamp = db.DateTimeProperty()
	utc_timestamp = db.IntegerProperty()
	string_timestamp = db.StringProperty()
	latest_activity = db.DateTimeProperty()
	comment_count = db.IntegerProperty()
	main_content = db.TextProperty()
	article_image = db.StringProperty()

def outing_key(outing=None):
	return db.Key.from_path('outing', outing or 'default_name')

class User(db.Model):
	user_email = db.StringProperty()
	read_articles = db.StringListProperty()
	latest_seen = db.DateTimeProperty()

def user_key(user=None):
	return db.Key.from_path('user', user or 'default_name')

class Comment(db.Model):
	comment_text = db.TextProperty()
	commenter = db.UserProperty()
	timestamp = db.DateTimeProperty()
	utc_timestamp = db.IntegerProperty()
	parent_id = db.StringProperty()

def comment_key(comment=None):
	return db.Key.from_path('comment', comment or 'default_name')

def convert_timestamp(timestamp):
	return calendar.timegm(timestamp.utctimetuple())

class MainPage(webapp2.RequestHandler):
  def get(self):

  	user = users.get_current_user()
  	if user:

  		# check if first time user
  		user_query = User.all()
  		user_query.filter('user_email =', user.email())
  		current_user = user_query.fetch(1)
  		if len(current_user) == 0:
  			logging.info("0")
  			this_user = User()
  			this_user.user_email = user.email()
  			this_user.put()
  			current_user = this_user
  		else:
  			current_user = current_user[0]
  		
  		shares_query = ProposedOuting.all()
  		shares_query.filter('originator =', user)
  		shares_query.order('-timestamp')
  		shares = shares_query.fetch(25)

  		email = user.email()
  		shared_query = ProposedOuting.all()
  		shared_query.filter('participants =', email)
  		shared_query.order('-timestamp')
  		shared = shared_query.fetch(25)
  		logging.info(len(shared))
  		logging.info(email)

  		full_list = shares + shared
  		full_list.sort(key = lambda x: x.latest_activity, reverse=True)

  		ary2 = []
  		ary3 = []
  		for item in full_list:

  			# create display version of utc timestamps
  			s = datetime.datetime.fromtimestamp(item.utc_timestamp)
  			item.string_timestamp = str(s)

  			ary3.append(item.outing_id)
  			try:
  				if item.latest_activity > current_user.latest_seen:
  					ary2.append(str(item.outing_id))
  			except:
  				ary2 = []

  		ary = json.dumps(current_user.read_articles)
  		logging.info(len(ary2))


  		# extract comments
  		comments_query = Comment.all()
  		comments_query.filter('parent_id IN', ary3)
  		comments = comments_query.fetch(20)
  		logging.info(len(comments))  		

		comments_obj = {};
		for comment in comments:
			obj1 = {}
			obj1['comment_text'] = comment.comment_text
			obj1['commenter'] = comment.commenter.email()
			# obj1['timestamp'] = comment.timestamp
			obj1['utc_timestamp'] = comment.utc_timestamp
			comments_obj[comment.parent_id]= obj1

		logging.info(comments_obj)
		comments_obj = json.dumps(comments_obj)
		logging.info(comments_obj)

		# create token for web socket creation
		token = channel.create_channel(user.user_id())
		logging.info(token)

		template_values = {
		'user_id': user.user_id(),
		'token': token,
  		'comments_obj': comments_obj,
  		'comments': comments,
  		'new_articles': ary2,
  		'read_articles': ary,
  		'current_user': current_user,
  		'shares': full_list
  		}

  		template = jinja_environment.get_template('index.html')
  		self.response.out.write(template.render(template_values))  


  		# update read list
  		second_user_query = User.all()
  		second_user_query.filter('user_email =', user.email())
  		second_current_user = second_user_query.fetch(1)
  		second_current_user = second_current_user[0]
  		if len(full_list) > 0:
  			second_current_user.latest_seen = full_list[0].latest_activity
  			second_current_user.put()

  		# for item in full_list:
  			# second_current_user.read_articles.append(item.outing_id)
  			# ary = set(second_current_user.read_articles)
  			# ary = list(ary)
  			# second_current_user.read_articles = ary
  			# second_current_user.put()

  	else:
  		self.redirect(users.create_login_url(self.request.uri))

class CreateOuting(webapp2.RequestHandler):
	def get(self):
		user = users.get_current_user()
		if user:
			template_values = {
			'user_email': user.email(),
			}

			template = jinja_environment.get_template('create_outing.html')
			self.response.out.write(template.render(template_values))
		else:
			self.redirect(users.create_login_url(self.request.uri))


class UploadOuting(webapp2.RequestHandler):
	def post(self):
		user = users.get_current_user()
		if user:
			outings = self.request.get('outings')
			outing = ProposedOuting(parent=outing_key(outings))
			link = self.request.get('url')
			proposed_participants = self.request.get('participants')
			originator = users.get_current_user()
			logging.info("originator = " + str(originator))
			logging.info('len = ' + str(len(proposed_participants)))
			timestamp = datetime.datetime.now()
			utc_timestamp = convert_timestamp(timestamp)
			outing.timestamp = timestamp
			outing.utc_timestamp = utc_timestamp
			outing.latest_activity = timestamp
			outing.comment_count = 0
			outing.link = link
			outing.post_text = self.request.get('post_text')
			participants = proposed_participants.split(",")
			ary = []
			for participant in participants:
				participant = participant.rstrip()
				ary.append(participant)
				outing.participants = ary
			outing.originator = originator

			for participant in outing.participants:
				logging.info('participant:' + participant)

			key = outing.put()
			key = str(key)
			outing.outing_id = key

			# extract title of article
			obj = extract.extract_content(link)
			title = obj['title']
			try:
				outing.article_title = title.decode('latin1')
			except:
				outing.article_title = "false"

			publisher = obj['publisher']
			try:
				outing.publisher = str(publisher)
			except:
				outing.publisher = "false"

			main_content = obj['main_content']
			logging.info(main_content)
			try:
				outing.main_content = main_content.decode('latin1')
			except:
				outing.main_content = "false"

			image = obj['image']
			logging.info("IMAGE!" + str(image))
			try:
				outing.article_image = str(image)
			except:
				outing.article_image = "false"

			outing.put()

			# prepare email and send
			message = mail.EmailMessage()
			message.sender= "Article Share <messages@singlecalendar.appspotmail.com>"
			message.to = proposed_participants
			message.subject = str(originator) + " shared an article"
			message.body = "Check out this article and share your thoughts: http://singlecalendar.appspot.com/outing/" + str(key)
			# message.html = '<p>Check out this article and share your thoughts: '+ str(title) + '</p><br><p>' + str(main_content) + '</p><a href="http://singlecalendar.appspot.com/outing/' + str(key) + '">read more</a>' 
			message.html = '<p>Check out this article and share your thoughts: '+ str(title) + '</p><br><a href="http://singlecalendar.appspot.com/outing/' + str(key) + '">read more</a>' 
			message.send()

			# self.redirect('/outing/' + urllib.urlencode({'id': key}))	
			self.redirect('/outing/' + str(key))
		else:
			self.redirect('/extension')

class OutingDirect(webapp2.RequestHandler):
	def get(self, outing_id):
		user = users.get_current_user()
		if user:
			outing = db.get(outing_id)

			comment_query = Comment.all()
			comment_query.filter('parent_id =', outing_id)
			comment_query.order('-timestamp')
			comments = comment_query.fetch(10)

			# comments = outing.comments
			# comments = json.loads(comments)

			# array = outing.comments
			# ary = []
			# for com in array:
				# new_com = json.loads(com)
				# ary.append(new_com)

			# comments = ary

			template_values = {
			'logged_in': 'true',
			'comments': comments,
			'originator': outing.originator,
			'participants': outing.participants,
			'link': outing.link,
			'post_text': outing.post_text,
			'post': outing
			}
		
		else:
			outing = db.get(outing_id)
			comment_query = Comment.all()
			comment_query.filter('parent_id =', outing_id)
			comment_query.order('-timestamp')
			comments = comment_query.fetch(10)

			template_values = {
			'logged_in': 'false',
			'comments': comments,
			'originator': outing.originator,
			'participants': outing.participants,
			'link': outing.link,
			'post_text': outing.post_text,
			'post': outing
			}
			# self.redirect(users.create_login_url(self.request.uri))

		template = jinja_environment.get_template('outing_direct.html')
		self.response.out.write(template.render(template_values))

class Login(webapp2.RequestHandler):
	def get(self, outing):
		self.redirect(users.create_login_url('/outing/' + str(outing)))

class CreateComment(webapp2.RequestHandler):
	def post(self):
		comments = self.request.get('comments')
		comment = Comment(parent=comment_key(comments))
		comment_text = self.request.get('comment')
		parent_id = self.request.get('parent_id')
		commenter = users.get_current_user()
		timestamp = datetime.datetime.now()
		utc_timestamp = convert_timestamp(timestamp)

		# grab relevant post object
		post = db.get(parent_id)
		# comments_obj = post.comments
		# comments_obj = json.loads(comments_obj)

		# obj = {}
		# obj['commenter'] = commenter.email()
		# obj['comment_text'] = comment_text

		# comments_obj[timestamp] = obj

		# comments_obj = str(comments_obj)
		# post.comments = json.dumps(comments_obj)

		# update latest_activity on the original post
		post.latest_activity = timestamp
		post.comment_count += 1

		# reinsert post into datastore
		post.put()

		comment.comment_text = comment_text
		comment.commenter = commenter
		comment.timestamp = timestamp
		comment.utc_timestamp = utc_timestamp
		comment.parent_id = parent_id
		comment.put()

		participants = post.participants
		email_list = participants
		originator_email = post.originator.email()
		email_list.append(originator_email)
		user = users.get_current_user()

		message = mail.EmailMessage()
		message.sender= "Article Share <messages@singlecalendar.appspotmail.com>"
		message.to = email_list
		message.subject = str(user.nickname()) + " commented on an article"
		message.body = str(comment_text) + " -- read the rest here: http://singlecalendar.appspot.com/outing/" + str(parent_id)
		message.html = '<p>' + str(comment_text) + '</p> <p>Read the rest here: <a href="http://singlecalendar.appspot.com/outing/' + str(parent_id) + '">http://singlecalendar.appspot.com/outing/' + str(parent_id) + '</a></p>' 
		message.send()

		self.redirect('/outing/' + str(parent_id))

class LogSenderHandler(InboundMailHandler):
	def receive(self, mail_message):
		logging.info("Received a message from: " + mail_message.sender)
		logging.info(mail_message.html)

"""        
		message = mail.InboundEmailMessage(self.request.body)
		logging.info('got the message')
		logging.info(message.subject)
		body = message.body
		logging.info(len(body))
"""		

class CommentMigration(webapp2.RequestHandler):
	def get(self):
		shares_query = ProposedOuting.all()
		shares = shares_query.fetch(100)
		for share in shares:
			share.comment_count = 0
			share.utc_timestamp = convert_timestamp(share.timestamp)
			share.put()

class SetLatestActivity(webapp2.RequestHandler):
	def get(self):
		shares_query = ProposedOuting.all()
		shares = shares_query.fetch(100)
		for share in shares:
			share.latest_activity = share.timestamp
			share.put()

class ExtensionSignIn(webapp2.RequestHandler):
	def get(self):
		user = users.get_current_user()
		if user:
			template = jinja_environment.get_template('extension_signin.html')
			self.response.out.write(template.render())
		else:
			self.redirect(users.create_login_url(self.request.uri))

class ShortenMainContent(webapp2.RequestHandler):
	def get(self):
		shares_query = ProposedOuting.all()
		shares = shares_query.fetch(100)
		for share in shares:
			try:
				if len(share.main_content) > 501:
					content = share.main_content[0:500]
					share.main_content = content
					share.put()
			except:
				logging.info("exception")

app = webapp2.WSGIApplication([('/', MainPage),
							('/create', CreateOuting),
							('/create_new_outing', UploadOuting),
							('/create_comment', CreateComment),
							('/outing/(\S+)', OutingDirect),
							('/login/(\S+)', Login),
							('/migrate', CommentMigration),
							('/extension', ExtensionSignIn),
							('/shorten', ShortenMainContent),
							('/activityreset', SetLatestActivity),
							(LogSenderHandler.mapping())],
                              debug=True)