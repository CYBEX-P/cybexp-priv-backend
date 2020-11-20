#!/usr/bin/env python3

import sys
sys.path.append("/priv-libs/libs")


from pprint import pprint
import traceback
import pymongo 
import pickle 

from flask import render_template
from flask import Response, request
from flask import send_file

from common import get_collection
from cpabew import CPABEAlg
from cpabe_key_gen import gen_cpabe_master_keys, gen_cpabe_org_secret_key, load_cpabe_org_secret_key_from_name, load_cpabe_master_keys
from de import RSADOAEP, rsa_key
from ore_key_gen import gen_ore_key_rand

ORE_key_location = "/secrets/ORE_key.bin"
backed_DB_uri = "mongodb://priv-backend-db:27017/"



def normalize_str(st):
   st = st.replace("/","__")
   st = st.replace(" ","_")
   return st

def normalize_attribs(attribs):
   return list(map(normalize_str, attribs))


def index():
   # return Response(status=403)
   return "up", 200


def add_enc_data():
   global backed_DB_uri
   raw_req_data = request.data
   # todo create index
   try:
      data = pickle.loads(raw_req_data)
      indexes = data["index"]
      if type(data) == dict and type(indexes) == list and len(indexes) > 0:
         db = get_collection(backed_DB_uri)
         db.insert_one(data)
         return Response(status=201)
      else:
         return Response(status=400)
   except:
      traceback.print_exc()
      return Response(status=400)


def query():
   return "not implemented", 200
   # how to query
   # https://stackoverflow.com/a/61274914/12044480