 
import sys
sys.path.append("/priv-libs/libs")


from pprint import pprint
import traceback
import pymongo 


def get_config(f_name):
   with open(f_name) as f:
      print("Loading data from {}...".format(f_name))
      data = yaml.load(f, Loader=yaml.FullLoader)
      return data

def create_index(col, name):
   col.create_index(name)

def get_collection(uri, db_name="priv_backend", col_name="enc_data", connect=False):
   myclient = pymongo.MongoClient(uri,connect=connect)
   mydb = myclient[db_name]
   mycol = mydb[col_name]
   return mycol