#! /usr/bin/env python

####################
### DGF 9/5/2013 ###
####################

#########################
### import dei moduli ###
#########################

import os
import re
import datetime
from datetime import date, timedelta, datetime
import logging
import time
from time import localtime
import tempfile
import sys
import ConfigParser
import shutil
import xml.etree.ElementTree as ET


#########################################
### dichiarazioni costanti simboliche ###
#########################################

PATH_HOME = "/opt/PIPPO"
PATH_LOG = PATH_HOME+"/Log"
PATH_CONFIG = PATH_HOME+"/Conf"
CONFIG_FILE = PATH_CONFIG+"/Config.cfg"

### definition of logger for manage the script log ###

SYSTEM_DATE=time.strftime("%Y%m%d")
LOG_FILENAME = PATH_LOG+"/pippo-"+SYSTEM_DATE+".log"
logger = logging.getLogger("pippo.py")
hdlr = logging.FileHandler(LOG_FILENAME)
FORMAT = logging.Formatter('%(asctime)s - [%(levelname)s] %(message)s')
hdlr.setFormatter(FORMAT)
logger.addHandler(hdlr)
logger.setLevel(logging.DEBUG)

### definition of parser for read the configuration file ###

parser = ConfigParser.ConfigParser()
parser.read(CONFIG_FILE)

############################
### definizione funzioni ###
############################

def ControlConfigFile():
    try:
        f = open(CONFIG_FILE,'r')
        logger.info("verification of a configuration file ok")
        f.close()
    except IOError:
        logger.error("configuration file not present. exit!")
        sys.exit()


def FindFile():
    ### read of configuration file ###
    for name_section in parser.sections():
        GetFile(parser.get(name_section,'path_timeline'))


def GetFile(path_tml):
    ### the yesterday date in format yyyymmdd ###
    d = datetime.now() - timedelta(days=1)
    delta = d.timetuple()[0:3]

    ### the today date in format yyyymmdd ###
    day = datetime.now()
    day_1 = day.timetuple()[0:3]

    ### creation of directory where to put the file of a day before ###
    dir = "Timeline_ITT_"+d.strftime("%Y-%m-%d%Z")

    ### creation of repository directory ###
    try:
        os.stat(PATH_HOME+"/"+dir)
    except:
        os.mkdir(PATH_HOME+"/"+dir)

    BuiltFileXmlInfo(dir)

    ### take all the files that end with the suffix xml ###
    for path, subdirs, files in os.walk(path_tml):
        for filename in [ f for f in files if re.search('.xml$', f, re.I)]:

           ### take the modification time from the xml file in the format yyyymmdd ###
           mtime_file = os.path.getmtime(os.path.join(path,filename))
           filetime = localtime(mtime_file)[0:3]
           #print(path+" "+str(filetime)+"/"+str(filetime))
           #print(d.strftime("%Y-%m-%d %Z"))

           ### comparing the date of the file you are searching with yesterday's date and copy it in a directory ###
           if filetime == delta:
               print(os.path.join(path,filename))

               ### I copy the files to the date found in the dir to be sent to a server ###
               ### If there is nothing in the file to proceed with the backup copy ###

               if not os.path.isfile(os.path.join(PATH_HOME+"/"+dir,filename)):

                   ### verify that the copy it's ok ###
                   try:
                       shutil.copy(os.path.join(path,filename),PATH_HOME+"/"+dir)
                   except:
                       ### it's not ok exit ###
                       logger.error("File "+filename+" not copy, exit")
                       sys.exit()
               else:
                   logger.info("File : "+filename+" exists in the dir for the server")

def BuiltFileXmlInfo(dir):

    ### buld the file xml in the INFO section ###

    root = ET.Element("root")
    tree = ET.ElementTree(root)

    info = ET.SubElement(root, "INFO")

    field1 = ET.SubElement(info, "LOAD_DOCUMENTPATH")
    field1.text = dir

    field2 = ET.SubElement(info, "CUSTOMER_ID")
    field2.text = "14"

    field3 = ET.SubElement(info, "PIVA_COD_FISC")
    field3.text = ''

    field4 = ET.SubElement(info, "MAP_ID")
    field4.text = "3"

    field5 = ET.SubElement(info, "COURIER_NAME")
    field5.text = dir

    field6 = ET.SubElement(info, "SIGN_SINGLEDOC")
    field6.text = "N"

    field6 = ET.SubElement(info, "HASH_TYPE")
    field6.set("CODE", "BASE64")
    field6.text = "SHA256"

    tree.write(PATH_HOME+"/default_1.xml")


def BuildFileXml():
    filetree = ET.parse(PATH_HOME+"/default_1.xml")
    rootfile = filetree.getroot()

    documents = ET.SubElement(rootfile, "DOCUMENTS")
    documents.set("FAMILY", "36")

    index_file = ET.SubElement(documents, "INDEX_FIELDS")

    field = ET.SubElement(index_file, "FIELD")
    field.set("NAME", "NOME_FILE")
    #field.append("DDD")

    #rootfile.append(field)

    filetree.write(PATH_HOME+"/default_1.xml")

############
### main ###
############

if __name__ == "__main__":
    ControlConfigFile()
    FindFile()
    BuildFileXml()
