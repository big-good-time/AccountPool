# 定义一个web接口，爬虫访问此接口便可以获取随机的Cookie

import json
from flask import Flask, g
from accountpool.processors.generator import RedisClient
from loguru import logger
app = Flask(__name__)

account = 'account'
credential = 'credential'

GENERATOR_MAP = {
    'antispider6', 'Antispider6Generator'
}

@app.route('/')
def index():
    return '<h2>Welcome to Cookie Pool System</h2>'

def get_conn():
    for website in GENERATOR_MAP:
        if not hasattr(g, website):
            setattr(g, f'{website}_{credential}', RedisClient(credential, website))
            setattr(g, f'{website}_{account}', RedisClient(account, website))
    return g

@app.route('/<website>/random')
def random(website):
    g = get_conn()
    result = getattr(g, f'{website}_{credential}').random()
    logger.debug(f'get credential {result}')
    return result