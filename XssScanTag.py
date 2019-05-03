#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Author: Kw0ng

import bs4
import json
import re
import requests
import sys
import threading
import urllib2
from bs4 import BeautifulSoup as BS


from models import *


class Thread(threading.Thread):
	def __init__(self, func, args):
		super(Thread, self).__init__()
		self.func = func
		self.args = args

	def run(self):
		self.func(*self.args)


class XssScanTag(object):
	def __init__(self, url, method, data, cookies, referer, user_agent):
		self.enc = "utf-8"
		requests.packages.urllib3.disable_warnings()

		self.url = url
		self.headers = {
			"User-Agent": user_agent,
			"Referer": referer
		}

		self.cookies = cookies

		self.urls = []
		self.payloads = json.load(open("XssScanTagPayload.json"))

		self.testUrls = {
			"betweenCommonTag": [],
			"betweenTitle": [],
			"betweenTextarea": [],
			"betweenXmp": [],
			"betweenIframe": [],
			"betweenNoscript": [],
			"betweenNoframes": [],
			"betweenPlaintext": [],
			"betweenScript": [],
			"betweenStyle": [],
			"utf-7": [],
			"inSrcHrefAction": [],
			"inScript": [],
			"inStyle": [],
			"inCommonAttr": [],
			"inMetaRefresh": []
		}
		self.result = []

	def request_url(self, url):
		try:
			r = requests.get(url, headers=self.headers, cookies=self.cookies, timeout=30, verify=False)
			html = r.text
			soup = BS(html, "lxml")
			r.close()

		except Exception, e:
			print "request_url failed: %s" % e
			html = ''
			soup = ''
			r = ''
		# pass

		return r, html, soup

	def judge_charset(self):
		(r, html, soup) = self.request_url(self.url)

		try:
			if ("gb" in r.headers["content-type"].lower()
			    or ("utf" not in r.headers["content-type"].lower()
			        and bool(soup.meta) and "gb" in soup.meta["content"].lower())):
				self.enc = "gbk"

		except Exception as e:
			print e.message

	def judge_out(self, url, keyword, list_):
		(r, html, soup) = self.request_url(url)

		try:
			if keyword in html:
				list_.append(url)

		except Exception as e:
			print "judge_out failed %s" % e.message

	def find_paras(self):
		query = urllib2.urlparse.urlparse(self.url).query
		paras = query.split("&")
		test_paras = {}

		for i in paras:
			if i == paras[0]:
				if "=" not in i:
					test_paras["?" + i] = "?" + i + "=sEc0307"
				elif i.endswith("="):
					test_paras["?" + i] = "?" + i + "sEc0307"
				else:
					test_paras["?" + i] = "?" + i.replace(i[i.rindex("=") + 1:], "sEc0307")
			else:
				if "=" not in i:
					test_paras["&" + i] = "&" + i + "=sEc0307"
				elif i.endswith("="):
					test_paras["&" + i] = "&" + i + "sEc0307"
				else:
					test_paras["&" + i] = "&" + i.replace(i[i.rindex("=") + 1:], "sEc0307")

		threads = [Thread(self.judge_out, (self.url.replace(i, test_paras[i]), "sEc0307", self.urls)) for i in
		           test_paras]
		for i in threads:
			i.start()
		for i in threads:
			i.join()

	def get_children_tags(self, tag, tag_list):
		try:
			for i in tag.children:
				if type(i) == bs4.element.Tag:
					tag_list.append(i)
					self.get_children_tags(i, tag_list)

		except Exception as e:
			print "get_children_tags something wrong: %s" % e.message

	def judge_location(self, url):
		(r, html, soup) = self.request_url(url)

		tag_list = []
		self.get_children_tags(soup, tag_list)

		re_key = re.compile("sEc0307")
		if soup.findAll(text=re_key):
			for i in soup.findAll(text=re_key):
				if i.findParent("title"):
					self.testUrls["betweenTitle"].append(url)
				elif i.findParent("textarea"):
					self.testUrls["betweenTextarea"].append(url)
				elif i.findParent("xmp"):
					self.testUrls["betweenXmp"].append(url)
				elif i.findParent("iframe"):
					self.testUrls["betweenIframe"].append(url)
				elif i.findParent("noscript"):
					self.testUrls["betweenNoscript"].append(url)
				elif i.findParent("noframes"):
					self.testUrls["betweenNoframes"].append(url)
				elif i.findParent("plaintext"):
					self.testUrls["betweenPlaintext"].append(url)
				elif i.findParent("script"):
					self.testUrls["betweenScript"].append(url)
				elif i.findParent("style"):
					self.testUrls["betweenStyle"].append(url)
				else:
					self.testUrls["betweenCommonTag"].append(url)

		if soup.findAll(name="meta", attrs={"http-equiv": "Refresh", "content": re.compile("sEc0307")}):
			self.testUrls["inMetaRefresh"].append(url)

		if html.startswith("sEc0307"):
			self.testUrls["utf-7"].append(url)

		for i in tag_list:
			for j in i.attrs:
				if "sEc0307" in i.attrs[j]:
					self.testUrls["inCommonAttr"].append(url)

					if j in ["src", "href", "action"] and i.attrs[j].startswith("sEc0307"):
						self.testUrls["inSrcHrefAction"].append(url)

					elif (j.startswith("on")
					      or (j in ["src", "href", "action"] and i.attrs[j].startswith("javascript:"))):
						self.testUrls["inScript"].append(url)

					elif j == "style":
						self.testUrls["inStyle"].append(url)

	@staticmethod
	def confirm_parent_tag(soup):
		for i in soup.findAll("x0307x"):
			for j in i.parents:
				if j.name in ("title", "textarea", "xmp", "iframe", "noscript", "noframes", "plaintext"):
					return False

		return True

	def confirm_in_script(self, soup, payload):
		tag_list = []
		self.get_children_tags(soup, tag_list)
		for i in tag_list:
			for j in i.attrs:
				if j.startswith("on") and payload in i.attrs[j]:
					return True
		return False

	def test_single_payload(self, url, location, payload):
		# url encode
		url1 = url.replace("sEc0307", urllib2.quote(payload))
		print "scan_xss_tag Url: %s" % url1

		(r, html, soup) = self.request_url(url1)

		if (location in ("betweenCommonTag", "betweenTitle", "betweenTextarea",
		                 "betweenXmp", "betweenIframe", "betweenNoscript", "betweenNoframes",
		                 "betweenPlaintext")
		        and soup.findAll("x0307x") and self.confirm_parent_tag(soup)):
			self.result.append("%s|%s|%s" % (location, payload, url1))

		if (location == "betweenScript" and (soup.findAll("x0307x") or
					soup.findAll(name="script",
				                text=re.compile(r"[^\\]%s" % payload.replace("(", "\(").replace(")", "\)"))))):
			self.result.append("%s|%s|%s" % (location, payload, url1))

		if (location == "betweenScript" and self.enc == "gbk"
		        and soup.findAll(name="script",
		                         text=re.compile(r"\\%s" % payload.replace("(", "\(").replace(")", "\)")))):
			self.result.append("[GBK]%s|%s|%s" % (location, payload, url1))

		if (location == "betweenStyle" and (soup.findAll("x0307x")
		                                    or soup.findAll(name="style",
		                                                    text=re.compile("%s" % payload.replace(".", "\.").replace(
			                                                    "(", "\(").replace(")", "\)"))))):
			self.result.append("%s|%s|%s" % (location, payload, url1))

		if (location == "inMetaRefresh" and soup.findAll(name="meta", attrs={"http-equiv": "Refresh",
		                                                                     "content": re.compile(payload)})):
			self.result.append("%s|%s|%s" % (location, payload, url1))

		if location == "utf-7" and html.startswith("+/v8 +ADw-x0307x+AD4-"):
			self.result.append("%s|%s|%s" % (location, payload, url1))

		if (location == "inCommonAttr" and (soup.findAll("x0307x")
		                                    or soup.findAll(attrs={"x0307x": re.compile("x0307x")}))):
			self.result.append("%s|%s|%s" % (location, payload, url1))

		if (location == "inSrcHrefAction" and (soup.findAll(attrs={"src": re.compile("^(%s)" % payload)})
		                                       or soup.findAll(attrs={"href": re.compile("^(%s)" % payload)})
		                                       or soup.findAll(attrs={"action": re.compile("^(%s)" % payload)}))):
			self.result.append("%s|%s|%s" % (location, payload, url1))

		if location == "inScript" and self.confirm_in_script(soup, payload):
			self.result.append("%s|%s|%s" % (location, payload, url1))

		if (location == "inStyle" and soup.findAll(attrs={
				    "style": re.compile("%s" % payload.replace(".", "\.").replace("(", "\(").replace(")", "\)"))})):
			self.result.append("%s|%s|%s" % (location, payload, url1))

	def test_xss(self, url, location):
		threads = []
		for i in self.payloads[location]:
			threads.append(Thread(self.test_single_payload, (url, location, i)))
		for i in threads:
			i.start()
		for i in threads:
			i.join()

	def run(self):
		self.find_paras()
		self.judge_charset()

		threads = [Thread(self.judge_location, (i,)) for i in self.urls]
		for i in threads:
			i.start()
		for i in threads:
			i.join()

		for i in self.testUrls:
			print i
			if self.testUrls[i]:
				print self.testUrls[i]
				self.testUrls[i] = list(set(self.testUrls[i]))

		threads = [Thread(self.test_xss, (j, i)) for i in self.testUrls for j in self.testUrls[i]]
		for i in threads:
			i.start()
		for i in threads:
			i.join()

		# Todo
		for i in self.result:
			print "FFFFound Xss_tag: %s" % i
			(location, payload, url) = i.split('|')
			XSSRecords.insert(url=url, injection=url, method='xss_tag', special=location, browsers=payload).execute()


def main():
	if len(sys.argv) == 3:
		url = sys.argv[1]
		cookies = {}
		cookies_text = sys.argv[2].split("; ")
		for i in cookies_text:
			cookies[i.split("=")[0]] = i.split("=")[1]

		print cookies
		s = XssScanTag(url, cookies)
		s.run()


if __name__ == '__main__':
	main()
