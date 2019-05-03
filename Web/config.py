#!/usr/bin/env python
# -*- coding: utf-8 -*-
# author: kw0ng

PER_PAGE = 10
CSS_FRAMEWORK = 'bootstrap3'
LINK_SIZE = 'sm'

SECRET_KEY = '***'

SHOW_SINGLE_PAGE = False

db_host = "127.0.0.1"
db_port = 3306
db_name = "*****"
db_user = "root"
db_password = ""
SQLALCHEMY_DATABASE_URI = "mysql://%s:%s@%s:%d/%s" % (db_user, db_password, db_host, db_port, db_name)
SQLALCHEMY_ECHO = False
SQLALCHEMY_POOL_RECYCLE = 3600
USERS = {'*****': {'pw': '*****'}}
