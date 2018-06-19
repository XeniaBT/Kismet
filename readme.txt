1.
netxml-Datei parsen

Accesspoint.csv erstellen:
python netxml2csvAP.py kismet.netxml Accesspoint.csv

Client.csv erstellen:
python netxml2csvClient.py kismet.netxml Client.csv

2.
In Neo4j-Desktop -- > Settings   ||   in der Configurationsdatei:  config:       /Users/.../Library/Application Support/Neo4j Desktop/Application/neo4jDatabases/database-.../installation-3.4.0/conf
 
# dbms.directories.import=import     <--   diese Zeile auskommentieren
dbms.security.allow_csv_import_from_file_urls=true    <-- diese Zeile einfügen


3. 
Accesspoint.csv in neo4j laden:

// Load AP
LOAD CSV WITH HEADERS FROM 'file:/Users/Ksenia/Documents/Wings/Masterarbeit/netxml2csv/AP.csv' AS nodes CREATE (:Accesspoint {BSSID: nodes.BSSID, Manuf: nodes.Manuf, Channel: nodes.Channel, Privacy: nodes.Privacy, Cipher: nodes.Cipher, Auth: nodes.Auth, Power: nodes.Power, ESSID: nodes.ESSID, Cloaked: nodes.Cloaked, Type: nodes.Type, FirstTime: nodes.FirstTime, LastTime: nodes.LastTime, Packets: nodes.Packets, Data: nodes.Data, Crypt_data: nodes.Crypt_data, locationAP: point({latitude:toFloat(nodes.Lat), longitude:toFloat(nodes.Lon)})})


4.
Client.csv in neo4j laden:

// 2. Load Clients
LOAD CSV WITH HEADERS FROM 'file:/Users/Ksenia/Documents/Wings/Masterarbeit/netxml2csv/Client.csv' AS nodes CREATE (:Client { ClientMAC: nodes.ClientMAC, ClientManuf: nodes.Manuf, ClientType: nodes.ClientType, ClientFirstTime: nodes.FirstTime, ClientLastTime: nodes.LastTime, ClientPower: nodes.ClientPower, ClientBSSID: nodes.ClientBSSID, ClientESSID: nodes.ClientESSID, locationC: point({latitude:toFloat(nodes.Lat), longitude:toFloat(nodes.Lon)})})

5.
Beziehungen zwischen den Accesspoints und Clients erstellen:

// 3. Relationship between AP and Clients
MATCH (a:Accesspoint), (c:Client) WHERE a.BSSID=c.ClientBSSID CREATE (a)-[r:conected {von:c.ClientFirstTime, bis:c.ClientLastTime}]->(c) RETURN a, c, r

6. 

Client.csv in neo4j laden:

// Load Location
LOAD CSV WITH HEADERS FROM 'file:/Users/Ksenia/Documents/Wings/Masterarbeit/netxml2csv/Client.csv' AS nodes CREATE (:Location { LocMAC: nodes.ClientMAC,  LocBSSID: nodes.ClientBSSID, LocESSID: nodes.ClientESSID, LocPoint: point({latitude:toFloat(nodes.Lat), longitude:toFloat(nodes.Lon)})})


7. 

// Relationship between Location and AP
MATCH (a:Accesspoint), (l:Location) WHERE a.BSSID=l.LocBSSID CREATE (l)-[r:located {von:a.FirstTime, bis:a.LastTime}]->(a) RETURN a, l, r


7. AP in der bestimmter Position

match (a:Accesspoint)
where distance(a.location, point({longitude:-103.844577, latitude:-84.288353}) < 100 return a


