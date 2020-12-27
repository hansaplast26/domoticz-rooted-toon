# Basic Python Plugin Example
#
# Author: GizMoCuz
#
"""
<plugin key="RootedToonPlug" name="Rooted Toon" author="Snah Muabhcie" version="1.0.0" externallink="https://toon.nl">
    <description>
        <h2>Rooted Toon</h2><br/>
        <ul style="list-style-type:square">
            <li>Interfacing between Domoticz and a rooted Toon</li>
            <li>The rooted toon is directly queried via http json commands</li>
        </ul>
    </description>
    <params>
        <param field="Address" label="IP Address" width="200px" required="true" default="127.0.0.1" />
        <param field="Port" label="Port" width="30px" required="true" default="80" />
    </params>
</plugin>
"""

#no: 0 -> '10'
#yes = 1 -> '20'
#temporary 2 -> '30'
programStates = ['10','20','30']
rProgramStates = ['1','2','3']
strProgramStates = ['No', 'Yes', 'Manual']

#ComfortLevelValue: 0 ->'40'
#HomeLevelValue: 1 -> '30'
#SleepLevelValue: 2 ->  '20'
#AwayLevelValue: 3 -> '10'
#Holiday: 4 ->'60'
#programs = ['40','30','20','10','60']
programs = ['40','30','20','10','50']
rPrograms = ['3','2','1','0','4']
strPrograms = ['Comfort', 'Home', 'Sleep', 'Away','Manual']

import Domoticz
import json
from datetime import datetime
from datetime import timezone

class BasePlugin:
    toonConnThermostatInfo = None
    toonConnBoilerInfo=None
    toonConnSetControl=None
    toonConnZwaveInfo=None
    toonSetControlUrl=""

    strCurrentSetpoint = ''
    strCurrentTemp = ''
    programState = -1
    program = -1
    strToonInformation=''

    enabled = False
    def __init__(self):
        #self.var = 123
        return

    def onStart(self):
        Domoticz.Log("onStart called")

        if (len(Devices)==0):
            Domoticz.Device(Name="Current Temperature", Unit=1, TypeName="Temperature").Create()
            Domoticz.Device(Name="Setpoint Temperature", Unit=2, Type=242, Subtype=1).Create()

            programStateOptions= {"LevelActions": "||", "LevelNames": "|No|Yes|Temporary", "LevelOffHidden": "true", "SelectorStyle": "0"}
            Domoticz.Device(Name="Auto Program", Unit=3, Image=15, TypeName="Selector Switch", Options=programStateOptions).Create()

            programOptions= {"LevelActions": "||||", "LevelNames": "|Away|Sleep|Home|Comfort|Manual", "LevelOffHidden": "true", "SelectorStyle": "0"}
            Domoticz.Device(Name="Program", Unit=4, Image=15, TypeName="Selector Switch", Options=programOptions).Create()

            Domoticz.Device(Name="Boiler pressure", Unit=5, TypeName="Pressure").Create()
            Domoticz.Device(Name="Program info", Unit=6, TypeName="Text").Create()

            #Gas

#            Domoticz.Device(Name="Current Gas Flow", Unit=5, TypeName="Gas").Create()
#            Domoticz.Device(Name="Current Gas Quantity", Unit=6, TypeName="Gas").Create()

            #Electricity
#            Domoticz.Device(Name="Current Electricity Flow (Delivered) - Normal Tariff", Unit=7, Type=248, Subtype=1).Create()
#            Domoticz.Device(Name="Current Electricity Quantity (Delivered) - Normal Tariff", Unit=8, TypeName="kWh").Create()
#            Domoticz.Device(Name="Current Electricity Flow (Delivered) - Low Tariff", Unit=9, Type=248, Subtype=1).Create()
#            Domoticz.Device(Name="Current Electricity Quantity (Delivered) - Low Tariff", Unit=10, TypeName="kWh").Create()

            #Electricity
