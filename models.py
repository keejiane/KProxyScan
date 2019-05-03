#!/usr/bin/env python
# -*- coding: utf-8 -*-
# author: kw0ng


from config import *
from peewee import *

db = MySQLDatabase(host=mysql_db['host'], user=mysql_db['user'],
					passwd=mysql_db['password'], port=mysql_db['port'],
					database=mysql_db['db_name'], charset=mysql_db['charset'])


class BaseModel(Model):
	class Meta:
		database = db


class SQLIRecords(BaseModel):
	url = TextField()
	num = CharField(max_length=255, default=None)
	dbms = CharField(max_length=255, default=None)
	dbms_version = CharField(max_length=255, default=None)
	matchRatio = FloatField(default=None)
	payload = TextField()
	title = CharField(max_length=255, default=None)
	vector = CharField(max_length=255, default=None)
	request_text = TextField()
	ctime = TimestampField(null=False, constraints=[SQL('DEFAULT CURRENT_TIMESTAMP')])


class XSSRecords(BaseModel):
	url = TextField()
	target = CharField(max_length=255, default=None)
	injection = CharField(max_length=255, default=None)
	method = CharField(max_length=255, default=None)
	special = CharField(max_length=255, default=None)
	browsers = CharField(max_length=255, default=None)
	final_attack = CharField(max_length=255, default=None)
	ctime = TimestampField(null=False, constraints=[SQL('DEFAULT CURRENT_TIMESTAMP')])


class Redirect(BaseModel):
	url = TextField()
	payload = TextField()
	method = CharField(max_length=255, default=None)
	stime = TimestampField(null=False, constraints=[SQL('DEFAULT CURRENT_TIMESTAMP')])


def create_tables():
	db.create_tables([SQLIRecords, XSSRecords], safe=True)
	print 'Create tables succeed!!!'

if __name__ == '__main__':
	create_tables()
