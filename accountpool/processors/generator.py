from accountpool.exceptions.init import InitException
from accountpool.storages.redis import RedisClient
from loguru import logger
import requests

class BaseCenerator(object):

    def __init__(self, website=None) -> None:
        self.website = website
        if not self.website:
            raise InitException
        self.account_operator = RedisClient(type='account', website=self.website)
        self.credential_operator = RedisClient(type='credential', website=self.website)
    
    def generate(self, username, password):
        """
        接收用户名和密码并生成Cookie
        """
        raise NotImplementedError
    
    def init(self):
        """
        在运行开始之前做一些准备工作，子类可以选择性复写
        """
        pass

    def run(self):
        """
        查找哪些还没有cookie的账号获取cookie
        """
        self.init()
        logger.debug('start on run generator')
        for username, password in self.account_operator.all().items():
            if self.credential_operator.get(username):
                continue
            logger.debug(f'start to generate credential of {username}')
            self.generate(username=username, password=password)


class Antispider6Generator(BaseCenerator):
    def generate(self, username, password):
        """
        根据账号密码模拟登录获取cookie并存储
        """
        if self.credential_operator.get(username):
            logger.debug(f'credential of {username} exists, skip')
            return
        login_url = 'https://antispider6.scrape.center/login'
        s = requests.Session()
        try:
            s.post(login_url, data={
                'username': username,
                'password': password
            })
            result = []
            for cookie in s.cookies:
                print(cookie.name, cookie.value)
                result.append(f'{cookie.name}={cookie.value}')
            result = ';'.join(result)
            logger.debug(f'get credential {result}')
            self.credential_operator.set(username, result)
        except Exception as e:
            logger.error(e)