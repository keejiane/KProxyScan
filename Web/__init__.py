#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Author: Kw0ng

from flask import Flask
from flask_bootstrap import Bootstrap
from flask_nav import Nav
from flask_sqlalchemy import SQLAlchemy
from flask_nav.elements import Navbar, View, Subgroup, Link, Text, Separator

app = Flask(__name__)
nav = Nav()
Bootstrap(app)
nav.init_app(app)

app.jinja_env.add_extension("chartkick.ext.charts")
app.config.from_object('config')
app.config.setdefault('SQLALCHEMY_TRACK_MODIFICATIONS', True)

db = SQLAlchemy(app)

nav.register_element('frontend_top', Navbar(
	View('KScan', '.index'),
	View('Dashboard', '.alertTrend'),
	Subgroup(
		'XSSer',
		View('XSSerTrend', '.xsserTrend'),
		Separator(),
		View('XSSer', '.xsser_search'),
	),

	Subgroup(
		'Sqlmap',
		View('SqlmapTrend', '.sqlmapTrend'),
		Separator(),
		View('Sqlmap', 'sqlmap_search'),
	),

	# Subgroup(
	# 	'Others',
	# 	View('UrlRedirect', '.redirect_search'),
	# 	Separator(),
	# 	View('CSRF', '.csrf_search'),
	# ),

	Text('About'),
	Text(''),
	View('Login', '.login'),
	View('Logout', '.logout'),
))

from . import views
