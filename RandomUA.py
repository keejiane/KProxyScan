#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Author: Kw0ng

import random
from config import user_agent


class RandomUA(object):
	def __init__(self):
		i = random.randint(0, len(user_agent))
		lst_user_agent = []
		for k, v in user_agent.items():
			lst_user_agent.append(v)

		self.ua = lst_user_agent[i-1]


if __name__ == "__main__":
	rua = RandomUA()
	print rua.ua
