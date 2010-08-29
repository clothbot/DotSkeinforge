"""
Extrude is a script to display and extrude a gcode file.

It controls the extruder and movement.  It can read linear and helical move commands. It saves a log file with the suffix _log.

To run extrude, install python 2.x on your machine, which is avaliable from http://www.python.org/download/

Then in the folder which extrude is in, type 'python' in a shell to run the python interpreter.  Finally type 'import extrude' to import
this program.  Extrude requires pySerial installed for this module to work. If you are using Fedora it is available on yum
(run "sudo yum install pyserial").  To actually control the reprap requires write access to the serial device, running as root is
one way to get that access.


This example displays and extrudes a gcode file.  This example is run in a terminal as root in the folder which contains
Hollow Square.gcode, and extrude.py.

>>> import extrude
Extrude has been imported.
The gcode files in this directory that are not log files are the following:
['Hollow Square.gcode']


>>> extrude.display()
File Hollow Square.gcode is being displayed.
reprap.serial = serial.Serial(0, 19200, timeout = 60)
reprap.cartesian.x.active = True
reprap.cartesian.y.active = True
reprap.cartesian.z.active = True
reprap.extruder.active = True
reprap.cartesian.x.setNotify()
reprap.cartesian.y.setNotify()
reprap.cartesian.z.setNotify()
reprap.cartesian.x.limit = 2523
reprap.cartesian.y.limit = 2000
reprap.cartesian.homeReset( 200, True )
( GCode generated by March 29,2007 Skeinforge )
( Extruder Initialization )
M100 P210
M103
reprap.extruder.setMotor(reprap.CMD_REVERSE, 0)
..
many lines of gcode and extruder commands
..
reprap.cartesian.homeReset( 600, True )
reprap.cartesian.free()
The gcode log file is saved as Hollow Square_log.gcode


>>> extrude.displayFile("Hollow Square.gcode")
File Hollow Square.gcode is being displayed.
..
The gcode log file is saved as Hollow Square_log.gcode


>>> extrude.displayFiles(["Hollow Square.gcode"])
File Hollow Square.gcode is being displayed.
..
The gcode log file is saved as Hollow Square_log.gcode


>>> extrude.displayText("
( GCode generated by March 29,2007 Skeinforge )
( Extruder Initialization )
..
many lines of gcode
..
")

reprap.serial = serial.Serial(0, 19200, timeout = 60)
reprap.cartesian.x.active = True
reprap.cartesian.y.active = True
reprap.cartesian.z.active = True
reprap.extruder.active = True
reprap.cartesian.x.setNotify()
reprap.cartesian.y.setNotify()
reprap.cartesian.z.setNotify()
reprap.cartesian.x.limit = 2523
reprap.cartesian.y.limit = 2000
reprap.cartesian.homeReset( 200, True )
( GCode generated by March 29,2007 Skeinforge )
( Extruder Initialization )
M100 P210
M103
reprap.extruder.setMotor(reprap.CMD_REVERSE, 0)
..
many lines of gcode and extruder commands
..
reprap.cartesian.homeReset( 600, True )
reprap.cartesian.free()


Note: On my system the reprap is not connected, so I get can not connect messages, like:

>>> extrude.extrude()
File Hollow Square.gcode is being extruded.
reprap.serial = serial.Serial(0, 19200, timeout = 60)
reprap.cartesian.x.active = True
reprap.cartesian.y.active = True
reprap.cartesian.z.active = True
reprap.extruder.active = True
reprap.cartesian.x.setNotify()
Error: Serial timeout
Error: ACK not recieved
..

On a system where a reprap is connected to the serial port, you should get the following:

>>> extrude.extrude()
File Hollow Square.gcode is being extruded.
..
The gcode log file is saved as Hollow Square_log.gcode


>>> extrude.extrudeFile("Hollow Square.gcode")
File Hollow Square.gcode is being extruded.
..
The gcode log file is saved as Hollow Square_log.gcode


>>> extrude.extrudeFiles(["Hollow Square.gcode"])
File Hollow Square.gcode is being extruded.
..
The gcode log file is saved as Hollow Square_log.gcode


>>> extrude.extrudeText("
( GCode generated by March 29,2007 Skeinforge )
( Extruder Initialization )
..
many lines of gcode
..
")

reprap.serial = serial.Serial(0, 19200, timeout = 60)
reprap.cartesian.x.active = True
reprap.cartesian.y.active = True
reprap.cartesian.z.active = True
reprap.extruder.active = True
reprap.cartesian.x.setNotify()
reprap.cartesian.y.setNotify()
reprap.cartesian.z.setNotify()
reprap.cartesian.x.limit = 2523
reprap.cartesian.y.limit = 2000
reprap.cartesian.homeReset( 200, True )
( GCode generated by March 29,2007 Skeinforge )
( Extruder Initialization )
M100 P210
M103
reprap.extruder.setMotor(reprap.CMD_REVERSE, 0)
..
many lines of gcode and extruder commands
..
reprap.cartesian.homeReset( 600, True )
reprap.cartesian.free()
"""