#            Domoticz.Device(Name="Current Electricity Flow (Received) - Normal Tariff", Unit=11, Type=248, Subtype=1).Create()
#            Domoticz.Device(Name="Current Electricity Quantity (Received) - Normal Tariff", Unit=12, TypeName="kWh").Create()
#            Domoticz.Device(Name="Current Electricity Flow (Received) - Low Tariff", Unit=13, Type=248, Subtype=1).Create()
#            Domoticz.Device(Name="Current Electricity Quantity (Received) - Low Tariff", Unit=14, TypeName="kWh").Create()

            # now assuming HARD=0
            Domoticz.Debug("Devices created.")


        self.toonConnThermostatInfo = Domoticz.Connection(Name="Toon Connection", Transport="TCP/IP", Protocol="HTTP", Address=Parameters["Address"], Port=Parameters["Port"])
        self.toonConnThermostatInfo.Connect()

        self.toonConnBoilerInfo = Domoticz.Connection(Name="Toon Connection", Transport="TCP/IP", Protocol="HTTP", Address=Parameters["Address"], Port=Parameters["Port"])
        self.toonConnBoilerInfo.Connect()

        #self.toonConnZwaveInfo = Domoticz.Connection(Name="Toon Connection", Transport="TCP/IP", Protocol="HTTP", Address=Parameters["Address"], Port=Parameters["Port"])
        #self.toonConnZwaveInfo.Connect()

        self.toonConnSetControl= Domoticz.Connection(Name="Toon Connection", Transport="TCP/IP", Protocol="HTTP", Address=Parameters["Address"], Port=Parameters["Port"])


        Domoticz.Heartbeat(5)
        return True


    def onStop(self):
        Domoticz.Debug("onStop called")

    def onConnect(self, Connection, Status, Description):
        Domoticz.Debug("onConnect called")
        requestUrl="/happ_thermstat?action=getThermostatInfo"

        if (Status==0):
            #Domoticz.Log("Connected successfully to: "+Parameters["Address"]+":"+Parameters["Port"])

            headers = { 'Content-Type': 'text/xml; charset=utf-8', \
                          'Connection': 'keep-alive', \
                          'Accept': 'Content-Type: text/html; charset=UTF-8', \
                          'Host': Parameters["Address"], \
                          'User-Agent':'Domoticz/1.0' }

            if (Connection == self.toonConnThermostatInfo):
                Domoticz.Debug("getThermostatInfo created")
                requestUrl="/happ_thermstat?action=getThermostatInfo"
            if (Connection == self.toonConnBoilerInfo):
                Domoticz.Debug("getBoilerInfo created")
                requestUrl="/boilerstatus/boilervalues.txt"
            #if (Connection == self.toonConnZwaveInfo):
            #    Domoticz.Log("getZwaveInfo created")
            #    requestUrl="/hdrv_zwave?action=getDevices.json"
            if (Connection == self.toonConnSetControl):
                Domoticz.Debug("getConnSetControl created")
                requestUrl=self.toonSetControlUrl

            #self.toonConn.Send(sendData)
            Domoticz.Debug("Connecting to: "+Parameters["Address"]+":"+Parameters["Port"] + requestUrl)
            Connection.Send({"Verb":"GET", "URL":requestUrl, "Headers": headers})


        else:
            Domoticz.Log("Failed to connect ("+str(Status)+":"+Description+") to "+Parameters["Address"]+":"+Parameters["Port"])

        return True

    def onMessageThermostatInfo(self, Connection, Response):
        Domoticz.Debug("onMessageThermostatInfo called")
        result='error'
        if 'result' in Response:
            result=Response['result']

        Domoticz.Debug("Toon getThermostatInfo command executed with status: " + result)
        if result!='ok':
            return

        toonInformation={}

        if 'currentTemp' in Response:
            currentTemp=float(Response['currentTemp'])/100
            strCurrentTemp="%.1f" % currentTemp
            if (strCurrentTemp!=self.strCurrentTemp):
                self.strCurrentTemp=strCurrentTemp
                Domoticz.Log("Updating current Temperature = "+strCurrentTemp)
                Devices[1].Update(nValue=0, sValue=strCurrentTemp)

        if 'currentSetpoint' in Response:
            currentSetpoint=float(Response['currentSetpoint'])/100
            strCurrentSetpoint="%.1f" % currentSetpoint
            if (strCurrentSetpoint!=self.strCurrentSetpoint):
                self.strCurrentSetpoint=strCurrentSetpoint
                Domoticz.Log("Updating current Setpoint = "+strCurrentSetpoint)
                Devices[2].Update(nValue=0, sValue=strCurrentSetpoint)

        if 'programState' in Response:
            programState=int(Response['programState'])
            if (programState!=self.programState):
                self.programState=programState
                Domoticz.Log("Updating programState  = " + str(programState)+"->"+ programStates[programState])
                Devices[3].Update(nValue=0, sValue=programStates[programState])

        if 'activeState' in Response:
            program=int(Response['activeState'])
            if (program!=self.program):
                self.program=program
                Domoticz.Log("Updating program = " +str(program)+"->" + programs[program])
                Devices[4].Update(nValue=0, sValue=programs[program])

        if 'nextTime' in Response:
            toonInformation['nextTime']=Response['nextTime']

        if 'nextState' in Response:
            toonInformation['nextState']=Response['nextState']

        if 'nextProgram' in Response:
            toonInformation['nextProgram']=Response['nextProgram']

        if 'nextSetpoint'in Response:
            toonInformation['nextSetpoint']=Response['nextSetpoint']


        if (len(toonInformation)==4):
            strToonInformation='This should never happen %s' % toonInformation['nextProgram']
            if int(toonInformation['nextProgram'])==0:
                strToonInformation="Progam is off"

            elif int(toonInformation['nextProgram'])>0:
                dt=datetime.fromtimestamp(int(toonInformation['nextTime']))
                strNextTime=dt.strftime("%Y-%d-%m %H:%M:%S")
                strNextProgram=strPrograms[int(toonInformation['nextState'])]
                strNextSetpoint="%.1f" % (float(toonInformation['nextSetpoint'])/100)

                strToonInformation="Next program %s (%s C) at %s" % (strNextProgram, strNextSetpoint, strNextTime)
                if (strToonInformation!=self.strToonInformation):
                    Domoticz.Log("Updating Toon information")
                    self.strToonInformation=strToonInformation

            Devices[6].Update(nValue=0, sValue=strToonInformation)

        return

    def onMessageBoilerInfo(self, Connection, Response):
        Domoticz.Debug("onMessageBoilerInfo called")
        if 'boilerPressure' in Response:
            Domoticz.Debug("boilerpressure: "+("%.1f" % Response['boilerPressure']))
            strBoilerPressure="%.1f" % Response['boilerPressure']
            Devices[5].Update(nValue=0, sValue=strBoilerPressure)

        return

    def onMessageZwaveInfo(self, Connection, Response):
        #todo implementation, maybe.
        Domoticz.Log("onMessageZwaveInfo called")



    def onMessage(self, Connection, Data):
        Domoticz.Debug("onMessage called")

        try:
            strData = Data["Data"].decode("utf-8", "ignore")
        except:
            Domoticz.Log("Something fishy")
            if (Connection==self.toonConnThermostatInfo):
                Domoticz.Log("ThermostatInfo")
                return
            if (Connection==self.toonConnBoilerInfo):
                Domoticz.Log("BoilerInfo")
                return

            else:
                Domoticz.Log("Unknown connection")
            return

        Domoticz.Debug(strData)
        if (strData[0]!='{'):
            Domoticz.Log("onMessage aborted, response format not JSON")
            return
        Response = json.loads(strData)

        if (Connection==self.toonConnSetControl):
            Domoticz.Log("onMessage: toonConnSetControl")
            result='error'
            if 'result' in Response:
                result=Response['result']

            Domoticz.Log("Toon set command executed with status: " + result)
            return

        if (Connection==self.toonConnThermostatInfo):
            self.onMessageThermostatInfo(Connection, Response)

        if (Connection==self.toonConnBoilerInfo):
            self.onMessageBoilerInfo(Connection, Response)

        ##if (Connection==self.toonConnZwaveInfo):
        #    Domoticz.Log("onMessage: toonConnZwaveInfo")


        return


    def onCommand(self, Unit, Command, Level, Hue):
        Domoticz.Debug("onCommand called for Unit " + str(Unit) + ": Parameter '" + str(Command) + "', Level: " + str(Level))

        if (Unit == 2):
            strLevel=str(int(Level*100))
            Domoticz.Debug("Toon New setpoint: %s" % str(Level))
            self.strCurrentSetpoint=str(Level)
            Devices[Unit].Update(nValue=0, sValue=str(Level))
            self.toonSetControlUrl="/happ_thermstat?action=setSetpoint&Setpoint=" + strLevel
            self.toonConnSetControl.Connect()

        if (Unit == 3):
            Domoticz.Log("Toon ProgramState")
            Domoticz.Log(str(Level)+" -> " + rProgramStates[int((Level//10)-1)])
            self.programState=str(Level)
            Devices[3].Update(nValue = 0, sValue = str(Level))
            self.toonSetControlUrl="/happ_thermstat?action=changeSchemeState&state="+rProgramStates[int((Level//10)-1)]
            self.toonConnSetControl.Connect()

        if (Unit == 4):
            Domoticz.Debug("Toon Program")
            Domoticz.Debug(str(Level)+" -> "+rPrograms[int((Level//10)-1)])
            self.program=str(Level)
            Devices[4].Update(nValue = 0, sValue = str(Level))
            self.toonSetControlUrl="/happ_thermstat?action=changeSchemeState&state=2&temperatureState="+rPrograms[int((Level//10)-1)]
            Domoticz.Debug(self.toonSetControlUrl)
            self.toonConnSetControl.Connect()


        #tbd send to Toon

    def onNotification(self, Name, Subject, Text, Status, Priority, Sound, ImageFile):
        Domoticz.Debug("Notification: " + Name + "," + Subject + "," + Text + "," + Status + "," + str(Priority) + "," + Sound + "," + ImageFile)

    def onDisconnect(self, Connection):
        Domoticz.Debug("onDisconnect called")

    def onHeartbeat(self):
        Domoticz.Debug("onHeartbeat called")

        if (self.toonConnThermostatInfo.Connected()==False):
            self.toonConnThermostatInfo.Connect()

        if (self.toonConnBoilerInfo.Connected()==False):
            self.toonConnBoilerInfo.Connect()

        #if (self.toonConnZwaveInfo.Connected()==False):
        #    self.toonConnZwaveInfo.Connect()


global _plugin
_plugin = BasePlugin()

def onStart():
    global _plugin
    _plugin.onStart()

def onStop():
    global _plugin
    _plugin.onStop()

def onConnect(Connection, Status, Description):
    global _plugin
    _plugin.onConnect(Connection, Status, Description)

def onMessage(Connection, Data):
    global _plugin
    _plugin.onMessage(Connection, Data)

def onCommand(Unit, Command, Level, Hue):
    global _plugin
    _plugin.onCommand(Unit, Command, Level, Hue)

def onNotification(Name, Subject, Text, Status, Priority, Sound, ImageFile):
    global _plugin
    _plugin.onNotification(Name, Subject, Text, Status, Priority, Sound, ImageFile)

def onDisconnect(Connection):
    global _plugin
    _plugin.onDisconnect(Connection)

def onHeartbeat():
    global _plugin
    _plugin.onHeartbeat()

    # Generic helper functions
def DumpConfigToLog():
    for x in Parameters:
        if Parameters[x] != "":
            Domoticz.Debug( "'" + x + "':'" + str(Parameters[x]) + "'")
    Domoticz.Debug("Device count: " + str(len(Devices)))
    for x in Devices:
        Domoticz.Debug("Device:           " + str(x) + " - " + str(Devices[x]))
        Domoticz.Debug("Device ID:       '" + str(Devices[x].ID) + "'")
        Domoticz.Debug("Device Name:     '" + Devices[x].Name + "'")
        Domoticz.Debug("Device nValue:    " + str(Devices[x].nValue))
        Domoticz.Debug("Device sValue:   '" + Devices[x].sValue + "'")
        Domoticz.Debug("Device LastLevel: " + str(Devices[x].LastLevel))
    return
