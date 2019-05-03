#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Author: Kw0ng


import datetime
import dateutil.relativedelta


def date_day(n=None):
	now = datetime.datetime.now()

	if n == 1:
		date = now - datetime.timedelta(hours=24)

	elif n == 3:
		date = now - datetime.timedelta(hours=72)

	elif n == 5:
		date = now - datetime.timedelta(weeks=1)

	elif n == 7:
		date = now + dateutil.relativedelta.relativedelta(months=-1)

	elif n == 0:
		date = now - datetime.timedelta(hours=1)
		return date

	else:
		# one year
		date = now - datetime.timedelta(weeks=36)

	return str(date)[:10]


def dbproxy2dict(dbproxy):
	datas = []

	for i in dbproxy:
		# datas.append(i)
		datas.append([str(i[0]), str(i[1])])

	return dict(datas)


def dbproxy2tuple(dbproxy):
	datas = []

	for i in dbproxy:
		datas.append(i)

	return tuple(datas)


if __name__ == "__main__":
	print date_day()
