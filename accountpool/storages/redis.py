import random, redis
from accountpool.settings import *

class RedisClient(object):
    def __init__(self, type, website, host=REDIS_HOST, port=REDIS_PORT, password=REDIS_PASSWORD):
        """
        初始化redis连接
        :type 类型
        :website 网站
        由类型:网站组成一个Hash名一共有两个账号和cookie
        """
        self.db = redis.StrictRedis(host=host, port=port, password=password, decode_responses=True)
        self.type = type
        self.website = website

    def name(self):
        """
        返回Hash名称
        """
        return f'{self.type}:{self.website}'
    
    def set(self, username, value):
        """
        设置Hash里面的数据
        :username
        :value
        """
        return self.db.hset(self.name(), username, value)
    
    def get(self, username):
        """
        获取值
        :username
        """
        return self.db.hget(self.name(), username)
    
    def delete(self, username):
        """
        删除值
        :username
        """
        return self.db.hdel(self.name(), username)
    
    def count(self):
        """
        获取有多少条数据
        """
        return self.db.hlen(self.name())
    
    def random(self):
        """
        随机取一个值
        """
        return random.choice(self.db.hvals(self.name()))
    
    def usernames(self):
        """
        获取所有的键
        """
        return self.db.hkeys(self.name())
    
    def all(self):
        """
        获取所有的数据
        """
        return self.db.hgetall(self.name())