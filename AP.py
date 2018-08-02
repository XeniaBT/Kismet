#!/usr/bin/python
#  Eingaben im  Terminal: python netxml2csvAP.py Inputdatei.netxml Outputdatei.csv
from lxml import etree
import os
import sys

def run():
    
    if len(sys.argv) != 3:
        print ("Geben Sie die Input.netxml und Output.csv ein:" % sys.argv[0])
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
                print ("Datei '%s' kann nicht geöfnet oder beschreiben werden." % output_file_name)
                exit()

            try:
                doc = etree.parse(input_file_name)
            except:
                print ("Inputfile kann nicht geöfnet werden: '%s'." % input_file_name)
                exit()
                
#            detect_id=input("Geben Sie ein ID der Detection ein: ")
             
            output.write("BSSID,Manuf,Channel,Privacy,Cipher,Auth,Power,ESSID,Cloaked,Type1,Type2,FirstTime,LastTime,Packets,Data,Crypt_data,Lat,Lon,Detect_ID\n")
            result = parse_net_xml(doc, detect_id)
            output.write(result)

def parse_net_xml(doc, detect_id):
    
    
    result = ""

    for network in doc.getiterator("wireless-network"):
#Hier werden die Clients rausgefiltertet, die nach einem AP suchen: wenn type=probe oder ad-hoc     
        type1 = network.attrib["type"]
        channel = network.find('channel').text
        if type1 == "probe":
            continue
    
        firstTime = network.attrib["first-time"]
        lastTime = network.attrib["last-time"]
        bssid = network.find('BSSID').text
        manuf = network.find('manuf').text
               
        encryption = network.getiterator('encryption')
        privacy = ""
        cipher = ""
        auth = ""
        if encryption is not None:
            for item in encryption:
                if item.text.startswith("WEP"):
                    privacy = "WEP"
                    cipher = "WEP"
                    auth = ""
                    break
                elif item.text.startswith("WPA"):
                    if item.text.endswith("PSK"):
                        auth = "PSK"
                    elif item.text.endswith("AES-CCM"):
                        cipher = "CCMP " + cipher
                    elif item.text.endswith("TKIP"):
                        cipher += "TKIP "
                elif item.text == "None":
                    privacy = "OPN"

        cipher = cipher.strip()

        if cipher.find("CCMP") > -1:
            privacy = "WPA2"

        if cipher.find("TKIP") > -1:
            privacy += "WPA"

#   Informationene aus der snr-info auslesen:
        power = network.find('snr-info')
        dbm = ""
        if power is not None:
            dbm = power.find('max_signal_dbm').text
  #          dbm = power.find('last_signal_dbm').text

        if power is not None and int(dbm) > 1:
            dbm = power.find('last_signal_dbm').text

        if power is not None and int(dbm) < 1:
            dbm = power.find('min_signal_dbm').text

#   Informationene aus der SSID auslesen:
        ssid = network.find('SSID')
        essid_text, packets, cloaked, type2 = "", "", "", ""
        if ssid is not None:
            essid_text = str(network.find('SSID').find('essid').text).replace(",",".")
            cloaked = network.find('SSID').find('essid').attrib['cloaked']
        else:
            essid_text = type1
                  
        if ssid is not None:
            packets = network.find('SSID').find('packets').text 
            type2 = network.find('SSID').find('type').text    
            
            
#   Informationene aus der <packets> auslesen:
        packetsinfo = network.find('packets')
        data, crypt_data = "", ""
        if packetsinfo is not None:
            data = packetsinfo.find('data').text
            crypt_data = packetsinfo.find('crypt').text

#   Informationene aus GPS auslesen:         
        gps = network.find('gps-info')
        lat, lon = '', ''
        if gps is not None:
            lat = network.find('gps-info').find('avg-lat').text
            lon = network.find('gps-info').find('avg-lon').text

        result += "%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s\n" % (bssid, manuf,  channel, privacy, cipher, auth, dbm, essid_text, cloaked, type1, type2, firstTime, lastTime, packets, data, crypt_data, lat, lon, detect_id)

    return result

if __name__ == "__main__":
      run()