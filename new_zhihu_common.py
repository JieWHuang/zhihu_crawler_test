import requests
import pymongo

headers = {
    'Cookie': 'q_c1=1883f1840aae4da282d328092b586954|1514120291000|1514120291000; __utmz=51854390.1514120292.1.1.utmcsr=baidu|utmccn=(organic)|utmcmd=organic; _zap=084caaf9-3293-40b4-801b-29a61c87a04a; aliyungf_tc=AQAAAPRB6x2dgwwA/k7T3zehfNVlrCWF; l_n_c=1; l_cap_id="MGFiM2M0MGVmOGQ5NDA1YWFmOWI1MzQyMmFmNmUyMGM=|1516372907|7e2585641df1410ea469fa764ec9a57d480917fe"; r_cap_id="YzI2NDBiZWFiMWYxNGExZDg1MjAzMjY5MTI3NTgwMmU=|1516372907|60207a4912110eb8457a69b79b9f2baaad4bf204"; cap_id="YzdmNmFlZjIzNjFhNGIxZmEyNjkyZGVhZmVjNmY3ZmM=|1516372907|d7e523abe32982696a07048f416a0bf750bf5fae"; n_c=1; d_c0="ADBte0HLAw2PTtJd_5kMd03T8T8o8JKTEWI=|1516372908"; _xsrf=d2e2e2ce-72d2-414f-9fec-f9db9a42d3e7; capsion_ticket="2|1:0|10:1516372936|14:capsion_ticket|44:ZGQ1N2QwYWNhZDM4NDg3Y2JlYTQyMjNiY2IwN2ZjYTM=|b6be1ad61612c5f74665cebb94d6c2dac0824312a29e40582a502dcc4c4c9c9a"; z_c0="2|1:0|10:1516372942|4:z_c0|92:Mi4xdkpOZEF3QUFBQUFBTUcxN1Fjc0REU1lBQUFCZ0FsVk56bEZQV3dBb3R2Q2VoMzlnUUFYb05rLTZLS2JUSC1Sa1BB|ba39ec284785b5e9b20f010f7d6d51c3da0f00ee09d1899ddc4edfdd00d0226a"; __utma=51854390.1991264370.1514120292.1514120292.1516372944.2; __utmb=51854390.0.10.1516372944; __utmc=51854390; __utmv=51854390.100--|2=registration_date=20160818=1^3=entry_date=20160818=1',
    'Host': 'www.zhihu.com',
    'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.132 Safari/537.36',
}

data = {'_xsrf': 'd2e2e2ce-72d2-414f-9fec-f9db9a42d3e7'}

client = pymongo.MongoClient('localhost', 27017)
mydb = client['mydb']

max_count = 5


def get(url, count=1):
    print('Crawling...', url)
    print('Trying Count...', count)
    if count >= max_count:
        print('Tried Too Many Times')
        return None
    try:
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            response.raise_for_status()
            response.encoding = response.apparent_encoding
            return response.text
        return None
    except Exception:
        print('GET Error! Retrying...')
        count += 1
        return get(url, count)


def post(url, count=1):
    print('Crawling...', url)
    print('Trying Count...', count)
    if count >= max_count:
        print('Tried Too Many Times')
        return None
    try:
        response = requests.post(url, data=data, headers=headers)
        if response.status_code == 200:
            response.raise_for_status()
            response.encoding = response.apparent_encoding
            return response.text
        return None
    except Exception:
        print('POST Error! Retrying...')
        count += 1
        return post(url, count)
