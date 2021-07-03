#!/usr/bin/env python3

import sys
sys.path.append("/priv-libs/libs")
from priv_common import load_yaml_file
import db_common


from pprint import pprint
import traceback


import views
from flask import Flask
# from web_client import get_ore_key, test_auth

# ref: split into files
#h ttps://stackoverflow.com/questions/11994325/how-to-divide-flask-app-into-multiple-py-files

conf =load_yaml_file("/config.yaml")
FLASK_DEBUG = conf["debug_mode_flask"]
DEBUG = conf["debug"]


backed_DB_uri = conf["backed_DB_uri"]
db_name = conf["db_name"]
col_name = conf["col_name"]


# # the fillowing code is no longer neede as backend should never get a key
# ORE_key_location = conf["ORE_key_location"]
# kms_url = conf["kms_url"]
# kms_access_key = conf["kms_access_key"]


# def load_fetch_ore_key():
#    global ORE_key_location, kms_url, basic_auth, kms_access_key

#    try:
#       k = open(ORE_key_location, "rb").read()
#       return
#    except FileNotFoundError:
#       try:
#          ore_key = get_ore_key(kms_url,kms_access_key, auth=basic_auth, debug=DEBUG)
#          if ore_key == None:
#             sys.exit("Could not fetch ORE key from KMS server({})".format(kms_url))

#       except:
#          if DEBUG:
#             traceback.print_exc()
#          sys.exit("Could not fetch ORE key from KMS server({})".format(kms_url))
#       open(ORE_key_location, "wb").write(ore_key)
#       return 
#    sys.exit("Could not load or fetch ORE key")

# basic_auth = None
# try:
#    basic_auth_user = conf["basic_auth"]["user"]
#    try:
#       basic_auth_pass = conf["basic_auth"]["pass"]
#       basic_auth = (basic_auth_user, basic_auth_pass)
#       print("Baic auth(as client): enabled")
#    except:
#       exit("Baic auth(as client): no password specified. Exiting.\n")
# except:
#    print("Baic auth(as client): disabled")
#    basic_auth = None


# if basic_auth != None:
#    if not test_auth(kms_url, basic_auth):
#       exit("Test failed: KMS basic auth(as client). quiting.")


app = Flask(__name__)

app.add_url_rule('/', methods=['GET'], view_func=views.index)

app.add_url_rule('/add/enc-data', methods=['POST'], view_func=views.add_enc_data)
app.add_url_rule('/query', methods=['POST'], view_func=views.query_data)


if __name__ == '__main__':
   # load_fetch_ore_key()
   col = db_common.get_collection(backed_DB_uri,db_name=db_name, col_name=col_name)
   db_common.create_index(col,"index")
   app.run(host="0.0.0.0", port=5000 , debug=FLASK_DEBUG, use_reloader=FLASK_DEBUG)