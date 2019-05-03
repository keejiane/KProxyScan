#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Author: Kw0ng

from functools import wraps
from flask import request, render_template
import re


def check_whitelist(string):
	status = False

	reg_poc = r'^([a-zA-Z0-9]|\.|\-|\_)+$'
	if len(string):
		if not re.match(reg_poc, string, re.I | re.M):
			print "check_whitelist, found dangerous characters: %s" % string
			status = True

	return status


def check_sqli(string):
	status = False
	reg_poc = r"('|\"|=|>|<|%|\(|\))"
	if re.search(reg_poc, string, re.I | re.M):
		status = True

	return status


def check_xss(string):
	status = False
	reg_poc = r"('|\"|=|>|<|%)"
	if re.search(reg_poc, string, re.I | re.M):
		status = True

	return status


def resp_warning():
	return render_template('warning.html')


def check_sec(dict_req):
	status = False

	if len(dict_req):
		for k, v in dict_req.items():
			if check_whitelist(v):
				status = True
				break

	return status


def check_sec_blacklist(dict_req):
	status = False

	if len(dict_req):
		for k, v in dict_req.items():
			if check_sqli(v) or check_xss(v):
				status = True
				break

	return status


def check_request(f):
	@wraps(f)
	def decorated(*args, **kwargs):
		dict_req_form = request.form
		dict_req_args = request.args

		if check_sec(dict_req_form) or check_sec(dict_req_args):
			return resp_warning()

		return f(*args, **kwargs)

	return decorated


def check_request_blacklist(f):
	@wraps(f)
	def decorated(*args, **kwargs):
		dict_req_form = request.form
		dict_req_args = request.args

		if check_sec_blacklist(dict_req_form) or check_sec_blacklist(dict_req_args):
			return resp_warning()

		return f(*args, **kwargs)

	return decorated
