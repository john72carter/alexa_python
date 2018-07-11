import time
import amazon


# create a new alexa with required attribs
# your amazon emai login
email="the email you login to amazom with"
# your amazon password
password="your amazon password"
# web site .com / .co.uk etc
web_site="http://alexa.amazon.co.uk/spa/index.html#settings/dialogs"
# the name of the alexa who recording you want to here (set to all for all)
# you can use this to filter out what was heard on other devices
device="Kitchen"
# trigger name of device, used to trim "alexa what time is it" to "what time is it"
trigger="Alexa"


my_alexa = amazon.alexa(email,password,web_site,device,trigger)

# loop printing what amazon heard on your alexa(s)
latest = amazon.event(None,None,None)
while(1):
	latest = my_alexa.read()
	if latest:	
		print latest.heard
	#time.sleep(1)

