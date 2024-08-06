# Copyright (c) 2024 Vinod Kumar Mishra
# This file is part of Visitorinout.
# Visitorinout is released under the MIT License.
# See the License file for more details.

#!/usr/bin/python3.10
import sys
import logging
logging.basicConfig(stream=sys.stderr)
sys.path.insert(0, "/opt/visitorinout")

from app import app as application
application.secret_key = 'your_secret_key'
