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
            detect_id=input("Geben Sie ein ID der Detection ein: ")
            result, clients = parse_net_xml(doc)
            output.write("ClientMAC,Manuf,ClientType1,ClientType2,FirstTime,LastTime,ClientPower,ClientBSSID,ClientESSID,Lat,Lon,DetectionID\n")
            for client_list in clients:
                for client in client_list:
                    output.write("%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s\n" % (client[0], client[1], client[2], client[3], client[4], client[5], client[6], client[7], client[8], client[9], client[10], detect_id))

def parse_net_xml(doc):
    
 #   detection_start=""
 #   detection = doc.find("detection-run").attrib["start-time"]


    result = ""
    type= ""
    
    total = len(list(doc.getiterator("wireless-network")))
    clients = list()

    for network in doc.getiterator("wireless-network"):
        type = network.attrib["type"]
        bssid = network.find('BSSID').text

        ssid = network.find('SSID')
        essid_text = ""
        if ssid is not None:
            essid_text = network.find('SSID').find('essid').text

            
        c_list = associatedClients(network, bssid, essid_text)
        if c_list is not None:
            clients.append(c_list)

    return result, clients

def associatedClients(network, bssid, essid_text):
    clients = network.getiterator('wireless-client')

    if clients is not None:
        client_info = list()
        for client in clients:
            client_mac = client.find('client-mac').text
            manuf = client.find('client-manuf').text
            ClientType1 = client.attrib['type']
            FirstTime = client.attrib['first-time']
            LastTime = client.attrib['last-time']
            
#   FirstTime und LastTime muss man nocht spliten in Data und Time damit die Zeitfunktion in Neo4j möglich ist.
#   ClientType: wenn type=tods und SSID existiert => es ist ein Client, der nach AP sucht           
            ssid = client.find('SSID')
            ClientType2 = ""
            if (ssid is not None):  # and (type == "tods"):
                ClientType2 = client.find('SSID').find('type').text 
#           else: ClientType = "ConectedClient"

            gps = client.find('gps-info')
            lat, lon = '', ''
            if gps is not None:
                lat = client.find('gps-info').find('avg-lat').text
                lon = client.find('gps-info').find('avg-lon').text


 #           if mac is not None:
 #               client_mac = mac.text
 #               if client_mac == bssid:
 #                   continue  
                snr = client.find('snr-info')
                if snr is not None:
                    power = client.find('snr-info').find('max_signal_dbm')
                    if power is not None:
                        client_power = power.text
                        c = client_mac, manuf, ClientType1, ClientType2, FirstTime, LastTime, client_power, bssid, essid_text, lat, lon
                        client_info.append(c)
                      
        return client_info

if __name__ == "__main__":
      run()
