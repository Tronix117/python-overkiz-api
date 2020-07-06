""" Python wrapper for the Tahoma API """
import aiohttp

import asyncio
import logging
import time
import hashlib
import math
import random
import json

from .exceptions import *
from .models import *

API_URL = "https://tahomalink.com/enduser-mobile-web/enduserAPI/"  # /doc for API doc


class TahomaClient(object):
    """ Interface class for the Tahoma API """

    def __init__(self, username, password, api_url=API_URL):
        """
        Constructor

        :param username: the username for Tahomalink.com
        :param password: the password for Tahomalink.com
        """

        self.username = username
        self.password = password
        self.api_url = api_url

        self._devices = None

        self.__roles = []

    async def login(self):

        payload = {"userId": self.username, "userPassword": self.password}

        async with aiohttp.ClientSession() as session:
            async with session.post(self.api_url + "login", data=payload) as response:

                result = await response.json()

                # 401
                # {'errorCode': 'AUTHENTICATION_ERROR', 'error': 'Bad credentials'}
                # {'errorCode': 'AUTHENTICATION_ERROR', 'error': 'Your setup cannot be accessed through this application'}
                if response.status == 401:
                    if result["errorCode"] == "AUTHENTICATION_ERROR":

                        if "Too many requests" in result["error"]:
                            print(result["error"])

                        if (
                            "Your setup cannot be accessed through this application"
                            in result["error"]
                        ):
                            print(result["error"])

                        if "Bad credentials" in result["error"]:
                            print(result["error"])

                        print(result["error"])

                        return False  # todo throw error

                # 401
                # {'errorCode': 'AUTHENTICATION_ERROR', 'error': 'Too many requests, try again later : login with xxx@xxx.tld'}
                # TODO Add retry logic on too many requests + for debug, log requests + timespans

                # 200
                # {'success': True, 'roles': [{'name': 'ENDUSER'}]}
                if response.status == 200:
                    if result["success"] == True:
                        self.__roles = result["roles"]
                        self.__cookies = response.cookies

                        return True

                # Temp fallbacks
                print(response.status)
                print(result)

    async def get_devices(self, refresh=False) -> List[Device]:

        if self._devices and refresh == False:
            return self._devices

        cookies = self.__cookies

        # TODO add retry logic for unauthorized? 
        async with aiohttp.ClientSession() as session:
            async with session.get(
                self.api_url + "setup/devices", cookies=cookies
            ) as response:

                result = await response.json()

                # for device in result.items()

                if response.status is 200:
                    devices = [Device(**d) for d in result]
                    self._devices = devices

                    return devices

