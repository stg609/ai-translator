import requests
from model import Model
from utils import LOG


class OpenAIModel(Model):
    __host_url = "https://stream.api2d.net"
    __completions_url = "/v1/completions"
    __chat_completions_url = "/v1/chat/completions"

    def __init__(self, model: str, api_key: str):
        self.model = model

        self.__headers = {
            'Content-Type': 'application/json',
            'Authorization': 'Bearer ' + api_key
        }

    def make_request(self, prompt):
        if self.model == "gpt-3.5-turbo":
            data = {
                "model": self.model,
                "messages": [
                    {"role": "user", "content": prompt}
                ],
                "max_tokens": 20
            }
            response = requests.post(self.__host_url+self.__chat_completions_url, headers=self.__headers, json=data)
            if response.status_code != 200:
                raise Exception(f"请求异常：{response.json()}")

            translation = response.json()["choices"][0]["message"]["content"].strip()
        else:
            data = {
                "model": self.model,
                "prompt": prompt,
                "max_tokens": 150,
                "temperature": 0
            }
            response = requests.post(
                self.__host_url+self.__completions_url, headers=self.__headers, json=data)
            if response.status_code != "200":
                raise Exception(f"请求异常：{response}")
            translation = response.json()["choices"][0]["text"].strip()

        return translation, True
