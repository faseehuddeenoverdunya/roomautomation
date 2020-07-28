# start up routine
# connect to wifi or turn on ap mode if no wifi connection found
# check for presistent states and set pins/outputs as required
import usocket as socket
import json
import os
import time as t
import machine as m
import network as n
import esp
import keypad
import _thread as thread


esp.osdebug(None)
led = m.Pin(2, m.Pin.OUT)
sta_if = n.WLAN(n.STA_IF)
ap_if = n.WLAN(n.AP_IF)


def blink(times):
    for i in range(times):
        led.on()
        t.sleep(0.1)
        led.off()
        t.sleep(0.1)


def startwireless():

    no_ap = True
    sta_if.active(True)
    blink(3)
    sta_if.config(dhcp_hostname=deviceData["deviceName"])
    cpass = deviceData['wifiAP'][0]
    for try_connect in range(int(deviceData['try_connect'])):
        print("Connecting to " + cpass['ssid'] + ". Try: " + str(try_connect))
        sta_if.connect(cpass['ssid'], cpass['password'])
        t.sleep(1)
        if sta_if.isconnected():
            no_ap = False
            print(sta_if.ifconfig())
            return 0

    if no_ap:
        print("start ap mode")

        sta_if.active(False)
        ap_if.active(True)
        ap_if.config(essid=deviceData["deviceName"],
                     authmode=n.AUTH_WPA_WPA2_PSK,
                     password=deviceData["apPass"])
        return 1


def handleRequest(request):
    if request == '/':
        response = page
    elif request[1] == 's' and len(request) == 3:
        toggleState(int(deviceData["SwitchPins"]
                        [request[1:]]["Pin"]), request[1:])
        response = "changed State"

    return response


def handle(sock):
    lineNumber = 0
    try:
        while True:
            line = sock.readline()
            if not line:
                break
            if lineNumber == 0:
                if line is not None:
                    request = str(line).split(" ")[1]
                    blink(1)
                    sock.send(handleRequest(request))
            lineNumber += 1
    except Exception as e:
        return "pagal"
    return "sucessful"


def toggleState(SelectedPin: int, SwitchName):
    # change gpio value
    # send state changes to save file, to remember current light state
    # print(str(SelectedPin))
    # invert value of switch
    cSwitch = m.Pin(SelectedPin)
    val = not int(cSwitch.value())
    cSwitch.value(val)
    # change value in mem json
    deviceData["SwitchPins"][SwitchName]["State"] = val
    # dump json to file
    with open("deviceData.json", "w+") as deviceJson:
        json.dump(deviceData, deviceJson)


def startServer(wirelessType, port: int):
    if wirelessType == 0:
        host = sta_if.ifconfig()[0]
    elif wirelessType == 1:
        host = ap_if.ifconfig()[0]

    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind(socket.getaddrinfo(host, port)[0][-1])
    server.listen(3)

    while True:
        sock, addr = server.accept()
        sock.setblocking(False)
        #
        request = handle(sock)
        #
        sock.close()


def InitPinStates():
    for sw in deviceData["SwitchPins"]:
        pin = int(deviceData["SwitchPins"][sw]["Pin"])
        state = int(deviceData["SwitchPins"][sw]["State"])
        m.Pin(pin, m.Pin.OUT, value=state)


def keypadControl():
    while True:
        inp = keypad.readKeyPress()
        t.sleep(0.4)

        if inp == "#":
            pass
        elif inp == '1' or inp == '2' or inp == '3' or inp == '4':
            if int(inp) > 0 and int(inp) <= 4:
                SwitchName = "s" + inp
                SwitchPin = int(deviceData["SwitchPins"][SwitchName]["Pin"])
                toggleState(SwitchPin, SwitchName)
        else:
            pass


# loading device data
with open("site/spa.html") as storedPage:
    page = storedPage.read()

with open('deviceData.json') as f:
    deviceData = json.load(f)


# starting Server, rest follows in server code
thread.start_new_thread(keypadControl, ())

# trying to connect to wifi with already saved data

#startServer(startwireless(), 80)
thread.start_new_thread(startServer, (startwireless(), 80))

# loading pinStates
InitPinStates()
