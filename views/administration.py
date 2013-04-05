import urllib2, urllib, json

import webapp2
from google.appengine.ext import deferred

from libs import facebook

import settings
from utils import BaseHandler
from models import *
from forms import *
from workers import *


class AdministrationIndexHandler(BaseHandler):

    def get(self):
        pass