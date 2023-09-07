import json

import requests
import execjs
import time
import datetime
import os

headers = {
    'Accept': '*/*',
    'Accept-Language': 'zh-CN,zh;q=0.9',
    'Connection': 'keep-alive',
    'Host': 'music.163.com',
    'Origin': 'https://music.163.com',
    'Content-Type': 'application/x-www-form-urlencoded',
    'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:22.0) Gecko/20100101 Firefox/22.0'
}

with open("wyy.js", "r", encoding="utf-8") as events_file:
    wyy_js_file = events_file.read()
wyy_js = execjs.compile(wyy_js_file)


def getEvent(userId, timestamp=str(int(time.time() * 1000000))[:15]):
    url = "https://music.163.com/weapi/event/get/" + userId + "?csrf_token="
    data = {
        "userId": userId,
        "total": "false",
        "limit": "20",
        "time": timestamp,  # 15位的时间戳
        "getcounts": "true",
        "csrf_token": ""
    }
    data = wyy_js.call("asrsea", data)
    # print(data)
    data = {"params": data["encText"], "encSecKey": data["encSecKey"]}
    # print(data)
    return requests.post(url, data, headers=headers)


uid = "0000000"
events_file = open("events/" + uid + ".txt", "a", encoding="utf-8")
index = 0
resp = getEvent(uid)
if not resp.ok:
    raise ValueError("获取动态列表失败")
if os.path.exists("events/chunk/" + uid):
    os.makedirs("events/chunk/" + uid)
with open("events/chunk/" + uid + "/events_" + str(index) + ".txt", "w", encoding="utf-8") as ec:
    ec.write(resp.text)
resp = json.loads(resp.text)
events = resp["events"]
print(len(events))
for event in events:
    index += 1
    events_file.write(
        "\n--------------------|{index}[{time}]({id})|---------------------------\n"
            .format(index=index,
                    time=datetime.datetime.fromtimestamp(event["eventTime"] / 1000).strftime("%Y-%m-%d %H:%M:%S"),
                    id=event["id"])
    )
    title = event["info"]["commentThread"]["resourceTitle"]
    if title is None:
        events_file.write("分享单曲\n")
    else:
        events_file.write(title + "\n")
    events_file.write(str(json.loads(event["json"])["msg"]))
time.sleep(2)
while resp["more"]:
    resp = getEvent(uid, resp["lasttime"])
    if not resp.ok:
        raise ValueError("获取动态列表失败")
    with open("events/chunk/" + uid + "/events_" + str(index) + ".txt", "w", encoding="utf-8") as ec:
        ec.write(resp.text)
    resp = json.loads(resp.text)
    events = resp["events"]
    print(len(events))
    for event in events:
        index += 1
        events_file.write(
            "\n--------------------|{index}[{time}]({id})|---------------------------\n"
                .format(index=index,
                        time=datetime.datetime.fromtimestamp(event["eventTime"] / 1000).strftime("%Y-%m-%d %H:%M:%S"),
                        id=event["id"])
        )
        title = event["info"]["commentThread"]["resourceTitle"]
        if title is None:
            events_file.write("分享单曲\n")
        else:
            events_file.write(title + "\n")
        events_file.write(str(json.loads(event["json"])["msg"]))
    time.sleep(2)
events_file.close()
