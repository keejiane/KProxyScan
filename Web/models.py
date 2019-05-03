#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Author: Kw0ng


from datetime import datetime
from Web import db


class Xsser(db.Model):
	__tablename__ = 'xsser'
	__table_args__ = {"useexisting": True}
	id = db.Column(db.Integer, primary_key=True)
	url = db.Column(db.String(1024), nullable=True)
	target = db.Column(db.String(255), nullable=True)
	injection = db.Column(db.String(255), nullable=True)
	method = db.Column(db.String(255), nullable=True)
	special = db.Column(db.String(255), nullable=True)
	browsers = db.Column(db.String(255), nullable=True)
	final_attack = db.Column(db.String(1024), nullable=True)
	ctime = db.Column(db.DateTime, default=datetime.now())


class Sqlmap(db.Model):
	__tablename__ = 'sqlmap'
	__table_args__ = {"useexisting": True}
	id = db.Column(db.Integer, primary_key=True)
	url = db.Column(db.String(1024), nullable=True)
	num = db.Column(db.String(255), nullable=True)
	dbms = db.Column(db.String(255), nullable=True)
	dbms_version = db.Column(db.String(255), nullable=True)
	matchRatio = db.Column(db.Float, nullable=True)
	payload = db.Column(db.String(2048), nullable=True)
	title = db.Column(db.String(255), nullable=True)
	vector = db.Column(db.String(255), nullable=True)
	request_text = db.Column(db.String(1024), nullable=True)
	ctime = db.Column(db.DateTime, default=datetime.now())


class Redirect(db.Model):
	__tablename__ = 'redirect'
	__table_args__ = {"useexisting": True}
	id = db.Column(db.Integer, primary_key=True)
	url = db.Column(db.String(1024), nullable=True)
	payload = db.Column(db.String(1024), nullable=True)
	method = db.Column(db.String(255), nullable=True)
	ctime = db.Column(db.DateTime, default=datetime.now())