from __future__ import absolute_import
#Init has to be imported first because it has code to workaround the python bug where relative imports don't work if the module is imported as a main module.
import __init__

try:
	import serial	# Import the pySerial modules.
except:
	print('You do not have pySerial installed, which is needed to control the serial port.')
	print('Information on pySerial is at:\nhttp://pyserial.wiki.sourceforge.net/pySerial')

from skeinforge_tools.skeinforge_utilities.vector3 import Vector3
from skeinforge_tools.skeinforge_utilities import euclidean
from skeinforge_tools.skeinforge_utilities import gcodec
import math
import os
import reprap	# Import the reprap module.
import time

__author__ = "Enrique Perez (perez_enrique@yahoo.com)"
__credits__ = 'greenarrow <http://forums.reprap.org/profile.php?12,81>'
__date__ = "$Date: 2008/21/04 $"
__license__ = "GPL 3.0"


def display( filename = ''):
	"Parse a gcode file and display the commands.  If no filename is specified, parse all the gcode files which are not log files in this folder."
	if filename == '':
		displayFiles( getGCodeFilesWhichAreNotLogFiles() )
		return
	displayFile( filename )

def displayFile( filename ):
	"Parse a gcode file and display the commands."
	print('File ' + filename + ' is being displayed.')
	fileText = gcodec.getFileText( filename )
	gcodec.writeFileMessageSuffix( filename, displayText( fileText ), 'The gcode log file is saved as ', '_log')

def displayFiles( filenames ):
	"Parse gcode files and display the commands."
	for filename in filenames:
		displayFile( filename )

def displayText(gcodeText):
	"Parse a gcode text and display the commands."
	skein = displaySkein()
	skein.parseText(gcodeText)
	return skein.output

def extrude( filename = ''):
	"""Parse a gcode file and send the commands to the extruder.  If no filename is specified, parse all the gcode files which are not log files in this folder.
	This function requires write access to the serial device, running as root is one way to get that access."""
	if filename == '':
		extrudeFiles( getGCodeFilesWhichAreNotLogFiles() )
		return
	extrudeFile( filename )

def extrudeFile( filename ):
	"""Parse a gcode file and send the commands to the extruder.
	This function requires write access to the serial device, running as root is one way to get that access."""
	print('File ' + filename + ' is being extruded.')
	fileText = gcodec.getFileText( filename )
	gcodec.writeFileMessageSuffix( filename, extrudeText( fileText ), 'The gcode log file is saved as ', '_log')

def extrudeFiles( filenames ):
	"""Parse gcode files and send the commands to the extruder.
	This function requires write access to the serial device, running as root is one way to get that access."""
	for filename in filenames:
		extrudeFile( filename )

def extrudeText(gcodeText):
	"""Parse a gcode text and send the commands to the extruder.
	This function requires write access to the serial device, running as root is one way to get that access."""
	skein = extrudeSkein()
	skein.parseText(gcodeText)
	return skein.output

def getGCodeFilesWhichAreNotLogFiles():
	"Get gcode files which are not log files."
	return gcodec.getFilesWithFileTypeWithoutWords('gcode', ['_log'] )

def getIntegerString( number ):
	"Get integer as string."
	return str( int( number ) )


