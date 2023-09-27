# 检测出失效的Cookie，然后将其从存储模块中删除。
# 把失效Cookie删除后，获取模块就会检测到与之对应的账号没有了Cookie信息，继而用此账号重新模拟登录并获取新的Cookie

import requests
from requests.exceptions import ConnectionError
from accountpool.storages.redis import *
from accountpool.exceptions.init import InitException
from loguru import logger

class BaseTester(object):

    def __init__(self, website=None) -> None:
        self.website = website
        if not self.website:
            raise InitException
        self.account_operator = RedisClient(type='account', website=self.website)
        self.credential_operatir = RedisClient(type='credential', website=self.website)

    def test(self, username, credential):
        """测试对应的Cookie是否有效"""
        raise NotImplementedError
    
    def run(self):
        """
        获取所有的cookie并测试
        """
        credentials = self.credential_operatir.all()
        for username, credential in credentials.items():
            self.test(username, credential)


class Antispider6Tester(BaseTester):
    
    def __init__(self, website=None) -> None:
        BaseTester.__init__(self, website)
    
    def test(self, username, credential):
        """
        拿到测试URL，获取Cookie进行模拟登录，如果Cookie无效就删除对应的记录
        """
        logger.info(f'testing credential for {username}')
        try:
            test_url = TEST_URL_MAP[self.website]
            response = requests.get(test_url, headers={
                'Cookie': credential
            }, timeout=5, allow_redirects=False)
            if response.status_code == 200:
                logger.info('credential is valid')
            else:
                logger.info('credential is no valid, delete it')
                self.credential_operatir.delete(username)
        except ConnectionError:
            logger.info('test failed')
            logger.info('credential is no valid, delete it')
            self.credential_operatir.delete(username)
        except Exception as e:
            logger.info(e)
            logger.info('credential is no valid, delete it')
            self.credential_operatir.delete(username)