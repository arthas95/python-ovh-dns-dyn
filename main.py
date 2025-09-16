import ovh
import json
import requests
import asyncio
import telegram
from api import *
from tg import *
# Instantiate the client
client = ovh.Client(
endpoint=endpoint2,
application_key=application_key2,
application_secret=application_secret2,
consumer_key=consumer_key2,
)





def get_public_ipv4():
    try:
        response = requests.get('https://api.ipify.org?format=json')
        response.raise_for_status()
        ip_data = response.json()
        return ip_data['ip']
    except requests.RequestException as e:
        return f"Error: {e}"
    

new_ip=get_public_ipv4()
TTL=300
zones = client.get('/domain/zone')
for z in zones:
    ids = client.get(f'/domain/zone/{z}/record', fieldType='A', subDomain='dyn')
    if ids:
        client.put(f'/domain/zone/{z}/record/{ids[0]}', target=new_ip, ttl=TTL)
        for rid in ids[1:]:
            client.delete(f'/domain/zone/{z}/record/{rid}')
        action = "updated"
    else:
        client.post(f'/domain/zone/{z}/record', fieldType='A', subDomain='dyn', target=new_ip, ttl=TTL)
        action = "created"
    client.post(f'/domain/zone/{z}/refresh')
    
    print(f"{z}: dyn.{z} A {action} -> {new_ip}")
    asyncio.run(connectionbot(f"{z}: dyn.{z} A {action} -> {new_ip}"))
   

