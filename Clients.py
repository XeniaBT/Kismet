#!/usr/bin/python
from lxml import etree
import os
import sys

def run():
    if len(sys.argv) != 3:
        print ("Richtige Reiehnfolge der Parameter: %s input.netxml output.csv" % sys.argv[0])
    else:
        output_file_name = sys.argv[2]
        input_file_name = sys.argv[1]
        
#  Detection-ID nach der XML-Dateiname erstellen      
        detect_id1 = str(input_file_name).strip(".netxml").split('/')
        i = (len(detect_id1) -1)
        detect_id = detect_id1[i]
        
        
        if input_file_name != output_file_name:
            try:                
                output = open(output_file_name, "w")
            except:
                print ("Die CSV-Datei '%s' kann nicht erstellt oder geöffnet werden." % output_file_name)
                exit()

            try:
                doc = etree.parse(input_file_name)
            
            except:
                print ("Dei NETXML-Datei kann nicht geöfnet werden: '%s'." % input_file_name)
                exit()
            
#            detect_id=input("Geben Sie ein ID der Detection ein: ")
            result, clients = parse_net_xml(doc)
            output.write("ClientMAC,Manuf,DetectionID\n")
            for client_list in clients:
                for client in client_list:
                    output.write("%s,%s,%s\n" % (client[0], client[1], detect_id))

def parse_net_xml(doc):
    
    result = ""
    NWtype= ""
    
    total = len(list(doc.getiterator("wireless-network")))
    clients = list()

    for network in doc.getiterator("wireless-network"):
        NWtype = network.attrib["type"]
        bssid = network.find('BSSID').text
 #       ssid = network.find('SSID')
  #      essid_text = ""
  #      if ssid is not None:
  #          essid_text = str(network.find('SSID').find('essid').text).replace(",",".")
            
        c_list = associatedClients(network, NWtype, bssid)
        if c_list is not None:
            clients.append(c_list)

    return result, clients

def associatedClients(network, NWtype, bssid):
    clients = network.getiterator('wireless-client')

    if clients is not None:
        client_info = list()
        for client in clients:
            client_mac = client.find('client-mac').text
            manuf = client.find('client-manuf').text
            if NWtype =="infrastructure" and bssid == client_mac:
                continue
            
           
            c = client_mac, manuf
            client_info.append(c)
                      
        return client_info

if __name__ == "__main__":
      run()