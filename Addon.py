import subprocess
from mitmproxy import http
import json
import os
class Addon:
    def __init__(self):
            self.captured = False

    def response(self,flow):
        if str(flow.request.url) == "https://cpapp.1lesson.cn/api/user/acquireOpenId":
            response = flow.response
            response_data = json.loads(str(response.text))
            print(response_data)
            self.captured = True
            print("捕捉到为："+response_data['data']['userId'])
            with open("userId.txt", "w") as file:
                file.write(response_data['data']['userId'])
            os.unsetenv('HTTP_PROXY')
            os.unsetenv('HTTPS_PROXY')
            exit()
addons = [
    Addon()
]