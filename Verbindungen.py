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
                print ("Die netxml-Datei kann nicht geöfnet werden: '%s'." % input_file_name)
                exit()
#            detect_id=input("Geben Sie ein ID der Detection ein: ")
            result, clients = parse_net_xml(doc)
            output.write("ClientMAC,ClientBSSID,ClientType1,ClientType2,NW_Type, Manuf,Channel,f_y,f_m,f_d,l_y,l_m,l_d,f_h,f_min,f_s,l_h,l_min,l_s,data,crypt,total,ClientPower,ClientESSID,Privacy,Cipher,Auth,Lat,Lon,ClientSSIDliste,DetectionID\n")
        
            for client_list in clients:
                for client in client_list:
                    output.write("%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s\n" % (client[0], client[1], client[2], client[3], client[4], client[5], client[6], client[7], client[8], client[9], client[10], client[11], client[12], client[13], client[14], client[15], client[16], client[17], client[18], client[19], client[20], client[21], client[22], client[23], client[24], client[25],client[26], client[27], client[28], client[29], detect_id))

def parse_net_xml(doc):

    result = ""
    NWtype= ""
    
    total = len(list(doc.getiterator("wireless-network")))
    clients = list()

    for network in doc.getiterator("wireless-network"):
        NWtype = network.attrib["type"]
        bssid = network.find('BSSID').text

        ssid = network.find('SSID')
        essid_text = ""
        if ssid is not None:
#            essid_text = network.find('SSID').find('essid').text
            essid_text = str(network.find('SSID').find('essid').text).replace(",",".")
        
        encryption = network.getiterator('encryption')
        privacy, cipher, auth = "","",""
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

        
                
                
        c_list = associatedClients(network, NWtype, bssid, essid_text, privacy, cipher, auth)
        if c_list is not None:
            clients.append(c_list)

    return result, clients

def associatedClients(network, NWtype, bssid, essid_text, privacy, cipher, auth):
    clients = network.getiterator('wireless-client')
    
    if clients is not None:
        client_info = list()
        for client in clients:
            client_mac = client.find('client-mac').text
#            if NWtype =="infrastructure" and bssid == client_mac:
#                continue
            manuf = client.find('client-manuf').text
            channel = client.find('channel').text 
            ClientType1 = client.attrib['type']
            FirstTimeGlobal = client.attrib['first-time']
            LastTimeGlobal = client.attrib['last-time']
            
# Datum und Uhrzeit splitten:            
            FirstTimeArrya = str(FirstTimeGlobal).split(' ')
            j = (len(FirstTimeArrya) -2)
            FirstTime_g = FirstTimeArrya[j]
            FirstTime = str(FirstTime_g).split(':')
            f_h = FirstTime[0]
            f_min = FirstTime[1]
            f_s = FirstTime[2]
            d1 = str(FirstTimeArrya[1])
            f_d = str(FirstTimeArrya[2])
            f_y = str(FirstTimeArrya[4])
            mon = {"Jan":"01", "Feb":"02", "Mar":"03", "Apr":"04", "May":"05", "Jun":"06", "Jul":"07", "Aug":"08", "Sep":"09", "Oct":"10", "Nov":"11", "Dec":"12" }
            f_m, l_m = "", ""
            if d1 in mon:
                f_m = str(mon[d1])
            
            
            LastTimeArrya = str(LastTimeGlobal).split(' ')
            j = (len(LastTimeArrya) -2)
            LastTime_g = LastTimeArrya[j]
            LastTime = str(FirstTime_g).split(':')
            l_h = FirstTime[0]
            l_min = FirstTime[1]
            l_s = FirstTime[2]
            
            d1 = str(LastTimeArrya[1])
            l_d = str(LastTimeArrya[2])
            l_y = str(LastTimeArrya[4])
            if d1 in mon:
                l_m = str(mon[d1])
#            LastDate = d4+"-"+dd+"-"+d2
            
            
#   ClientType: wenn type=tods und SSID existiert => es ist ein Client, der nach AP sucht           
            ssid = client.find('SSID')
            ClientType2 = ""
            if (ssid is not None):  # and (type == "tods"):
                ClientType2 = client.find('SSID').find('type').text 
                
            
       #     cSSID = ""
       #     ClientSSIDliste = list()
       #     cSSIDliste = ""
       #     if (ssid is not None):
        #        x = client.find('SSID').find('ssid')
        #        y=""
        #        if x is not None:
       #             y = client.find('SSID').find('ssid').text 
       #         ClientSSIDliste.append(y)
       #         cSSIDliste = str(ClientSSIDliste)
            
            
  
 #   clients = network.getiterator('wireless-client')
 #   if clients is not None:
 #       client_info = list()
 #       for client in clients:
  #          client_mac = client.find('client-mac').text

            
            cSSIDliste = ""            
            if ssid is not None:
                ClientSSIDliste = list()
                for n in ssid:
                    x = client.find('SSID').find('ssid')
                    if x is not None:
                        y = client.find('SSID').find('ssid').text 
                        ClientSSIDliste.append(y)
                cSSIDliste = str(ClientSSIDliste)
                cSSIDliste = str(' '.join(str(x) for x in ClientSSIDliste))
            
            
            
       #     ClientSSIDliste = list()
       #     cSSIDliste, cSSIDls = "", ""
       #     if (ssid is not None):
        #        for z in ssid:
       #             x = client.find('SSID').find('ssid')
      #              if x is not None:
      #                   cSSIDliste = client.find('SSID').find('ssid').text 
                   #     cSSIDls = client.find('SSID').find('ssid').text 
                #    cSSIDliste = str(ClientSSIDliste.append(cSSIDls))
                    
            
            frames = client.find('packets')
            date, crypt, total = '','',''
            if frames is not None:
                data = client.find('packets').find('data').text
                crypt = client.find('packets').find('crypt').text
                total = client.find('packets').find('total').text
            
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
                power = client.find('snr-info').find('last_signal_dbm')
            if power is not None:
                client_power = power.text
                c = client_mac, bssid, ClientType1, ClientType2, NWtype, manuf, channel, f_y, f_m, f_d, l_y, l_m, l_d, f_h, f_min, f_s, l_h, l_min, l_s, data, crypt, total, client_power, essid_text, privacy, cipher, auth, lat, lon, cSSIDliste
                client_info.append(c)
                      
        return client_info

if __name__ == "__main__":
      run()