#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Jul 21 13:49:50 2017

@author: shayneufeld
"""

import os
from flask import Flask

app = Flask(__name__, static_folder = os.path.join(os.getcwd(),'static'))
from pricecamp_app import views