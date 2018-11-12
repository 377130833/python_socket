import websocket 
try:
    import thread
except ImportError:
    import _thread as thread
import time
import json
import random
import hmac
import base64
import hashlib
import socket


#数据类型编码(默认的编码函数很多数据类型都不能编码,自定义一个encoder去继承jsonencoder)
class MyEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, bytes):
            return str(obj, encoding='utf-8');
        return json.JSONEncoder.default(self, obj)

def get_sign(secret_key, message):
    h = hmac.new(bytes(secret_key,'utf-8'), bytes(message,'utf-8'), hashlib.sha512)
    return base64.b64encode(h.digest())

def on_message(ws, message):
    print(message)

def on_error(ws, error):
    print(error)

def on_close(ws):
    print("websocket.WebSocketApp reConnect......")
    #断线重连
    start_open()

#私有鉴权接口
def on_open(ws):
    def run(*args):
        nonce = int(time.time() * 1000)
        id = random.randint(0,99999)
        signature = get_sign('your_secret', str(nonce))
        data={ 'id' : id, 'method' : 'server.sign' , 'params' : [your_key, signature, nonce]}
        js=json.dumps(data,cls=MyEncoder)
        ws.send(js)
        #鉴权完成之后进行其他操作
        time.sleep(3)
        data = {"id": id, "method": "order.subscribe", "params": ["DOGE_USDT","OCN_USDT"]}
        js=json.dumps(data,cls=MyEncoder)
        ws.send(js)
    thread.start_new_thread(run, ())

#公共接口
def on_public(ws):
    def run(*args):
        id = random.randint(0,99999)
        data={"id": id, "method": "depth.subscribe", "params": ["ETH_USDT", 5, "0.0001"]}
        js=json.dumps(data,cls=MyEncoder)
        ws.send(js)
        #可订阅更多接口
        time.sleep(3)
        data={"id": id, "method": "trades.subscribe", "params": ["ETH_USDT","BTC_USDT"]}
        js=json.dumps(data,cls=MyEncoder)
        ws.send(js)
    thread.start_new_thread(run, ())

def start_open():
    websocket.enableTrace(True)
    ws = websocket.WebSocketApp("url",
                              on_message = on_message,
                              on_error = on_error,
                              on_close = on_close)
    ws.on_open = on_public
    #长连接(启动心跳包,ping_interval发送心跳间隔时间,ping_timeout心跳超时时间)
    ws.run_forever(ping_interval=60,ping_timeout=5)


if __name__ == "__main__":
    start_open()