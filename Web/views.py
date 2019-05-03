#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Author: Kw0ng

from flask import render_template, redirect, request, current_app, url_for
from flask_paginate import Pagination, get_page_args
from middleware import *
from lib import *
from sqlalchemy.sql import text
from models import *
from . import app
import flask_login
import re

users = app.config['USERS']

login_manager = flask_login.LoginManager()
login_manager.init_app(app)
login_manager.session_protection = "basic"


class User(flask_login.UserMixin):
	pass


@login_manager.user_loader
def user_loader(email):
	if email not in users:
		return

	user = User()
	user.id = email
	return user


@login_manager.request_loader
def request_loader(request):
	email = request.form.get('email')
	if email not in users:
		return

	user = User()
	user.id = email

	if request.form.get['pw'] == users[email]['pw']:
		return user

	return


@app.route('/login', methods=['GET', 'POST'])
@check_request_blacklist
def login():
	if request.method == 'GET':
		return render_template('login.html')

	email = request.form['email']
	if email not in users.keys():
		return render_template('login.html', password_is_wrong=True)

	if request.form['pw'] == users[email]['pw']:
		user = User()
		user.id = email
		flask_login.login_user(user)
		return render_template('index.html', login_is_true=True)
	return render_template('login.html', password_is_wrong=True)


@app.route('/protected')
@flask_login.login_required
def protected():
	return 'Logged in as:%s' % flask_login.current_user.id


@app.route('/logout')
def logout():
	flask_login.logout_user()
	return render_template('login.html', logou_is_true=True)


@login_manager.unauthorized_handler
def unauthorized_handler():
	return render_template('index.html', login_is_true=False)


@app.route('/', methods=['GET', 'POST'])
@flask_login.login_required
def index():
	return render_template('index.html')


@app.route('/xsserTrend/', defaults={'n': 1})
@app.route('/xsserTrend', defaults={'n': 1})
@app.route('/xsserTrend/n/<int:n>/')
@app.route('/xsserTrend/n/<int:n>')
@check_request
@flask_login.login_required
def xsserTrend(n):
	day = date_day(n)

	xss_method = "SELECT method, count(*) AS c FROM xssrecords WHERE ctime>='%s' GROUP BY method LIMIT 10" % day
	xss_special = "SELECT special, count(*) AS c FROM xssrecords WHERE ctime>='%s' GROUP BY special LIMIT 10" % day
	xss_url = "SELECT substring_index(url, '/', 3) AS s, count(*) AS c FROM xssrecords WHERE ctime>='%s' GROUP BY s \
	ORDER BY c LIMIT 20" % day

	data_method = db.engine.execute(xss_method)
	data_special = db.engine.execute(xss_special)
	data_url = db.engine.execute(xss_url)

	data_method_dict = dbproxy2dict(data_method)
	data_special_dict = dbproxy2dict(data_special)
	data_url_dict = dbproxy2dict(data_url)

	active_url = '/xsserTrend/n/%s' % n

	return render_template('xsserTrend.html',
	                       mathod_data=data_method_dict,
	                       special_data=data_special_dict,
	                       url_data=data_url_dict,
	                       active_url=active_url)


@app.route('/sqlmapTrend/', defaults={'n': 1})
@app.route('/sqlmapTrend', defaults={'n': 1})
@app.route('/sqlmapTrend/n/<int:n>/')
@app.route('/sqlmapTrend/n/<int:n>')
@check_request
@flask_login.login_required
def sqlmapTrend(n):
	day = date_day(n)

	sql_title = "SELECT title, count(*) AS c FROM sqlirecords WHERE ctime>='%s' GROUP BY title LIMIT 10" % day
	sql_matchRatio = "SELECT matchRatio, count(*) AS c FROM sqlirecords WHERE ctime>='%s' GROUP BY matchRatio LIMIT 10" % day
	sql_url = "SELECT substring_index(url, '/', 3) AS s, count(*) AS c FROM sqlirecords WHERE ctime>='%s' GROUP BY s \
	ORDER BY c LIMIT 20" % day

	data_title = db.engine.execute(sql_title)
	data_matchRatio = db.engine.execute(sql_matchRatio)
	data_url = db.engine.execute(sql_url)

	data_title_dict = dbproxy2dict(data_title)
	data_matchRatio_dict = dbproxy2dict(data_matchRatio)
	data_url_dict = dbproxy2dict(data_url)

	active_url = '/sqlmapTrend/n/%s' % n

	return render_template('sqlmapTrend.html',
	                       title_data=data_title_dict,
	                       matchRatio_data=data_matchRatio_dict,
	                       url_data=data_url_dict,
	                       active_url=active_url)


