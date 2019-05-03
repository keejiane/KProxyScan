#!/usr/bin/env python
# -*- coding: utf-8 -*-
# author: kw0ng

import sys
import pymongo
import datetime
import urlparse
from libmproxy import flow
from libmproxy.proxy import ProxyServer, ProxyConfig
from config import mitm_config, mongo_db


class RequestCollector(flow.FlowMaster):
	def run(self):
		self.mongodb_init()
		try:
			flow.FlowMaster.run(self)
		except KeyboardInterrupt:
			self.shutdown()

	@staticmethod
	def mongodb_init():
		conn = pymongo.MongoClient(host=mongo_db['host'], port=mongo_db['port'])
		db = conn.mitmproxy
		collection = db.requests
		return collection

	def mongodb_insert(self, request):
		insert_dict = {}
		if request:
			insert_dict = {
				'time': datetime.datetime.now(),
				'req': {
					'url': request['url'],
					'method': request['method'],
					'data': request['data'],
					'referer': request['referer'],
					'cookies': request['cookies']
				},
				'req_text': request['req_text'],
				'sorted_params': request['sorted_params'],
				'sqli_status': 0,
				'xss_status': 0,
				'xss_dom_status': 0,
				'redirect_status': 0
			}

		try:
			self.mongodb_init().insert(insert_dict)
		except Exception, e:
			print e.message

		return

	def handle_request(self, f):
		f = flow.FlowMaster.handle_request(self, f)
		if f:
			f.reply()
		# print type(f.request)
		return f

	def handle_response(self, f):
		global whitelist
		f = flow.FlowMaster.handle_response(self, f)
		if f:
			url = f.request.url
			urlp = urlparse.urlparse(url)
			# scheme = f.request.scheme
			# path = f.request.path
			method = f.request.method
			# host = f.request.host
			req_body = f.request.body
			req_headers = f.request.headers
			res_code = f.response.status_code
			try:
				content_type = f.response.headers['content-type']
				content_type = content_type.split(';')[0]
			except KeyError:
				content_type = ''

			try:
				req_referer = req_headers['Referer']
			except KeyError:
				req_referer = ''

			try:
				req_cookies = req_headers['Cookie']
			except KeyError:
				req_cookies = ''

			# req_cookies = f.request.cookies
			# req_text = self.get_raw_request(f.request)
			req_text = self.get_raw_request(f.request)

			# 判断需要的数据包
			insert_status = 0
			if not whitelist:
				print 'Whitelist is empty, Quit!!!'
				sys.exit(0)

			for i in whitelist:
				if urlp.netloc.endswith(i):
					insert_status = 1
					break

			if (method == 'GET' and urlp.query) or (method == 'POST' and (urlp.query or req_body)):
				if 'text/html' in content_type or 'application/json' in content_type:
					if insert_status and res_code == 200:
						sorted_params = self.sort_param(f.request)
						isdupicate = self.check_duplicate(sorted_params)
						if url and isdupicate:
							print "Url is unique, inserting to db..."
							req = {
								'url': url,
								'method': method,
								'referer': req_referer,
								'cookies': req_cookies,
								'data': req_body,
								'sorted_params': sorted_params,
								'req_text': req_text
							}

							if len(url) < 2048:
								self.mongodb_insert(req)
								print "Url:%s\r\nis inserted~~~" % url
							else:
								print "Url:%s \r\nis too large than 2048 bytes, drop it..." % url
						else:
							print "Url:%s\r\nis duplicate..." % url

			f.reply()
		return f

	@staticmethod
	def get_raw_request(request):
		# Get raw http request body
		text = ""
		method = request.method
		url = request.url
		urlp = urlparse.urlparse(url)
		body = request.body
		headers = request.headers
		protocol = 'HTTP/1.1'
		if not urlp.fragment and not urlp.query:
			link = "%s" % urlp.path
		elif not urlp.fragment:
			link = "%s?%s" % (urlp.path, urlp.query)
		elif not urlp.query:
			link = "%s#%s" % (urlp.path, urlp.fragment)
		else:
			link = "%s?%s#%s" % (urlp.path, urlp.query, urlp.fragment)
		text += "%s %s %s\r\n" % (method, link, protocol)
		text += bytes(headers)
		text += "\r\n"
		if body:
			text += body
		return text

	def check_duplicate(self, params):
		unduplicate = True
		if params and len(params) < 2048:
			res = self.mongodb_init().find({"sorted_params": params}).count()
			if res > 0:
				unduplicate = False
		return unduplicate

	@staticmethod
	def sort_param(request):
		all_params = []
		url = request.url
		urlp = urlparse.urlparse(url)
		if not request.body:
			if urlp.query:
				get_params = urlparse.parse_qs(urlp.query).keys()
				get_params.sort()
				all_params = get_params

		elif not urlp.query:
			post_params = urlparse.parse_qs(request.body).keys()
			post_params.sort()
			all_params = post_params

		elif request.body and urlp.query:
			get_params = urlparse.parse_qs(urlp.query).keys()
			post_params = urlparse.parse_qs(request.body).keys()
			get_params.extend(post_params)
			all_params = get_params

		sorted_params = '&'.join(all_params)
		# 添加路径path
		sorted_params = '%s://%s?%s' % (urlp.scheme, urlp.netloc, sorted_params)
		return sorted_params

"""
with open('blacklist', 'r') as ff:
	domains = ff.xreadlines()
	for domain in domains:
		domain = domain.strip().rstrip()
		if domain.find('#'):
			continue

		blacklist.append(domain)
"""

if __name__ == '__main__':
	whitelist = []
	config = ProxyConfig(
		host=mitm_config['host'],
		port=mitm_config['port'],
		# use ~/.mitmproxy/mitmproxy-ca.pem as default CA file.
		cadir="~/.mitmproxy/"
	)

	with open('whiteLists.txt', 'r') as ff:
		domains = ff.xreadlines()
		for domain in domains:
			domain = domain.strip().rstrip()
			if domain.find('#') != -1:
				continue

			whitelist.append(domain)
			print domain
		print "will be scan."

	state = flow.State()
	server = ProxyServer(config)
	m = RequestCollector(server, state)
	print "MITMProxy is running on localhost..."
	m.run()
