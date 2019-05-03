#!/usr/bin/env python
# -*- coding: utf-8 -*-
# author: kw0ng

import pymongo
from config import mongo_db
from bson.objectid import ObjectId


class TaskStatus(object):
	def __init__(self):
		self.conn = pymongo.MongoClient(host=mongo_db['host'], port=mongo_db['port'])
		self.db = self.conn.mitmproxy
		self.collection = self.db.requests

		return

	def set_sqli_checking(self, task_id):
		self.collection.update({'_id': ObjectId(task_id)}, {'$set': {'sqli_status': 1}})

	def set_sqli_checked(self, task_id):
		self.collection.update({'_id': ObjectId(task_id)}, {'$set': {'sqli_status': 2}})

	def set_xss_checking(self, task_id):
		self.collection.update({'_id': ObjectId(task_id)}, {'$set': {'xss_status': 1}})

	def set_xss_checked(self, task_id):
		self.collection.update({'_id': ObjectId(task_id)}, {'$set': {'xss_status': 2}})

	def set_xss_dom_checking(self, task_id):
		self.collection.update({'_id': ObjectId(task_id)}, {'$set': {'xss_dom_status': 1}})

	def set_xss_dom_checked(self, task_id):
		self.collection.update({'_id': ObjectId(task_id)}, {'$set': {'xss_dom_status': 2}})

	def set_redirect_checking(self, task_id):
		self.collection.update({'_id': ObjectId(task_id)}, {'$set': {'redirect_status': 1}})

	def set_redirect_checked(self, task_id):
		self.collection.update({'_id': ObjectId(task_id)}, {'$set': {'redirect_status': 2}})
