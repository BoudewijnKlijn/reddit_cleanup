import os
import sys
import time

import requests
import requests.auth
from dotenv import load_dotenv

load_dotenv()

AGENT_NAME = f"personal-bot/0.1 by {os.environ['REDDIT_USERNAME']}"
BASE_URL = "https://oauth.reddit.com"
USER = os.environ["REDDIT_USERNAME"]


class Connection:
    def __init__(self):
        self.agent_name = f"personal-bot/0.1 by {os.environ['REDDIT_USERNAME']}"
        self.rate_limit_remaining = None
        self.rate_limit_used = None
        self.rate_limit_reset = None
        self.token = self.get_token()
        self.last_request_response = None
        self.headers = {
            "Authorization": f"bearer {self.token}",
            "User-Agent": AGENT_NAME,
        }

    def __str__(self):
        try:
            return (
                # f"{self.agent_name=}, {self.token=}, {self.last_request_response=}, "
                f"{self.rate_limit_used=}, {self.rate_limit_remaining=}, {self.rate_limit_reset=}"
            )
        except AttributeError as e:
            print(e)
            return f"{self.agent_name=}"

    def get_token(self):
        client_auth = requests.auth.HTTPBasicAuth(
            os.environ["CLIENT_ID"], os.environ["CLIENT_SECRET"]
        )
        post_data = {
            "grant_type": "password",
            "username": os.environ["REDDIT_USERNAME"],
            "password": os.environ["REDDIT_PASSWORD"],
        }
        headers = {"User-Agent": self.agent_name}
        response = self.post_request(
            url="https://www.reddit.com/api/v1/access_token",
            auth=client_auth,
            data=post_data,
            headers=headers,
        )
        return response.json().get("access_token")

    def update_connection(self):
        self.rate_limit_remaining = int(
            float(self.last_request_response.headers.get("x-ratelimit-remaining", 1))
        )
        self.rate_limit_reset = int(
            float(self.last_request_response.headers.get("x-ratelimit-reset", 600))
        )
        self.rate_limit_used = int(
            float(self.last_request_response.headers.get("x-ratelimit-used", 0))
        )

    def is_request_allowed(self):
        if self.rate_limit_remaining is not None and self.rate_limit_remaining <= 0:
            sleep_time = self.rate_limit_reset
            print(f"{sleep_time=}")
            time.sleep(sleep_time)

    def before_request(self):
        self.is_request_allowed()

    def after_request(self, response):
        self.last_request_response = response
        self.update_connection()
        if self.last_request_response.status_code != 200:
            sys.exit(
                f"ERROR: Status code != 200. {self.__str__()}. {self.last_request_response.headers}"
            )
        print(self.__str__())

    def post_request(self, **kwargs):
        self.before_request()
        response = requests.post(**kwargs)
        self.after_request(response)
        return response

    def get_request(self, **kwargs):
        self.before_request()
        response = requests.get(**kwargs)
        self.after_request(response)
        return response
