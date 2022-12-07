#launch poin object (on add) for Object OPCDATA
#Created 08 07 2022
#Last Update 19 07 2022

from psdi.server import MXServer
from psdi.mbo import MboConstants
import psdi.security.UserInfo
from psdi.server import MXServer
import psdi.util.MXSession as MXSession

#Set OPC Data
newValue = mbo.getDouble("VALUE")
strNewValue = str(newValue)
date = mbo.getDate("DATETIME")
currentDate = MXServer.getMXServer().getDate()
site = mbo.getString("SITEID")
org = mbo.getString("ORGID")

#Set OPC Tag
opcTagSet = mbo.getMboSet("OPCTAG")
opcTag = opcTagSet.getMbo(0)
assetnum = opcTag.getString("ASSETNUM")
meterName = opcTag.getString("METERNAME")

#Set Asset Meter Data 
assetMeterSet = opcTag.getMboSet("ASSETMETER")
assetMeter = assetMeterSet.getMbo(0)

if assetMeter is not None:
    #Set Meter Type
    meterSet = assetMeter.getMboSet("METER")
    meter = meterSet.getMbo(0)
    meterType = meter.getString("METERTYPE")

    #set asset data
    assetSet = assetMeter.getMboSet("ASSET")
    asset = assetSet.getMbo(0)
    asid = asset.getInt("ASSETID")
    assetnum = asset.getString("ASSETNUM")
    #Set Delta
    lastRead = assetMeter.getDouble("LASTREADING")
    lastVal = int(lastRead)
    delta = newValue - lastVal
    #Update ASSET METER 
    assetMeter.setValue("LASTREADING",strNewValue,2L)
    assetMeter.setValue("LASTREADINGDATE",currentDate,2L)
    #Add History 
    if meterType == "CONTINUOUS":
      newMeterSet = assetMeter.getMboSet("NEWMETERREADING")
      history = newMeterSet
      history = newMeterSet.add()
      history.setValue("ASSETNUM",assetnum,2L)
      history.setValue("ASSETID",asid,2L)
      history.setValue("SITEID",site,2L)
      history.setValue("ORGID",org,2L)
      history.setValue("METERNAME",meterName,2L)
      history.setValue("READING",newValue,2L)
      history.setValue("READINGDATE",date,2L)
      history.setValue("INSPECTOR","MAXADMIN",2L)
      history.setValue("READINGSOURCE","ENTERED",2L)
      history.setValue("DELTA",delta,2L)
    elif meterType == "GAUGE":
      point = assetMeter.getString("POINTNUM") #add to condition monitoring
      newMeterSet = assetMeter.getMboSet("NEWMEASUREMENT")
      history = newMeterSet
      history = newMeterSet.add()
      history.setValue("ASSETNUM",assetnum,2L)
      history.setValue("ASSETID",asid,2L)
      history.setValue("SITEID",site,2L)
      history.setValue("ORGID",org,2L)
      history.setValue("METERNAME",meterName,2L)
      history.setValue("MEASUREMENTVALUE",newValue,2L)
      history.setValue("MEASUREDATE",date,2L)
      history.setValue("INSPECTOR","MAXADMIN",2L)
      history.setValue("POINTNUM",point,2L)