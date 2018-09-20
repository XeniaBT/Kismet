## KISMET to Neo4j

1. netxml-Datein parsen

        Accesspoint.csv erstellen:
        python netxml2csvAP.py kismet.netxml Accesspoint.csv

        Client.csv erstellen:
        python netxml2csvClient.py kismet.netxml Client.csv

        Verbindungen.csv erstellen:
        python netxml2csvVerbindungen.py kismet.netxml Verbindugen.csv


2. Configurationsdatei ändern:

    Schritt 1: Neo4j-Datenbenk starten. Damit wird die Logdatei erstellt.
    Schritt 2: Die Datenbank stipen. Gehen auf "Manage" --> "Logs". Hier den config-Pfad kopieren und im Text-Editor öffnen. Im Ordener "conf" die Datei "neo4j.conf" öffene.
    Schritt 3: In der neo4j.conf - Datei folgendes änden:

        #   dbms.directories.import=import     <--   diese Zeile auskommentieren ("#"-Zeichen setzen)
            dbms.security.allow_csv_import_from_file_urls=true    <-- diese Zeile suchen und "#"-Zeichen entfernen



----------

3. Neo4j Datenbank erstellen (Die Reienfolge beachten):

        // Create Clients
        LOAD CSV WITH HEADERS FROM 'file:/Users/Ksenia/Documents/Wings/Masterarbeit/netxml2csv/Client.csv' AS nodes 
        MERGE (:Client {cMAC: nodes.ClientMAC, cManuf: nodes.Manuf, cDetectionID: nodes.DetectionID})

        // Create Verbindung
        LOAD CSV WITH HEADERS FROM 'file:/Users/Ksenia/Documents/Wings/Masterarbeit/netxml2csv/Verbindungen.csv' AS nodes 
        CREATE (:Verbindung {vMAC: nodes.ClientMAC, vBSSID: nodes.ClientBSSID, ProbeSSID: nodes.ClientSSIDs, NW_Type: nodes.NW_Type, vType1: nodes.ClientType1, vType2: nodes.ClientType2, Pover:nodes.ClientPower, Data:nodes.data, Crypt:nodes.crypt, Total:nodes.total, Privacy:nodes.Privacy, Cipher:nodes.Cipher, Auth:nodes.Auth, vDetectionID: nodes.DetectionID, locationC: point({latitude:toFloat(nodes.Lat), longitude:toFloat(nodes.Lon)}), vFirstTime:datetime({year:toInt(nodes.f_y), month:toInt(nodes.f_m), day:toInt(nodes.f_d), hour:toInt(nodes.f_h), minute:toInt(nodes.f_min), second:toInt(nodes.f_s)}), vLastTime:datetime({year:toInt(nodes.l_y), month:toInt(nodes.l_m), day:toInt(nodes.l_d), hour:toInt(nodes.l_h), minute:toInt(nodes.l_min), second:toInt(nodes.l_s)})})

        // Create Detection
        LOAD CSV WITH HEADERS FROM 'file:/Users/Ksenia/Documents/Wings/Masterarbeit/netxml2csv/Client.csv' AS nodes 
        MERGE (:Detection {DetectionID: nodes.DetectionID})

        // Create Accesspoints
        LOAD CSV WITH HEADERS FROM 'file:/Users/Ksenia/Documents/Wings/Masterarbeit/netxml2csv/AP.csv' AS nodes MERGE (:Accesspoint {apBSSID: nodes.BSSID, apESSID: nodes.ESSID, apManuf: nodes.Manuf, apDetectionID: nodes.Detect_ID})

        // Create Relationship Detection —> Verbindung
        MATCH (d:Detection), (v:Verbindung) WHERE d.DetectionID = v.vDetectionID CREATE (d)-[:detected_V]->(v)

        // Create Relationship Accesspoints —> Verbindungen
        MATCH (a:Accesspoint), (v:Verbindung) WHERE a.apBSSID = v.vBSSID CREATE (a)-[:APsends{APsendsType1:v.vType1, APsendsType2:v.vType2, APsendsCrypt:v.Crypt, APsendsData:v.Data, APvon:v.vFirstTime, APbis:v.vLastTime}]->(v)

        // Create Relationship Clients —> Verbindungen
        MATCH (c:Client), (v:Verbindung) WHERE c.cneoMAC = v.vMAC CREATE (c)-[:Csends{CsendsType1:v.vType1, CsendsType2:v.vType2, CsendsCrypt:v.Crypt, CsendsData:v.Data, Cvon:v.vFirstTime, Cbis:v.vLastTime}]->(v)

        // Create Relationship Detection —> Client
        MATCH (c:Client)-[s:Csends]-(v:Verbindung), (d:Detection)-[:detected_V]-(vb:Verbindung) WHERE v.vMAC=vb.vMAC MERGE (d)-[:detected_C]->(c)

        // Create Relationship Detection —> AP
        MATCH (a:Accesspoint)-[s:APsends]-(v:Verbindung), (d:Detection)-[:detected_V]-(vb:Verbindung) WHERE v.vBSSID=vb.vBSSID MERGE (d)-[:detected_AP]->(a)



4. Beispiele für die Filtern:

        // Alle nicht verbundenen Clients aus Detections 1234 oder 5678
        MATCH (c:Client)-[r:Csends]->(v:Verbindung) WHERE v.vType2="Probe Request" AND (v.vDetectionIDverb="1234" OR v.vDetectionIDverb="5678")  RETURN c,r,v

        // Clients, die von 18:00 und 19:00 erfasst wurden
        MATCH (v:Verbindung)-[]-(c:Client)-[r:detected_C]-(d:Detection)
        WHERE dateTime("2018-06-24T18:50:55") < v.vFirstTime < dateTime("2018-06-24T19:50:55")
        RETURN c, d

        // Alle Messungen und dabei erfasse Clients anzeigen: 
        MATCH (d:Detection)-[r:detected_C]-(c:Client)
        RETURN  * LIMIT 300

        // Client, der in allen Messungen (hier 4 Messungen) vorkommt. SIZE = Anzahl der Messungen
        MATCH (d:Detection),(c:Client)--(v:Verbindung{NW_Type:"probe"})
        WHERE NOT c.cManuf="Unknown" AND size((c)-[:detected_C]-()) =4
        RETURN  d, c

        // Nicht verbundene Clients, die NUR in einer Messung vorkommen:
        MATCH (d:Detection),(c:Client)--(v:Verbindung{NW_Type:"probe"})
        WHERE NOT c.cManuf="Unknown" AND size((c)-[:detected_C]-()) = 1
        RETURN  d, c

        // Alle Clinets im Umkreis von 100m
        MATCH (v:Verbindung)-[]-(c:Client)
        WHERE distance(v.locationC, point({latitude:48.839809, longitude:9.323862})) < 100 AND NOT c.cManuf="Unknown" 
        RETURN c
