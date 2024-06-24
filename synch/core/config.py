from dotenv import dotenv_values, find_dotenv
from collections import OrderedDict


if not find_dotenv():
    exit()

config = OrderedDict(
    (k.lower(), v) for k, v in dotenv_values(".env", encoding="utf-8").items()
)