@app.route('/alertTrend/', defaults={'n': 1})
@app.route('/alertTrend', defaults={'n': 1})
@app.route('/alertTrend/n/<int:n>/')
@app.route('/alertTrend/n/<int:n>')
@check_request
@flask_login.login_required
def alertTrend(n):
	day = date_day(n)

	sql_mix_count = "SELECT 'xss', count(*) AS c FROM xssrecords WHERE ctime>='%s' UNION SELECT 'sqli', count(*) AS c FROM \
		sqlirecords WHERE ctime >= '%s'" % (day, day)
	sql_mix_url = "SELECT substring_index(url,'/', 3) AS s, count(*) AS c FROM xssrecords WHERE ctime>='%s' UNION SELECT \
		substring_index(url,'/', 3) AS s, count(*) AS c  FROM sqlirecords WHERE ctime>='%s' GROUP BY s ORDER BY c LIMIT 20" \
	    % (day, day)

	data_mix_count = db.engine.execute(sql_mix_count)
	data_mix_url = db.engine.execute(sql_mix_url)

	data_count_dict = dbproxy2dict(data_mix_count)
	data_url_dict = dbproxy2dict(data_mix_url)

	active_url = '/alertTrend/n/%s' % n

	return render_template('alertTrend.html',
	                       mix_count_data=data_count_dict,
	                       mix_url_data=data_url_dict,
	                       active_url=active_url)


@app.route('/xsser/search', methods=['GET', 'POST'])
@check_request
@flask_login.login_required
def xsser_search():
	page, per_page, offset = get_page_args()

	xss_table = 'xssrecords'
	xss_cmd = "SELECT * FROM %s WHERE 1=1" % xss_table
	xss_cmd_total = "SELECT * FROM %s WHERE 1=1" % xss_table

	for key in ('url', 'special', 'method', 'ctime'):
		key_v = request.args.get(key, False)

		if key_v:
			if key.find('time') == -1:
				xss_cmd = "%s AND %s LIKE \"%%%%%s%%%%\"" % (xss_cmd, key, key_v)
				xss_cmd_total = "%s AND %s LIKE \"%%%%%s%%%%\"" % (xss_cmd_total, key, key_v)

			else:
				xss_cmd = "%s AND %s > \"%s\"" % (xss_cmd, key, key_v)
				xss_cmd_total = "%s AND %s > \"%s\"" % (xss_cmd_total, key, key_v)

			xss_cmd = "%s ORDER BY ctime DESC LIMIT %s, %s" % (xss_cmd, offset, per_page)
		print "xss_cmd: %s" % xss_cmd

		datas_proxy = db.engine.execute(xss_cmd)
		datas_proxy_total = db.engine.execute(xss_cmd_total)
		total = datas_proxy_total.rowcount

		print "page: %s per_page: %s offset: %s total: %s" % (page, per_page, offset, total)

		datas = dbproxy2tuple(datas_proxy)

	pagination = get_pagination(page=page,
	                            per_page=per_page,
	                            total=total,
	                            record_name='datas',
	                            format_total=True,
	                            format_number=True)

	return render_template('xsser.html', xssers=datas,
	                       page=page,
	                       per_page=per_page,
	                       pagination=pagination,
	                       active_url='users-page-url')


@app.route('/sqlmap/search', methods=['GET', 'POST'])
@check_request
@flask_login.login_required
def sqlmap_search():
	page, per_page, offset = get_page_args()

	sql_table = 'sqlirecords'
	sql_cmd = "SELECT * FROM %s WHERE 1=1" % sql_table
	sql_cmd_total = "SELECT * FROM %s WHERE 1=1" % sql_table

	for key in ('url', 'title', 'matchRatio', 'ctime'):
		key_v = request.args.get(key, False)

		if key_v:
			# if key.find('time') == -1:
			if not re.search(r'(time|match)', key, re.I):
				sql_cmd = "%s AND %s LIKE \"%%%%%s%%%%\"" % (sql_cmd, key, key_v)
				sql_cmd_total = "%s AND %s LIKE \"%%%%%s%%%%\"" % (sql_cmd_total, key, key_v)

			else:
				sql_cmd = "%s AND %s > \"%s\"" % (sql_cmd, key, key_v)
				sql_cmd_total = "%s AND %s > \"%s\"" % (sql_cmd_total, key, key_v)

	sql_cmd = "%s ORDER BY ctime DESC LIMIT %s, %s" % (sql_cmd, offset, per_page)
	print "sql_cmd: %s" % sql_cmd

	datas_proxy = db.engine.execute(sql_cmd)
	datas_proxy_total = db.engine.execute(sql_cmd_total)
	total = datas_proxy_total.rowcount

	print "page: %s per_page: %s offset: %s total: %s" % (page, per_page, offset, total)

	datas = dbproxy2tuple(datas_proxy)

	pagination = get_pagination(page=page,
	                            per_page=per_page,
	                            total=total,
	                            record_name='datas',
	                            format_total=True,
	                            format_number=True)

	return render_template('sqlmap.html', sqlmaps=datas,
	                       page=page,
	                       per_page=per_page,
	                       pagination=pagination,
	                       active_url='users-page-url')


def get_css_framework():
	return current_app.config.get('CSS_FRAMEWORK', 'bootstrap3')


def get_link_size():
	return current_app.config.get('LINK_SIZE', 'sm')


def show_single_page_or_not():
	return current_app.config.get('SHOW_SINGLE_PAGE', False)


def get_pagination(**kwargs):
	kwargs.setdefault('record_name', 'records')
	return Pagination(css_framework=get_css_framework(),
	                  link_size=get_link_size(),
	                  show_single_page=show_single_page_or_not(),
	                  **kwargs)