class displaySkein:
	"A class to display a gcode skein of extrusions."
	def __init__( self ):
		self.extruderActive = 0
		self.feedrateMinute = 200.0
		self.oldLocation = None
		self.output = ''

	def addToOutput( self, line ):
		"Add line with a newline at the end to the output."
		print(line)
		self.output += line + '\n'

	def evaluateCommand( self, command ):
		"Add an extruder command to the output."
		self.addToOutput( command )

	def helicalMove( self, isCounterclockwise, splitLine ):
		"Parse a helical move gcode line and send the commands to the extruder."
		if self.oldLocation == None:
			return
		location = Vector3( self.oldLocation )
		self.setFeedrate( splitLine )
		setPointToSplitLine( location, splitLine )
		location = location + self.oldLocation
		center = Vector3( self.oldLocation )
		indexOfR = indexOfStartingWithSecond( "R", splitLine )
		if indexOfR > 0:
			radius = getDoubleAfterFirstLetter( splitLine[ indexOfR ] )
			halfLocationMinusOld = location - self.oldLocation
			halfLocationMinusOld *= 0.5
			halfLocationMinusOldLength = halfLocationMinusOld.length()
			centerMidpointDistance = math.sqrt( radius * radius - halfLocationMinusOldLength * halfLocationMinusOldLength )
			centerMinusMidpoint = getRotatedWiddershinsQuarterAroundZAxis( halfLocationMinusOld )
			centerMinusMidpoint.normalize()
			centerMinusMidpoint *= centerMidpointDistance
			if isCounterclockwise:
				center.setToVec3( halfLocationMinusOld + centerMinusMidpoint )
			else:
				center.setToVec3( halfLocationMinusOld - centerMinusMidpoint )
		else:
			center.x = getDoubleForLetter( "I", splitLine )
			center.y = getDoubleForLetter( "J", splitLine )
		curveSection = 0.5
		center += self.oldLocation
		afterCenterSegment = location - center
		beforeCenterSegment = self.oldLocation - center
		afterCenterDifferenceAngle = getAngleAroundZAxisDifference( afterCenterSegment, beforeCenterSegment )
		absoluteDifferenceAngle = abs( afterCenterDifferenceAngle )
		steps = int( math.ceil( max( absoluteDifferenceAngle * 2.4, absoluteDifferenceAngle * beforeCenterSegment.length() / curveSection ) ) )
		stepPlaneAngle = getPolar( afterCenterDifferenceAngle / steps, 1.0 )
		zIncrement = ( afterCenterSegment.z - beforeCenterSegment.z ) / float( steps )
		for step in range( 1, steps ):
			beforeCenterSegment = getRoundZAxisByPlaneAngle( stepPlaneAngle, beforeCenterSegment )
			beforeCenterSegment.z += zIncrement
			arcPoint = center + beforeCenterSegment
			self.moveExtruder( arcPoint )
		self.moveExtruder( location )
		self.oldLocation = location

	def homeReset( self ):
		"Send all axies to home position. Wait until arrival."
		homeCommandString = 'reprap.cartesian.homeReset(' + getIntegerString( self.feedrateMinute ) + ', True )'
		self.evaluateCommand( homeCommandString )

	def linearMove( self, splitLine ):
		"Parse a linear move gcode line and send the commands to the extruder."
		location = Vector3()
		if self.oldLocation != None:
			location = self.oldLocation
		self.setFeedrate( splitLine )
		setPointToSplitLine( location, splitLine )
		self.moveExtruder( location )
		self.oldLocation = location

	def moveExtruder( self, location ):
		"Seek to location. Wait until arrival."
		moveSpeedString = getIntegerString( self.feedrateMinute )
		xMoveString = getIntegerString( location.x )
		yMoveString = getIntegerString( location.y )
		zMoveString = getIntegerString( location.z )
		moveCommandString = 'reprap.cartesian.seek( (' + xMoveString + ', ' + yMoveString + ', ' + zMoveString + '), ' + moveSpeedString + ', True )'
		self.evaluateCommand( moveCommandString )

	def parseGCode( self, lines ):
		"Parse gcode and send the commands to the extruder."
		self.evaluateCommand('reprap.serial = serial.Serial(0, 19200, timeout = 60)')	# Initialise serial port, here the first port (0) is used.
		self.evaluateCommand('reprap.cartesian.x.active = True')	# These devices are present in network, will automatically scan in the future.
		self.evaluateCommand('reprap.cartesian.y.active = True')
		self.evaluateCommand('reprap.cartesian.z.active = True')
		self.evaluateCommand('reprap.extruder.active = True')
		self.evaluateCommand('reprap.cartesian.x.setNotify()')
		self.evaluateCommand('reprap.cartesian.y.setNotify()')
		self.evaluateCommand('reprap.cartesian.z.setNotify()')
		self.evaluateCommand('reprap.cartesian.x.limit = 2523')
		self.evaluateCommand('reprap.cartesian.y.limit = 2000')
		self.homeReset()	# The module is now ready to receive commands
		for line in lines:
			self.parseLine(line)
		self.homeReset()
		self.evaluateCommand('reprap.cartesian.free()')	# Shut off power to all motors.

	def parseLine( self, line ):
		"Parse a gcode line and send the command to the extruder."
		self.addToOutput(line)
		splitLine = line.split(' ')
		if len( splitLine ) < 1:
			return 0
		firstWord = splitLine[0]
		if firstWord == 'G1':
			self.linearMove( splitLine )
		if firstWord == 'G2':
			self.helicalMove( False, splitLine )
		if firstWord == 'G3':
			self.helicalMove( True, splitLine )
		if firstWord == 'M101':
			self.extruderActive = 1
			self.evaluateCommand('reprap.extruder.setMotor(reprap.CMD_REVERSE, 150)')
		if firstWord == 'M103':
			self.extruderActive = 0
			self.evaluateCommand('reprap.extruder.setMotor(reprap.CMD_REVERSE, 0)')
			self.oldActiveLocation = None

	def parseText( self, text ):
		"Parse a gcode text and evaluate the commands."
		textLines = getTextLines( text )
		self.parseGCode( textLines )

	def setFeedrate( self, splitLine ):
		"Set the feedrate to the gcode split line."
		indexOfF = indexOfStartingWithSecond( "F", splitLine )
		if indexOfF > 0:
			self.feedrateMinute = getDoubleAfterFirstLetter( splitLine[ indexOfF ] )


class extrudeSkein( displaySkein ):
	"A class to extrude a gcode skein of extrusions."
	def evaluateCommand( self, command ):
		"""Add an extruder command to the output and evaluate the extruder command.
		Display the entire command, but only evaluate the command after the first equal sign."""
		self.addToOutput( command )
		firstEqualIndex = command.find('=')
		exec( command )


print('Extrude has been imported.')
print('The gcode files in this directory that are not log files are the following:')
print( getGCodeFilesWhichAreNotLogFiles() )
