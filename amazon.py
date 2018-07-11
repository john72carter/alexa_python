from selenium import webdriver
from selenium.webdriver.common.keys import Keys
import time
import subprocess

class browser:
	def __init__(self,url):
		self.cmd_err = None
		self.new_ids = []
		self.existing_ids = self.__get_window_ids('Amazon Sign In')
		self.url = url
		self.window_id = 0
		self.driver = webdriver.Firefox()
	  	try:
	     		self.driver.get(self.url)
	  	except:
	     		print "failed driver.get "+self.url
	     		print "will retry in 30 seconds"
	     		time.sleep(30)
	     		return "timeout"
		   
		while len(self.new_ids) < 1:
			self.new_ids = self.__get_window_ids('Amazon Sign In')
			time.sleep(1)
		if len(self.new_ids) == 1:
			self.window_id = self.new_ids[0]
		else:
			for old in self.existing_ids:
				for new in self.new_ids:
					print new + " " + old
					print str(self.new_ids)

	def __get_window_ids(self,title):
		temp_list = []
		window_id_list =[]
		self.title = title
		try:
		  p = subprocess.Popen(['xdotool','search','--name',self.title],stdout=subprocess.PIPE,stderr=subprocess.PIPE)
		  ids,self.cmd_err = p.communicate()
		  temp_list = ids.split("\n")
		  for win_id in temp_list:
			if len(win_id) > 0:
				window_id_list.append(win_id)
					
		  return window_id_list
		except:
		  print "attempt to search for Amazon Alexa window using xdotool failed" + str(self.cmd_err)
		return None

	def minimise(self):
		try: 
		  p = subprocess.Popen(['xdotool','windowminimize',self.window_id],stdout=subprocess.PIPE,stderr=subprocess.PIPE)
		  result,self.cmd_err = p.communicate()
		except:
		  print "attempt to minimise Amazon Alexa window using xdotool failed"+ str(self.cmd_err)

	def close(self):
		try: 
	  	
		  p = subprocess.Popen(['xdotool','windowclose',self.window_id],stdout=subprocess.PIPE,stderr=subprocess.PIPE)
		  result,self.cmd_err = p.communicate()	
		except:
		  print "attempt to close Amazon Alexa window using xdotool failed"+ str(self.cmd_err)

class event:
	def __init__(self,heard,time,device):
		self.heard = heard 	# what your alexa heard you say
		self.time = time    	# when it recorded it 
		self.device = device 	# then name of the device the recording was made on

	def __eq__(self, other):
		return (str(self.heard) == str(other.heard)) and (self.time==other.time) and (self.device==other.device)

	def __ne__(self, other):
		return (str(self.heard) != str(other.heard)) or (self.time != other.time) or (self.device != other.device)


class alexa():
		
	def __init__(self,user,password,url,device,trigger):
		self.history = []
		self.new_history = []
		self.device = device
		self.trigger = trigger
		self.user = user
		self.password = password
		self.url = url
		self.exceptions = 0
		self.window_id = None
		self.cmd_err = None
		self.new_event = False
		self.__reset()

	def __reset(self):
		if self.window_id != None:
			self.my_browser.close()
		self.my_browser = browser(self.url)	
		self.driver = self.my_browser.driver
		
		self.__login_to_amazon()
		self.my_browser.minimise()
		self.__load_history_page()
		self.__process_alexa_history_entries()
		self.history = self.new_history
		print "Init complete"
	


	def read(self):
		ret_val = self.__process_alexa_history_entries()
		if ret_val == "_Reset":
			self.__reset()
		        print "back from reset  self.new_event "+str(self.new_event)
			#self.__process_alexa_history_entries()

		self.history = self.new_history
		if self.new_event:
			#print "read returning "+str(self.new_history[0].heard)
			return self.new_history[0]
		

	def __login_to_amazon(self):

	  # i dont know whats happening here but if you keep trying eventually the "a-page" will open
	  page_not_ready=True
	  while(page_not_ready):
	    ids = self.driver.find_elements_by_xpath('//*[@id]')
	    for ii in ids:
	      #print ii.tag_name
	      try:
		print ii.get_attribute('id')
		if ii.get_attribute('id') == "a-page":
		   page_not_ready = False
		   break
	      except:
		time.sleep(1)	 


	  inputElement = self.driver.find_element_by_name("email")
	  inputElement.send_keys(self.user)
	  inputElement = self.driver.find_element_by_id("ap_password")
	  inputElement.send_keys(self.password)
	  inputElement = self.driver.find_element_by_id("signInSubmit")
	  inputElement.send_keys(Keys.RETURN)


	def __load_history_page(self):
	  page_not_ready=True
	  while(page_not_ready):
	    try:
	      inputElement = self.driver.find_element_by_id("iSettings")
	      inputElement.send_keys(Keys.RETURN)
	      page_not_ready = False
	    except:
	      time.sleep(1)
	 
	  print "settings selected"
	  page_not_ready=True
	  while(page_not_ready):
	    try:
	      element = self.driver.find_element_by_link_text("History")
	      element.click()
	      page_not_ready = False
	    except:
	      time.sleep(1)

	  print "History selected"

	def __process_alexa_history_entries(self):
	  try:
	     ids = self.driver.find_elements_by_xpath('//*[@class]')
	  except:
	    print "waiting for connection"
	    self.exceptions += 1
	    if self.exceptions > 10:
		 return "_Reset"
	    return 0	
	  self.new_history = []
          ndx = 0
	  self.new_event = False
	  for ii in ids:
	    try:
	      #print ii.get_attribute('class')
	      if ii.get_attribute('class') == "dd-title d-dialog-title":
		 text = ii.get_attribute('textContent')
		 #print text
	      if ii.get_attribute('class') == "sub-text":
	 	 time_and_device = ii.get_attribute('textContent')
	 	 tokens = time_and_device.split(" on ",1)
		 # ignore whats heard by other devices 
		 if tokens[1] == self.device:		
			temp_event = event(text,tokens[0],tokens[1])			
			#print temp_event.heard 
  			self.new_history.append(temp_event)
			#print self.new_history[ndx] +" != "+self.history[ndx]
			if self.new_history[ndx] != self.history[ndx]:
				#print "returning early"
				self.new_event = True
				return 
	      self.exceptions = 0
	    except:
	      #print "keep reading history " + time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime())
	      self.exceptions += 1
	    if self.exceptions > 10:
		 return "_Reset"

	




