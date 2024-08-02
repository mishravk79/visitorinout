#!/usr/bin/python3.10
import sys
import logging
logging.basicConfig(stream=sys.stderr)
sys.path.insert(0, "/opt/visitor")

from app import app as application
application.secret_key = 'your_secret_key'
