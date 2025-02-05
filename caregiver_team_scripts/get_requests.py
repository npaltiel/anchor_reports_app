import os
import xml.etree.ElementTree as ET
from caregiver_team_scripts.asynchronous import async_soap_request

app_name = os.getenv("APP_NAME") 
api_secret = os.getenv("API_SECRET")  
api_key = os.getenv("API_KEY")

app_name = 'ANTH1476'
api_secret = '8d2a50da-b799-4ce1-b780-920203e2edec'
api_key = 'MQAwADIANgA2ADgALQBEAEMANABCADAARQAzADMANgAzAEQANgBDADgARgBFADIAMwA2ADMANQA3AEUAMQA2ADgAOQBBAEQAMQA='

async def get_caregiver_id(caregiver_code):
    payload = f"""<?xml version="1.0" encoding="utf-8"?>
        <soap:Envelope xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xmlns:xsd="http://www.w3.org/2001/XMLSchema" xmlns:soap="http://schemas.xmlsoap.org/soap/envelope/">
          <soap:Body>
            <SearchCaregivers xmlns="https://www.hhaexchange.com/apis/hhaws.integration">
              <Authentication>
                <AppName>{app_name}</AppName>
                <AppSecret>{api_secret}</AppSecret>
                <AppKey>{api_key}</AppKey>
              </Authentication>
              <SearchFilters>
                <CaregiverCode>{caregiver_code}</CaregiverCode>
              </SearchFilters>
            </SearchCaregivers>
          </soap:Body>
        </soap:Envelope>"""
    response_content = await async_soap_request('https://app.hhaexchange.com/integration/ent/v1.8/ws.asmx', payload,
                                                '"https://www.hhaexchange.com/apis/hhaws.integration/SearchCaregivers"')
    root = ET.fromstring(response_content)
    namespace = {'ns1': "https://www.hhaexchange.com/apis/hhaws.integration"}
    caregiver_ids = [elem.text for elem in root.findall('.//ns1:CaregiverID', namespaces=namespace)]
    return int(caregiver_ids[0]) if caregiver_ids else None


async def get_teams():
    payload = f"""<?xml version="1.0" encoding="utf-8"?>
    <soap:Envelope xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xmlns:xsd="http://www.w3.org/2001/XMLSchema" xmlns:soap="http://schemas.xmlsoap.org/soap/envelope/">
      <soap:Body>
        <GetCaregiverTeams xmlns="https://www.hhaexchange.com/apis/hhaws.integration">
          <Authentication>
            <AppName>{app_name}</AppName>
            <AppSecret>{api_secret}</AppSecret>
            <AppKey>{api_key}</AppKey>
          </Authentication>
          <OfficeID>2365</OfficeID>
        </GetCaregiverTeams>
      </soap:Body>
    </soap:Envelope>"""

    response_content = await async_soap_request('https://app.hhaexchange.com/integration/ent/v1.8/ws.asmx', payload,
                                                '"https://www.hhaexchange.com/apis/hhaws.integration/GetCaregiverTeams"')
    root = ET.fromstring(response_content)
    namespaces = {'ns1': 'https://www.hhaexchange.com/apis/hhaws.integration'}
    team_dict = {team.find('ns1:CaregiverTeamName', namespaces).text: team.find('ns1:CaregiverTeamID', namespaces).text
                 for team in root.findall('.//ns1:CaregiverTeam', namespaces)}
    return team_dict


async def get_notification_methods():
    payload = f"""<?xml version="1.0" encoding="utf-8"?>
    <soap:Envelope xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xmlns:xsd="http://www.w3.org/2001/XMLSchema" xmlns:soap="http://schemas.xmlsoap.org/soap/envelope/">
      <soap:Body>
        <GetCaregiverNotificationMethods xmlns="https://www.hhaexchange.com/apis/hhaws.integration">
          <Authentication>
            <AppName>{app_name}</AppName>
            <AppSecret>{api_secret}</AppSecret>
            <AppKey>{api_key}</AppKey>
          </Authentication>
        </GetCaregiverNotificationMethods>
      </soap:Body>
    </soap:Envelope>"""

    response_content = await async_soap_request('https://app.hhaexchange.com/integration/ent/v1.8/ws.asmx', payload,
                                                '"https://www.hhaexchange.com/apis/hhaws.integration/GetCaregiverNotificationMethods"')
    root = ET.fromstring(response_content)
    namespaces = {'ns1': 'https://www.hhaexchange.com/apis/hhaws.integration'}
    notification_methods_dict = {method.find('ns1:CaregiverNotificationMethodName', namespaces).text: method.find(
        'ns1:CaregiverNotificationMethodID', namespaces).text for method in
                                 root.findall('.//ns1:CaregiverNotificationMethod', namespaces)}
    return notification_methods_dict
