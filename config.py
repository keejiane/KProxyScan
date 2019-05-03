#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Author: Kw0ng

# MITMProxy config
mitm_config = {
	'host': '192.168.0.115',
	'port': 8111
}

# sqlmapapi server config
sqlmap_api = 'http://127.0.0.1:8775'

# Mysql database config
mysql_db = {
	'host': '127.0.0.1',
	'user': 'root',
	'password': '',
	'db_name': 'kw0ngScan',
	'port': 3306,
	'charset': 'utf8'
}

# Mongodb config
mongo_db = {
	'host': '127.0.0.1',
	'port': 27017
}

# Redis config
redis_broker = {
	"sqli_url": "redis://127.0.0.1:6379/0",
	"sqli_burl": "redis://127.0.0.1:6379/1",
	"xss_url": "redis://127.0.0.1:6379/2",
	"xss_burl": "redis://127.0.0.1:6379/3",
	"xss_dom_url": "redis://127.0.0.1:6379/4",
	"xss_dom_burl": "redis://127.0.0.1:6379/5",
	"redirect_url": "redis://127.0.0.1:6379/6",
	"redirect_burl": "redis://127.0.0.1:6379/7"
}

# enable plugin or not
scan_plugin_status = {
	'sqli_plugin': True,
	'xss_plugin': True,
	'xss_dom_plugin': True,
	'redirect_plugin': True
}

user_agent = {
	"IE 11.0.9600.18376": "Mozilla/5.0 (Windows NT 6.1; WOW64; Trident/7.0; rv:11.0) like Gecko",
	"Chrome 51.0.2704.103 m": "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/51.0.2704.103 Safari/537.36",
	"Firefox 40.0.3": "Mozilla/5.0 (Windows NT 6.1; WOW64; rv:40.0) Gecko/20100101 Firefox/40.0",
	"Opera 38.0.2220.41": "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/51.0.2704.106 Safari/537.36 OPR/38.0.2220.41",
	"Chrome 51.0.2704.106 m": "Mozilla/5.0 (Windows NT 6.1; WOW64; rv:39.0) Gecko/20100101 Firefox/39.0",
	"IE8.0.7600.16385": "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/51.0.2704.106 Safari/537.36",
	"Firefox 39.0": "Mozilla/4.0 (compatible; MSIE 8.0; Windows NT 6.1; WOW64; Trident/4.0; GTB7.5; SLCC2; .NET CLR 2.0.50727; .NET CLR 3.5.30729; .NET CLR 3.0.30729; Media Center PC 6.0;"
	}