import requests
from requests.auth import HTTPBasicAuth
import json
from datetime import datetime

counter=0
path = "./energy.json"

def write_in_json_file(totalLoad, price):
    data = []
    with open(path, 'r') as file:
        data = json.load(file)
        
    date_today = str(datetime.now().month) + "-" + str(datetime.now().year)  

    if len(data) == 0:
        data.append({date_today : {"totalLoad":totalLoad, "cost":price}})
    else:
        for i in range(len(data)):
            if data[i].get(date_today) != None:
                data[i][date_today]["totalLoad"] += totalLoad
                data[i][date_today]["cost"] +=  price
                break
            if i == len(data)-1:
                data.append({date_today : {"totalLoad":totalLoad, "cost":price}})
        
    

    with open(path, 'w') as file:
        json.dump(data, file, indent=4)


#while True:
    #response = requests.get("http://192.168.33.3:80/netio.json", auth=HTTPBasicAuth("netio", "netio"))
    #if response.status_code == 200:
        #data = response.json()
        #totalLoad = float(data["GlobalMeasure"]["totalLoad"])
        #price = totalLoad / 1000 * 0.13
write_in_json_file(10, 10*0.000000036)