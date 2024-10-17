#!/usr/bin/python3

from urllib.parse import urlencode
import argparse
import json
import requests
import sys

class Contabo:
    def __init__(self, **kwargs) -> None:
        self.__client_id: str     = kwargs.get('clientid', None)
        self.__client_secret: str = kwargs.get('clientsecret', None)
        self.__api_user: str      = kwargs.get('apiuser', None)
        self.__api_password: str  = kwargs.get('apipassword', None)

    def createSnapshot(self, access_token: str, description: str, instanceId: str, name: str) -> bool:
        url = f"https://api.contabo.com/v1/compute/instances/{instanceId}/snapshots"
        data = {
            'name': name,
            'description': description
        }
        headers = {
            'Authorization': f"Bearer {access_token}",
            'x-request-id': '04e0f898-37b4-48bc-a794-1a57abe6aa31',
            'x-trace-id': '123213'
        }
        response = requests.post(url, data=data, headers=headers)
        if response.status_code == 201:
            return True
        else:
            print(response.content)
            return False

    def deleteSnapshot(self, access_token: str, instanceId: str, snapshotId: str) -> bool:
        url = f"https://api.contabo.com/v1/compute/instances/{instanceId}/snapshots/{snapshotId}"
        headers = {
            'Authorization': f"Bearer {access_token}",
            'x-request-id': '04e0f898-37b4-48bc-a794-1a57abe6aa31',
            'x-trace-id': '123213'
        }
        response = requests.delete(url, headers=headers)
        if response.status_code == 204:
            return True
        else:
            print(response.content)
            return False
        
    def getAccessToken(self) -> str:
        url = 'https://auth.contabo.com/auth/realms/contabo/protocol/openid-connect/token'
        data = {
            'client_id': self.__client_id,
            'client_secret': self.__client_secret,
            'username': self.__api_user,
            'password': self.__api_password,
            'grant_type': 'password'
        }
        response = requests.post(url, data=data)
        if response.status_code == 200:
            response_json = json.loads(response.text)
            access_token = response_json.get('access_token')
            return access_token
        else:
            # Error handling if token retrieval fails
            return None

    def getInstanceID(self, access_token: str, hostname: str) -> str:
        url = "https://api.contabo.com/v1/compute/instances"
        headers = {
            'Authorization': f"Bearer {access_token}",
            'x-request-id': '51A87ECD-754E-4104-9C54-D01AD0F83406'
        }
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            instancesData = response.json()
            for item in instancesData["data"]:
                if item['name'] == hostname:
                    return item['instanceId']
            return None
        else:
            # Error handling if token retrieval fails
            return None
 
    def getSnapshots(self, access_token: str, instance: str) -> dict:
        url = f"https://api.contabo.com/v1/compute/instances/{instance}/snapshots"
        headers = {
            'Authorization': f"Bearer {access_token}",
            'Content-Type': 'application/json',
            'x-request-id': '04e0f898-37b4-48bc-a794-1a57abe6aa31',
            'x-trace-id': '123213'
        }
        response = requests.get(url, headers=headers)
        
        if response.status_code == 200:
            snapshots = response.json()
            return snapshots
        else:
            # Error handling if token retrieval fails
            return None

def main():
    parser = argparse.ArgumentParser(description="snapshot organisation")
    parser.add_argument('--clientid', action='store', dest='clientid', default=None, help='client id')
    parser.add_argument('--clientsecret', action='store', dest='clientsecret', default=None, help='client secret')
    parser.add_argument('--apiuser', action='store', dest='apiuser', default=None, help='api user')
    parser.add_argument('--apipassword', action='store', dest='apipassword', default=None, help='api password')
    parser.add_argument('--hostname', action='store', dest='hostname', default=None, help='hostname')
    parser.add_argument('--action', action='store', dest='action', default=None, help='create a snapshot otherwise just show snapshots')
    parser.add_argument('--name', action='store', dest='name', default='daily', help='name of snapshot')
    parser.add_argument('--description', action='store', dest='description', default='daily', help='description of snapshot')
    parser.add_argument('--noofpsnaps', action='store', dest='noofpsnaps', default=2, help='number of possible of snapshots')

    # parse argparse
    options = parser.parse_args()
    clientid: str = options.clientid
    clientsecret: str = options.clientsecret
    apiuser: str = options.apiuser
    apipassword: str = options.apipassword
    hostname: str = options.hostname
    action: str = options.action
    name: str = options.name
    description: str = options.description
    noofpsnaps: int = options.noofpsnaps

    if hostname == None:
        print("parameter hostname is empty")
        sys.exit(1)

    contabo: Contabo = Contabo(clientid=clientid, clientsecret=clientsecret, apiuser=apiuser, apipassword=apipassword)

    accessToken = contabo.getAccessToken()
    
    instanceid = contabo.getInstanceID(access_token=accessToken, hostname=hostname)

    snapshots = contabo.getSnapshots(access_token=accessToken, instance=instanceid)
    snapshotIDs = []

    if action == "create":
        if len(snapshots['data']) == noofpsnaps:
            for snapshot in snapshots["data"]:
                snapshotIDs.append(snapshot["snapshotId"])
                snapshotIDs.sort()
                snapshotID = snapshotIDs[0]
            print("")
            print(f"Deleting snapshot {snapshotID} for instance {instanceid}")
            contabo.deleteSnapshot(access_token=accessToken, instanceId=instanceid, snapshotId=snapshotID)

        contabo.createSnapshot(access_token=accessToken, description=description, instanceId=instanceid, name=name)

        snapshots = contabo.getSnapshots(access_token=accessToken, instance=instanceid)
        snapshotIDs = []
        if snapshots['data']:
            for snapshot in snapshots["data"]:
                print("")
                print("Snapshot ID:", snapshot["snapshotId"])
                print("Name:", snapshot["name"])
                print("Creation date:", snapshot["createdDate"])
    else:
        if snapshots['data']:
            for snapshot in snapshots["data"]:
                print("")
                print("Snapshot ID:", snapshot["snapshotId"])
                print("Name:", snapshot["name"])
                print("Creation date:", snapshot["createdDate"])
        else:
            print("No snapshot avialable")

if __name__ == "__main__":
    main()