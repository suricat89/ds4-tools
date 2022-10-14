#!/usr/bin/env python

import subprocess
import re
from time import sleep

registeredDevices = [
  '48:18:8D:6A:A2:17',
  '00:1F:E2:DF:20:56'
]

sleepTime = 1
scanTimeout = '2'

def executeCommand(command: str):
  result = subprocess.check_output(command, shell=True).decode('utf-8')
  result = result.split('\n')
  return result

def checkCommandSucceeded(result: list[str], successMsg: str):
  for l in result:
    if re.search(successMsg, l) != None:
      return True
  return False

def scanDevices():
  result = executeCommand('bluetoothctl --timeout %s scan on' % (scanTimeout))
  
  if len(result) > 2:
    for i in range(2, len(result)):
      if result[i] != '':
        print(result[i])
  
  return result

def removeDevice(deviceAddress: str):
  try:
    result = executeCommand('bluetoothctl remove %s' % (deviceAddress))
    return checkCommandSucceeded(result, 'Device has been removed')
  except:
    return False

def trustDevice(deviceAddress: str):
  try:
    result = executeCommand('bluetoothctl trust %s' % (deviceAddress))
    return checkCommandSucceeded(result, '.* trust succeeded')
  except:
    return False

def connectDevice(deviceAddress: str):
  try:
    result = executeCommand('bluetoothctl connect %s' % (deviceAddress))
    return checkCommandSucceeded(result, 'Connection successful')
  except:
    return False

def checkRegisteredDeviceScanning(results: list[str]):
  isDeviceRegistered = False
  isDeviceTurningOff = False
  device = ''

  for registeredDevice in registeredDevices:
    for result in results:
      if registeredDevice in result:
        isDeviceRegistered = True
        device = registeredDevice
        if re.search('.* Connected: no', result):
          isDeviceTurningOff = True

  if isDeviceRegistered and not isDeviceTurningOff:
    return device

  return None

def pairDevice(deviceAddress: str):
  print('Trying to connect to device %s' % (deviceAddress))
  connectedDevice = connectDevice(deviceAddress)
  print('Connect success: %s' % (connectedDevice))
  if (connectedDevice):
    return True

  print('Removing device %s' % (deviceAddress))
  removedDevice = removeDevice(deviceAddress)
  print('Remove success: %s' % (removedDevice))
  if removedDevice == False:
    return False

  print('Scanning devices again')
  result = scanDevices()
  deviceAddress = checkRegisteredDeviceScanning(result)
  print('Device available: %s' % (deviceAddress))

  print('Trusting device %s' % (deviceAddress))
  trustedDevice = trustDevice(deviceAddress)
  print('Trust success: %s' % (trustedDevice))
  if trustedDevice == False:
    return False

  print('Connecting to device %s' % (deviceAddress))
  connectedDevice = connectDevice(deviceAddress)
  print('Connect success: %s' % (connectedDevice))

  return connectedDevice

print('Starting listener')
while(True):
  sleep(sleepTime)
  result = scanDevices()
  registeredDevice = checkRegisteredDeviceScanning(result)

  if registeredDevice == None:
    continue

  print('Device discovered: %s' % (registeredDevice))
  pairDevice(registeredDevice)
