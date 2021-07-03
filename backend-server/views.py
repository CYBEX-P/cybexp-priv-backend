#!/usr/bin/env python3

import sys
sys.path.append("/priv-libs/libs")
from priv_common import load_yaml_file
from db_common import get_collection

from pprint import pprint
import traceback
import pymongo 
import pickle 

from flask import render_template
from flask import Response, request
from flask import send_file

# from cpabew import CPABEAlg
# from cpabe_key_gen import gen_cpabe_master_keys, gen_cpabe_org_secret_key, load_cpabe_org_secret_key_from_name, load_cpabe_master_keys
# from de import RSADOAEP, rsa_key
# from ore_key_gen import gen_ore_key_rand
from ORE import *

conf =load_yaml_file("/config.yaml")
# ORE_key_location = conf["ORE_key_location"]
backed_DB_uri = conf["backed_DB_uri"]
db_name = conf["db_name"]
col_name = conf["col_name"]
DEBUG = conf["debug"]
PRINT_PRE_FILTERED = conf["print_pre_time_filtered_data"]
PRINT_FILTERED = conf["print_time_filtered_data"]
PRINT_RESPONSE = conf["print_response"]

# kms_access_key = conf["kms_access_key"]



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
   global backed_DB_uri, db_name, col_name
   raw_req_data = request.data
   try:
      data = pickle.loads(raw_req_data)
      indexes = data["index"]
      if type(data) == dict and type(indexes) == list and len(indexes) > 0:
         db = get_collection(backed_DB_uri,db_name=db_name, col_name=col_name)
         db.insert_one(data)
         return Response(status=201)
      else:
         return Response(status=400)
   except:
      traceback.print_exc()
      return Response(status=400)



def _bigger_than(bin_dat, timestamp_bin):
   left = OREComparable(ORECiphertext.from_raw_bytes(bin_dat))
   right = OREComparable(ORECiphertext.from_raw_bytes(timestamp_bin))
   r = left > right
   # print("right:", r,flush=True)
   return r

def _smaller_than(bin_dat, timestamp_bin):
   left = OREComparable(ORECiphertext.from_raw_bytes(bin_dat))
   right = OREComparable(ORECiphertext.from_raw_bytes(timestamp_bin))
   r = left < right
   # print("left:", r,flush=True)
   return r


def _bigger_eq_than(bin_dat, timestamp_bin):
   left = OREComparable(ORECiphertext.from_raw_bytes(bin_dat))
   right = OREComparable(ORECiphertext.from_raw_bytes(timestamp_bin))
   r = left >= right
   # print("left=:", r,flush=True)
   return r
   
def _smaller_eq_than(bin_dat, timestamp_bin):
   left = OREComparable(ORECiphertext.from_raw_bytes(bin_dat))
   right = OREComparable(ORECiphertext.from_raw_bytes(timestamp_bin))
   r = left <= right
   # print("right=:", r,flush=True)
   return r



def time_filt_data(data, left_t, right_t, l_in, r_in):
   if not left_t and not right_t:
      # print("skiping time filtering ...",flush=True)
      return data
   # print("*"*20)
   # print(" Filtering ")
   # print("*"*20,flush=True)

   new_data = list()
   for d in data:
      if "timestamp" not in d:
         # print("skipping because timestamp missing",flush=True)
         # print(d.keys(),flush=True)
         continue

      timestamps = d["timestamp"]
      
      try:
         # filter left
         if left_t:
            if l_in:
               # print("left inclusive",flush=True)
               l_map = map(_bigger_eq_than,timestamps, [left_t] * len(timestamps))
            else:
               l_map = map(_bigger_than,timestamps, [left_t] * len(timestamps))
            # print(l_map,flush=True)
            if not any(l_map):
               continue

         # filter right
         if right_t:
            if r_in:
               r_map = map(_smaller_eq_than,timestamps, [right_t] * len(timestamps))
            else:
               r_map = map(_smaller_than,timestamps, [right_t] * len(timestamps))
            if not any(r_map):
               continue

         new_data.append(d)

      except: # no harm done, as it is encrypted, if decryptable user can self filter timestamp
         traceback.print_exc()
         sys.stdout.flush()
         new_data.append(d)

   return new_data


def query_data():
   global backed_DB_uri, db_name, col_name, DEBUG
   # DEBUG = True
   filt = {"_id":0}
   raw_req_data = request.data
   try:
      try:
         data = pickle.loads(raw_req_data)
      except:
         return "data must be a python pickled dictionary with the folowing keys: 'index':de_enc, [time_left]:ore_enc, [time_right]:ore_enc, [left_inclusive]:bool, [right_inclusive]:bool",400
      if type(data) == dict:
         try:
            index = data["index"]
            query_type = data["query_type"]

            if not (query_type=="search" or query_type=="count"):
               return "Query must be a python pickled dictionary containing 'index' and 'query_type', where 'index' is the encrypted query and 'query_type' is 'search' or 'count'",400
         except KeyError:
            return "Query must be a python pickled dictionary containing 'index' and 'query_type', where 'index' is the encrypted query and 'query_type' is 'search' or 'count'",400

         if DEBUG:
            print("query type:", query_type)
            print("index:", index)

         if type(index) != bytes:
            return Response(status=400)

         query = {"index": index}
         slow_count = False

         if "time_left" in data:
            l_time = data["time_left"]
            slow_count = True
         else:
            l_time = None
         if "time_right" in data:
            r_time = data["time_right"]
            slow_count = True
         else:
            r_time = None

         if "left_inclusive" in data:
            left_inclusive = data["left_inclusive"]
            slow_count = True
         else:
            left_inclusive = False
         if "right_inclusive" in data:
            right_inclusive = data["right_inclusive"]
            slow_count = True
         else:
            right_inclusive = False

         db = get_collection(backed_DB_uri,db_name=db_name, col_name=col_name)

         if query_type == "search" or slow_count:
            query_data = db.find(query, filt)
            # find() returns cursor, which is consumed after use
            # prevent from being consumed by casting into unmutable
            query_data = list(query_data)

            if PRINT_PRE_FILTERED:
               print("#"*50)
               pprint(list(query_data))
               print("#"*50,flush=True)

            filtered_data = time_filt_data(query_data, l_time, r_time, left_inclusive, right_inclusive)
            
            if PRINT_FILTERED:
               print("#"*20+" filted data "+"#"*15)
               pprint(filtered_data)
               print("#"*50,flush=True)

            if query_type == "count":
               resp = {"count": len(filtered_data)}
            else:
               resp = filtered_data

         elif query_type == "count" and not slow_count:
            # for time restrictions visit function here
            # https://pymongo.readthedocs.io/en/stable/api/pymongo/collection.html#pymongo.collection.Collection.count_documents
            resp_count = db.count_documents(query)
            resp = {"count": resp_count}

         else: # should never get here
            return Response(status=400) 


         if PRINT_RESPONSE:
            print("resp:",resp, flush=True)


         return pickle.dumps(resp), 200
         # return Response(status=201)
      else:
         return Response(status=400)
   except:
      traceback.print_exc()
      return Response(status=500)
   # how to query
   # https://stackoverflow.com/a/61274914/12044480

