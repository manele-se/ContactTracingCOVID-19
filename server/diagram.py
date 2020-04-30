
# Generates the simulation server architecture diagrams
# 
# To run, first install these Python modules:
#  - diagrams
#  - napkin
#  - plantuml
# Also install GraphViz
# On Mac, this is done like this:
# brew install graphviz
# pip3 install napkin
# pip3 install plantuml
# pip3 install diagrams
#
# https://diagrams.mingrammer.com/docs/getting-started/examples
# https://github.com/pinetr2e/napkin/blob/master/DEMO_EXAMPLES.md

from diagrams import Diagram, Cluster
from diagrams.aws.compute import EC2
from diagrams.aws.network import APIGateway, AppMesh, DirectConnect
from diagrams.azure.mobile import AppServiceMobile
from diagrams.onprem.client import Client
import napkin

def generate_architecture_diagram():
  # Use a much higher resolution than default

  graph_attr = {
    'dpi': '240'
  }

  with Diagram("", show=False, direction="TB", graph_attr=graph_attr, filename="simulation_server"):
    with Cluster(""):
      with Cluster(""):
        www = APIGateway("WWW")
        ws = DirectConnect("WebSocket")
      
      udp = AppMesh("UDP")
      server = EC2("Server")
      
      server - [udp, www, ws]
    
    browser = Client("Browser")
    
    www >> browser
    ws >> browser
    ws << browser
    
    device = AppServiceMobile("Device")
    udp >> device
    udp << device

@napkin.seq_diagram()
def device_sends_broadcast(c):
  app = c.object('sender', cls='TracingApp')
  advertiser = c.object('BluetoothLeAdvertiser')
  client = c.object('udp1', cls='UdpClient')
  server = c.object('Server')
  client2 = c.object('udp2', cls='UdpClient')
  scanner = c.object('BluetoothLeScanner')
  app2 = c.object('receiver', cls='TracingApp')
  
  with app:
    with advertiser.start_advertising("token"):
      with c.loop('forever'):
        with client.send():
          udp_packet = getattr(server, 'UDP DATAGRAM')
          with udp_packet():
            with server.handle_incoming_broadcast():
              server.get_devices_near('sender')
              with c.loop('for every device'):
                udp_packet2 = getattr(client2, 'UDP DATAGRAM')
                with udp_packet2():
                  with scanner.receive():
                    with app2.callback("token"):
                      app2.add_heard_token("token")

if __name__ == '__main__':
  generate_architecture_diagram()
  napkin.generate(output_format='plantuml_png', output_dir='.')


