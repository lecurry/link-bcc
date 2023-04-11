import sys, json, re
from woutils.woredis import WoRedis

nodePrefix = "wo-bcc/node-"
linkPrefix = "wo-bcc/link-"
edgesPrefix = "wo-bcc/edges-"

initredis = WoRedis()

class DataHandle():
    def tcpReceive(self,tcpreceive):
        """
            tcp接收的请求数据存入redis
            ip+端口对应数据存入redis
        """
        for tcpdata in tcpreceive:
            sip = tcpdata[5]
            if type(tcpdata[5]) == bytes:
                sip = tcpdata[5].decode('utf-8')
            v4ip = re.split(":",str(sip))[-1]
            ipAndPort = str(v4ip) + "-" + str(tcpdata[6])
            linkKey = linkPrefix + ipAndPort
            receivedCom = tcpdata[1].decode("utf-8") 
            if not initredis.get(linkKey):
                initredis.set(linkKey,receivedCom)
            nodeKey = nodePrefix + receivedCom
            if not initredis.get(nodeKey):
                nodejson = {}
                nodejson["id"] = receivedCom
                nodejson["title"] = receivedCom
                nodejson["subTitle"] = str(tcpdata[5]) + ":" + str(tcpdata[6])
                nodejson["mainStat"] = "全部请求:9(暂不实现)"
                nodejson["secondaryStat"] = "关闭请求:4(暂不实现)"
                nodejson["arc__1"] = 5
                nodejson["arc__2"] = 3
                nodejson["arc__3"] = 1
                initredis.set(nodeKey,json.dumps(nodejson,ensure_ascii=False))

    def tcpSend(self,tcpsend):
        """
            tcp请求发起数据存入redis
            ip+端口对应数据存入redis
        """
        for tcpdata in tcpsend:
            ipAndPort = str(tcpdata[3]) + "-" + str(tcpdata[4])
            linkKey = linkPrefix + ipAndPort
            sendCom = tcpdata[1].decode("utf-8") 
            if not initredis.get(linkKey):
                initredis.set(linkKey,sendCom)
            nodeKey = nodePrefix + sendCom
            if not initredis.get(nodeKey):
                nodejson = {}
                nodejson["id"] = sendCom
                nodejson["title"] = sendCom
                nodejson["subTitle"] = str(tcpdata[3]) + ":" + str(tcpdata[4])
                nodejson["mainStat"] = "z全部请求:9(暂不实现)"
                nodejson["secondaryStat"] = "关闭请求:4(暂不实现)"
                nodejson["arc__1"] = 5
                nodejson["arc__2"] = 3
                nodejson["arc__3"] = 1
                initredis.set(nodeKey,json.dumps(nodejson,ensure_ascii=False))
            self.tcpLink(tcpdata)

    def tcpLink(self,tcpdata):
        """
            把服务链路关系数据存入redis
        """
        receiveIpAndPort = tcpdata[5].decode('utf-8') + "-" + str(tcpdata[6])
        linkKey = linkPrefix + receiveIpAndPort
        if initredis.get(linkKey):
            target = initredis.get(linkKey)
        else:
            target = receiveIpAndPort
        sendCom = tcpdata[1].decode('utf-8')
        nodeKey = nodePrefix + target
        if not initredis.get(nodeKey):
            #如果外部服务不存在，便添加一个默认，供画图使用
            nodejson = {
                    "id": target,
                    "title": target,
                    "subTitle": target,
                    "mainStat": "全部请求:9(暂不实现)",
                    "secondaryStat": "关闭请求:4(暂不实现)",
                    "arc__1": 5,
                    "arc__2": 3,
                    "arc__3": 1
                }
            initredis.set(nodeKey,json.dumps(nodejson,ensure_ascii=False))
        targetKey = edgesPrefix + sendCom + "-" + target
        if not initredis.get(targetKey):
            nodejson = {}
            nodejson["id"] = sendCom + "-" + target
            nodejson["source"] = sendCom
            nodejson["target"] = target
            nodejson["mainStat"] = "全部请求:9(暂不实现)"
            nodejson["secondaryStat"] = "关闭请求:4(暂不实现)"
            initredis.set(targetKey,json.dumps(nodejson,ensure_ascii=False))