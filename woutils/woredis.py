import redis,json,os 

class WoRedis():
    def __init__(self,host=os.getenv("RedisHost"),port=os.getenv("RedisPort"),pwd=os.getenv("RedisPwd")):
        pool = redis.ConnectionPool(host=host, port=port, password=pwd, decode_responses=True)
        self.r = redis.Redis(connection_pool=pool)
    def set(self,key,val):
        self.r.setex(key, 86400, val)

    def get(self,key):
        return self.r.get(key)

    def prefixList(self,prefix):
        nodekeys = self.r.scan_iter(prefix)
        pipe = self.r.pipeline()
        for onekey in nodekeys:
            pipe.get(onekey)
        dict_list = [json.loads(item) for item in pipe.execute()]
        return dict_list
    
    def getjson(self,key):
        return json.loads(self.get(key))  