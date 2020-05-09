import random
from source import timeframework

class Doctor:
  
    def __init__(self, server):
        self.server = server
   
    def compute_contagius_window(self):
        """compute number of days from today and add 2 extra days"""
        nr_days= 2 + random.randrange(14)
        return timeframework.ge_today_index()- nr_days
      
    def comunicate_test_result(self, name):
        """tell the client to upload sk"""
        self.server.send_info_to_client(name, {
          'data_type': 'action',
          'action': 'upload',
          'time': self.compute_contagius_window()
        })
        
        
        
    
    