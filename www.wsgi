import sys
import os

try:
    from server import app as application
except KeyError as e:
    print e
