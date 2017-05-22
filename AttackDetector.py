from Record import Record
from HitStructure import HitStructure
from datetime import datetime
import time
import os
class AttackDetector(object):
	#def __init__(self):
	#Function to calculate the time difference
	def calculateTimeDifference(self,lastHitTime,currentTime):
		desiredFormatForDifference = '%H:%M:%S'
		difference = datetime.strptime(currentTime,desiredFormatForDifference) - datetime.strptime(lastHitTime, desiredFormatForDifference)
		difference = difference.seconds*1000
		return difference

	#Loads the inputfile onto a list and passes onto the fraudDetection function
	def loadInput(self,filename):
		dataFile=open(filename,'r')
		recordList = []
		setOfSuspiciousIPs=set()
		for line in dataFile:
			#sends each line of the file to the split function in order to populate the Record data structure from the required fields of the record in the actual file
			record = self.splitFields(line)
			recordList.append(record)
		#sends the data onto the main function for detecting the suspicious IP's
		countOfSuspiciousIPs,setOfSuspiciousIPs=self.fraudDetection(recordList)
		#Redirects the output to an output file
		self.writeOutput(setOfSuspiciousIPs)
		dataFile.close()
		return countOfSuspiciousIPs
	
	#Main function responsible for detecting the suspicious IPs	
	def fraudDetection(self,recordList):
		#print("Record is : "+ r.getIpAddress() +"Time:"+ r.gettimeStamp())
		
		mapOfRecords = {} # responsible for maintaining the count of seen IP's in the current 2minute window
		suspiciousIPs = set() # responsible for mainitaining the suspicious IPs
		#The below function implements the idea:
		"""
			1.If IP not in map, add a new entry into the map with the following data:
				Key : IP
				Value : Hit Structure [timestamp:timestampOfTheIP,count:1]
			2.If IP in map,check whether the timestamp is within the last 30 secs
				a.If yes, increment the count value in the Hit Structure by 1
				b.If no, update the entry in the map with the timestamp of this IP and resetting the count to 1.
			3.If the count exceeds the threshold, add it to the set of suspicious IPs
				
		"""
		for record in recordList:
			ipAddress = record.getIpAddress()
			#print("Currently processing :"+ ipAddress)
			currentTime=record.gettimeStamp()
			#Implements step 2. of the above algorithm
			if ipAddress in mapOfRecords:
				lastHitTime = mapOfRecords[ipAddress].gettimeStamp()#fetches the last timestamp this IP was seen in the 2 minute window 
				difference = self.calculateTimeDifference(lastHitTime,currentTime)#calculates the difference between current record and last seen same IP record
				#print("Difference :"+ str(difference))
				diffSeconds = int(difference/1000%60)
				diffMinutes = int(difference/(60*1000)%60)
				diffHours = int(difference/(60*60*1000))
				#print(str(diffSeconds) +" "+str(diffMinutes)+" "+str(diffHours))
				#Implements step 2a. of the above algortihm
				if diffHours == 0 and diffMinutes == 0 and diffSeconds <=30:	
					updateCount = mapOfRecords[ipAddress].getCount();
					h=HitStructure(lastHitTime,updateCount+1)
					mapOfRecords[ipAddress]=h
					#Implements step 3 of the above algortihm
					if updateCount+1>=87:
						if ipAddress not in suspiciousIPs:
							suspiciousIPs.add(ipAddress)
				#Implements step 2b. of the above algortihm 
				else:
					h=HitStructure(lastHitTime,1)
			#Implements step 1 of the above algorithm
			else:
				h = HitStructure(currentTime,1)
				mapOfRecords[ipAddress]=h
		return len(suspiciousIPs),suspiciousIPs
	
	#Function to check if output file exists from the previous run. If yes, overwrites the output file with the new output
	def writeOutput(self,suspiciousIPs):
		outputFile=os.path.expanduser('~') + '/dosDetector/suspicious.txt'
		try:
    			os.remove(outputFile)#If the file already exists, remove it
		except OSError:
    			pass
		fileHandler = open(outputFile,'a')
		#Write the unique list of suspicious IP's onto a different file
		for ip in suspiciousIPs:
			fileHandler.write(ip+"\n")
		fileHandler.close()
		
	#Function to accept a line and populate the Record Data Structure for easy access
	def splitFields(self,line):
		fields = line.split(" ")
		timestamp=fields[3].split(":",1)[1].split(" ", 1)[0]
		r = Record(fields[0],timestamp);
		return r
#Main function
def main():
	#Creates an instance of the above class
	attackDetector = AttackDetector()
	filename = "/u/aritde/dosDetector/apache-access-log.txt"
	result = attackDetector.loadInput(filename)
	#Displays the suspicious IP count on the console
	print("Suspicious IPs : "+str(result))

if __name__== "__main__":
	main()
