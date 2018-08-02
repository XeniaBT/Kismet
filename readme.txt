1.
netxml-Datei parsen

Accesspoint.csv erstellen:
python netxml2csvAP.py kismet.netxml Accesspoint.csv

Client.csv erstellen:
python netxml2csvClient.py kismet.netxml Client.csv

Verbindungen.csv erstellen:
python netxml2csvVerbindungen.py kismet.netxml Verbindugen.csv


2.
In Neo4j-Desktop -- > Settings   ||   in der Configurationsdatei:  config:       /Users/.../Library/Application Support/Neo4j Desktop/Application/neo4jDatabases/database-.../installation-3.4.0/conf
 
#   dbms.directories.import=import     <--   diese Zeile auskommentieren
dbms.security.allow_csv_import_from_file_urls=true    <-- diese Zeile einfügen



----------

// Create Clients
LOAD CSV WITH HEADERS FROM 'file:/Users/Ksenia/Documents/Wings/Masterarbeit/netxml2csv/Client.csv' AS nodes 
MERGE (:Client {cMAC: nodes.ClientMAC, cManuf: nodes.Manuf, cDetectionID: nodes.DetectionID})

// Create Verbindung
LOAD CSV WITH HEADERS FROM 'file:/Users/Ksenia/Documents/Wings/Masterarbeit/netxml2csv/Verbindungen.csv' AS nodes 
CREATE (:Verbindung {vMAC: nodes.ClientMAC, vBSSID: nodes.ClientBSSID, NW_Type: nodes.NW_Type, vType1: nodes.ClientType1, vType2: nodes.ClientType2, Pover:nodes.ClientPower, Data:nodes.data, Crypt:nodes.crypt, Total:nodes.total, Privacy:nodes.Privacy, Cipher:nodes.Cipher, Auth:nodes.Auth, vDetectionID: nodes.DetectionID, locationC: point({latitude:toFloat(nodes.Lat), longitude:toFloat(nodes.Lon)}), vFirstTime:datetime({year:toInt(nodes.f_y), month:toInt(nodes.f_m), day:toInt(nodes.f_d), hour:toInt(nodes.f_h), minute:toInt(nodes.f_min), second:toInt(nodes.f_s)}), vLastTime:datetime({year:toInt(nodes.l_y), month:toInt(nodes.l_m), day:toInt(nodes.l_d), hour:toInt(nodes.l_h), minute:toInt(nodes.l_min), second:toInt(nodes.l_s)})})

// Create Detection
LOAD CSV WITH HEADERS FROM 'file:/Users/Ksenia/Documents/Wings/Masterarbeit/netxml2csv/Client.csv' AS nodes 
MERGE (:Detection {DetectionID: nodes.DetectionID})

// Create Accesspoints
LOAD CSV WITH HEADERS FROM 'file:/Users/Ksenia/Documents/Wings/Masterarbeit/netxml2csv/AP.csv' AS nodes MERGE (:Accesspoint {apBSSID: nodes.BSSID, apESSID: nodes.ESSID, apManuf: nodes.Manuf, apDetectionID: nodes.Detect_ID})

// Create Relationship Clients -->Verbindungen
MATCH (c:Client), (v:Verbindung) WHERE c.ClienMAC = v.vMAC CREATE (c)-[:Csends{CsendsType1:v.vType1, CsendsType2:v.vType2, CsendsCrypt:v.Crypt, CsendsData:v.Data, Cvon:v.vFirstTime, Cbis:v.vLastTime}]->(v)

// Create Relationship Accesspoints -->Verbindungen
MATCH (a:Accesspoint), (v:Verbindung) WHERE a.apBSSID = v.vBSSID CREATE (a)-[:APsends{APsendsType1:v.vType1, APsendsType2:v.vType2, APsendsCrypt:v.Crypt, APsendsData:v.Data, APvon:v.vFirstTime, APbis:v.vLastTime}]->(v)

// Create Rel Det-Client
MATCH (c:Client)-[s:Csends]-(v:Verbindung), (d:Detection)-[:detected_V]-(vb:Verbindung) WHERE v.vMAC=vb.vMAC MERGE (d)-[:detected_C]->(c)

// Create Rel Det-AP
MATCH (a:Accesspoint)-[s:APsends]-(v:Verbindung), (d:Detection)-[:detected_V]-(vb:Verbindung) WHERE v.vBSSID=vb.vBSSID MERGE (d)-[:detected_AP]->(a)

Filtern:

//Alle nicht verbundene Clients aus Detections 1234 oder 5678
MATCH (c:Client)-[r:Csends]->(v:Verbindung) WHERE v.vType2="Probe Request" AND (v.vDetectionIDverb="1234" OR v.vDetectionIDverb="5678")  RETURN c,r,v

MATCH (v:Verbindung{NW_Type:"probe"}), (c:Client)-[s:seenC]-(d:Detection) WHERE v.vMAC = c.cMAC AND v.vDetectionID CONTAINS "Loc1" RETURN distinct c, s, d

// Alle nicht verbundene Clients aus einer Messung
MATCH (v:Verbindung{NW_Type:"probe",vDetectionID:"23Juni_Loc1" }) RETURN v

// Nicht verbundener Client: bei welchen messungen war er dabei?
MATCH (v1:Verbindung{NW_Type:"probe", vDetectionID:"24Juni_Loc1"})-[r:Csends]-(c:Client)-[s:detected_C]-(d:Detection), (v:Verbindung)
WHERE c.cMAC IN v.vMAC
RETURN v1, r, c, d, s

// Clients, die von 18:00 und 19:00 erfass wurden
MATCH (v:Verbindung)-[]-(c:Client)-[r:detected_C]-(d:Detection)
WHERE dateTime("2018-06-24T18:50:55") < v.vFirstTime < dateTime("2018-06-24T19:50:55")
RETURN c, d


MATCH (v:Verbindung)-[r:Csends]-(c:Client)-[s:detected_C]-(d:Detection) with c, count(*) as x
WHERE  x = 6
RETURN   c
----------

7. AP in der bestimmter Position

match (a:Accesspoint)
where distance(a.location, point({longitude:-103.844577, latitude:-84.288353}) < 100 return a


