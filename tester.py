#!/usr/bin/env python

import httplib
from xml.dom import minidom
import sys
import time

STATION_XML = """<?xml version="1.0" encoding="iso-8859-1"?>
<ReqC ver="1.1" prod="iRail" lang="EN">
<LocValReq id="FROM" maxNr="1">
<ReqLoc match="%s" type="ST"/>
</LocValReq>
<LocValReq id="TO" maxNr="1">
<ReqLoc match="%s" type="ST"/>
</LocValReq>
</ReqC>"""

SCHEDULE_XML = """<?xml version="1.0" encoding="iso-8859-1"?>
<ReqC ver="1.1" prod="iRail" lang="EN">
<ConReq>
<Start min="10">
<Station externalId="%s" distance="0">
</Station>
<Prod prod="1111111111111111">
</Prod>
</Start>
<Dest min="10">
<Station externalId="%s" distance="0">
</Station>
</Dest>
<Via>
</Via>
<ReqT time="%s" date="%s" a="0">
</ReqT>
<RFlags b="0" f="6">
</RFlags>
<GISParameters>
<Front>
</Front>
<Back>
</Back>
</GISParameters>
</ConReq>
</ReqC>
"""



def make_request(xmlstring):
    headers = {"Content-type": "application/x-www-form-urlencoded",
               "Accept": "text/plain"}
    conn = httplib.HTTPConnection("hari.b-rail.be:80")
    conn.request("POST", "/Hafas/bin/extxml.exe", xmlstring, headers)
    response = conn.getresponse()
    return response.read()

def now():
    timestruct = time.localtime()
    timestamp = "%s:%s" % (timestruct.tm_hour, timestruct.tm_min)
    day = "%s%s%s" % (timestruct.tm_year, timestruct.tm_mon, timestruct.tm_mday)
    return timestamp, day

def find_stations(doc):
    to_station_id, from_station_id = -1, -1
    lvrs = doc.getElementsByTagName("LocValRes")
    for lvr in lvrs:
        st = lvr.getElementsByTagName("Station")[0]
        ext = st.getAttribute("externalId")
        name = st.getAttribute("name")
        print "found externalId for station %s: %s" %(name, ext)
        st_type = lvr.getAttribute("id")
        if st_type == "TO":
            to_station_id = ext
        else:
            from_station_id = ext
    return from_station_id, to_station_id


def main():
    if len(sys.argv) != 3:
        print "usage tester.py <from_station_name> <to_station_name>"
        sys.exit(1)
    from_station_name = sys.argv[1]
    to_station_name = sys.argv[2]
    xmlquery = STATION_XML % (from_station_name, to_station_name)
    data = make_request(xmlquery)

    doc = minidom.parseString(data)
    print doc.toxml()

    from_station_id, to_station_id = find_stations(doc)
    tstamp, day = now()
    body = SCHEDULE_XML % (from_station_id, to_station_id, tstamp, day)

    data = make_request(body)
    print data


if __name__ == "__main__":
    main()
