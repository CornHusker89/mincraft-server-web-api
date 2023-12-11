

import requests
import time

try:
    result = requests.post("https://127.0.0.1:3536/api/start", verify=False)

    print(result.status_code, result.json())
except:
    pass





time.sleep(3)

try:
    result = requests.post("https://127.0.0.1:3536/api/command", json={"command": "kill WAHuskeyFan"}, verify=False)

    print(result.status_code, result.json())
except:
    pass





time.sleep(3)

try:
    result = requests.post("https://127.0.0.1:3536/api/command", json={"command": ["kill WAHuskeyFan", "kill WAHuskeyFan", "kill WAHuskeyFan"]}, verify=False)

    print(result.status_code, result.json())
except:
    pass