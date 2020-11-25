#!/usr/bin/env python3

import sys
sys.path.append("/priv-libs/libs")


from pprint import pprint
import traceback

# ref: split into files
#h ttps://stackoverflow.com/questions/11994325/how-to-divide-flask-app-into-multiple-py-files

DEBUG = True
ORE_key_location = "/secrets/ORE_key.bin"
kms_url = "http://192.168.1.101:5002"
backed_DB_uri = "mongodb://priv-backend-db:27017/"

import views
import common
from flask import Flask
from web_client import get_ore_key

app = Flask(__name__)

app.add_url_rule('/', methods=['GET'], view_func=views.index)

app.add_url_rule('/add/enc-data', methods=['POST'], view_func=views.add_enc_data)
app.add_url_rule('/query', methods=['POST'], view_func=views.query_data)

def load_fetch_ore_key():
   global ORE_key_location, kms_url

   try:
      k = open(ORE_key_location, "rb").read()
      return
   except FileNotFoundError:
      try:
         ore_key = get_ore_key(kms_url)
         if ore_key == None:
            sys.exit("Could not fetch ORE key from KMS server({})".format(kms_url))

      except:
         sys.exit("Could not fetch ORE key from KMS server({})".format(kms_url))
      open(ORE_key_location, "wb").write(ore_key)
      return 
   sys.exit("Could not load or fetch ORE key")




if __name__ == '__main__':
   load_fetch_ore_key()
   col = common.get_collection(backed_DB_uri)
   common.create_index(col,"index")
   app.run(host="0.0.0.0", port=5000 , debug=DEBUG, use_reloader=DEBUG)