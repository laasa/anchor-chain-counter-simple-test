 # software includes geomag.py
# by Christopher Weiss cmweiss@gmail.com
# https://github.com/cmweiss/geomag
# Infos on NMEA0183 from:
      # https://github.com/mak08/VRDashboard/issues/31
      # https://www.nmea.org/Assets/100108_nmea_0183_sentences_not_recommended_for_new_designs.pdf
      # http://www.plaisance-pratique.com/IMG/pdf/NMEA0183-2.pdf

from avnav_nmea import NMEAParser
import math
import time
import os
from datetime import date
import sys

class Config(object):

  def __init__(self, api):
    pass


class Plugin(object):
  PATHANCC = "gps.anchorChainValue"
  OWNID = 'IN'
  outFilter = []
 
  #FILTER = ['$AA']
  FILTER = []
  CONFIG = [
      {
      'name': 'sourceName',
      'description': 'source name to be set for the generated records (defaults to anchor_chain_counter)',
      'default': 'anchor_chain_counter'
      },
      ]

  @classmethod
  def pluginInfo(cls):
    """
    the description for the module
    @return: a dict with the content described below
            parts:
               * description (mandatory)
               * data: list of keys to be stored (optional)
                 * path - the key - see AVNApi.addData, all pathes starting with "gps." will be sent to the GUI
                 * description
    """
    return {
      'description': 'a plugin that calculates true wind data, magnetic deviation at the current position, speed through water and magnetic and true heading',
      'version': '1.0',
      'config': cls.CONFIG,
      'data': [
        {
          'path': cls.PATHANCC,
          'description': 'anchor chain counter',
        },
      ]
    }

  def __init__(self, api):
    """
        initialize a plugins
        do any checks here and throw an exception on error
        do not yet start any threads!
        @param api: the api to communicate with avnav
        @type  api: AVNApi
    """
    self.api = api
    self.api.registerEditableParameters(self.CONFIG, self.changeParam)
    self.api.registerRestart(self.stop)
    self.oldtime = 0
    self.variation_time = 0
    self.variation_val = None

    self.userAppId = None
    self.startSequence = 0
    self.receivedTags = []
    self.WindData = []
    self.source=self.api.getConfigValue("sourceName",None)
    self.saveAllConfig()
    
  def stop(self):
    pass
  
  def getConfigValue(self, name):
    defaults = self.pluginInfo()['config']
    for cf in defaults:
      if cf['name'] == name:
        return self.api.getConfigValue(name, cf.get('default'))
    return self.api.getConfigValue(name)
  
  def saveAllConfig(self):
    d = {}
    defaults = self.pluginInfo()['config']
    for cf in defaults:
      v = self.getConfigValue(cf.get('name'))
      d.update({cf.get('name'):v})
    self.api.saveConfigValues(d)
    return 
  
  def changeConfig(self, newValues):
    self.api.saveConfigValues(newValues)
  
  def changeParam(self, param):
    self.api.saveConfigValues(param)
    self.startSequence += 1

  def run(self):
    """
    the run method
    @return:
    """
    startSequence = None
    seq = 0
    self.api.log("started")
    self.api.setStatus('STARTED', 'running')
    gm = None
    source='anchor_chain_counter'
    while not self.api.shouldStopMainThread():
      if startSequence != self.startSequence:
        self.outFilter = self.getConfigValue('FILTER_NMEA_OUT')
        if not (isinstance(self.outFilter, list)):
            self.outFilter = self.outFilter.split(',')
      lastTime = time.time()

      # fetch from queue till next compute period
      runNext = False
      while not runNext:
        now = time.time()
        if now < lastTime:
          # timeShift back
          runNext = True
          continue
        waitTime = 0.001
        runNext = True
        seq, data = self.api.fetchFromQueue(seq, number=100, waitTime=waitTime, includeSource=True,filter=self.FILTER)
        if len(data) > 0:
          for line in data:
            if not source in line.source : # KEINE Auswertung von selbst erzeugten Daten!!
                self.parseData(line.data, source=source)

  def make_sentence(self, title, *keys):
      s = '$' + self.OWNID + title
      for arg in keys:
          if(type(arg) == float or type(arg) == int):
              s = s + ',' + arg.__format__('06.2f')
          else:
              s = s + ',' + arg
      return(s)
  
  def nmeaChecksum(cls, part):
    chksum = 0
    if part[0] == "$" or part[0] == "!":
      part = part[1:]
    for s in part:
      chksum ^= ord(s)
    return ("%02X" % chksum)

  def parseData(self, data, source='internal'):
    valAndSum = data.rstrip().split("*")
    if len(valAndSum) > 1:
      sum = self.nmeaChecksum(valAndSum[0])
      if sum != valAndSum[1].upper():
        self.api.error("invalid checksum in %s, expected %s" % (data, sum))
        return
    darray = valAndSum[0].split(",")
    if len(darray) < 1 or (darray[0][0:1] != "$" and darray[0][0:1] != '!'):
      self.api.error("invalid nmea data (len<1) " + data + " - ignore")
      return False
    tag = darray[0][3:]
    rt = {}

    try:   
        
#ANC - Anchor Chain Counter

#        1   2 3
#        |   | |
# $AAANC,x.x,M*hh<CR><LF>

# Field Number: 
#  1) anchor chain counter
#  2) Meters
#  3) Checksum        
      if tag == 'ANC':
        rt['anchorChainValue'] = float(darray[1] or '0')
        self.api.addData(self.PATHANCC, rt['anchorChainValue'],source=source)
        return(True)
    
    except Exception:
      self.api.error(" error parsing nmea data " + str(data) + "\n")
    return False

