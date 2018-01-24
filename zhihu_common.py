import requests
import pymongo

headers = {
    'Cookie': 'q_c1=1883f1840aae4da282d328092b586954|1514120291000|1514120291000; __utmz=51854390.1514120292.1.1.utmcsr=baidu|utmccn=(organic)|utmcmd=organic; _zap=084caaf9-3293-40b4-801b-29a61c87a04a; aliyungf_tc=AQAAAPRB6x2dgwwA/k7T3zehfNVlrCWF; l_n_c=1; l_cap_id="MGFiM2M0MGVmOGQ5NDA1YWFmOWI1MzQyMmFmNmUyMGM=|1516372907|7e2585641df1410ea469fa764ec9a57d480917fe"; r_cap_id="YzI2NDBiZWFiMWYxNGExZDg1MjAzMjY5MTI3NTgwMmU=|1516372907|60207a4912110eb8457a69b79b9f2baaad4bf204"; cap_id="YzdmNmFlZjIzNjFhNGIxZmEyNjkyZGVhZmVjNmY3ZmM=|1516372907|d7e523abe32982696a07048f416a0bf750bf5fae"; n_c=1; d_c0="ADBte0HLAw2PTtJd_5kMd03T8T8o8JKTEWI=|1516372908"; _xsrf=d2e2e2ce-72d2-414f-9fec-f9db9a42d3e7; capsion_ticket="2|1:0|10:1516372936|14:capsion_ticket|44:ZGQ1N2QwYWNhZDM4NDg3Y2JlYTQyMjNiY2IwN2ZjYTM=|b6be1ad61612c5f74665cebb94d6c2dac0824312a29e40582a502dcc4c4c9c9a"; z_c0="2|1:0|10:1516372942|4:z_c0|92:Mi4xdkpOZEF3QUFBQUFBTUcxN1Fjc0REU1lBQUFCZ0FsVk56bEZQV3dBb3R2Q2VoMzlnUUFYb05rLTZLS2JUSC1Sa1BB|ba39ec284785b5e9b20f010f7d6d51c3da0f00ee09d1899ddc4edfdd00d0226a"; __utma=51854390.1991264370.1514120292.1514120292.1516372944.2; __utmb=51854390.0.10.1516372944; __utmc=51854390; __utmv=51854390.100--|2=registration_date=20160818=1^3=entry_date=20160818=1',
    'Host': 'www.zhihu.com',
    'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.132 Safari/537.36',
}  # 请求头，通过Cookie登录知乎网

data = {'_xsrf': 'd2e2e2ce-72d2-414f-9fec-f9db9a42d3e7'}  # POST请求需要传入的参数

client = pymongo.MongoClient('localhost', 27017)  # 连接MongoDB数据库
mydb = client['mydb']  # 创建数据库

max_count = 5  # 最大尝试次数


def get(url, count=1):  # GET请求
    print('Crawling...', url)
    print('Trying Count...', count)
    if count >= max_count:
        print('Tried Too Many Times')
        return None
    try:
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            response.encoding = response.apparent_encoding  # 确保中文能正常显示
            return response.text
        return None
    except Exception:  # 若出现异常，则再次尝试，若尝试5次还是失败，则返回None
        print('GET Error! Retrying...')
        count += 1
        return get(url, count)


def post(url, count=1):  # POST请求
    print('Crawling...', url)
    print('Trying Count...', count)
    if count >= max_count:
        print('Tried Too Many Times')
        return None
    try:
        response = requests.post(url, data=data, headers=headers)
        if response.status_code == 200:
            response.encoding = response.apparent_encoding  # 确保中文能正常显示
            return response.text
        return None
    except Exception:  # 若出现异常，则再次尝试，若尝试5次还是失败，则返回None
        print('POST Error! Retrying...')
        count += 1
        return post(url, count)


def save2mongodb(data, type):  # 保存数据到MongoDB数据库，方便数据被调用
    if type == 'topic':  # 通过判断数据信息类型，进行数据存储
        try:
            if mydb['zhihu_topic'].update({'topic_id': data['topic_id']}, {'$set': data}, True):  # 判断重复，若重复，则不保存
                print(data['topic_name'], 'Saving to MongoDB Successfully...')
            else:
                print(data['topic_name'], 'Saving to MongoDB Failed...')
        except:
            pass
    elif type == 'question':
        try:
            if mydb['zhihu_question'].update({'question_id': data['question_id']}, {'$set': data}, True):
                print(data['question_title'], 'Saving to MongoDB Successfully...')
            else:
                print(data['question_title'], 'Saving to MongoDB Failed')
        except:
            pass
    elif type == 'column':
        try:
            if mydb['zhihu_column'].update({'column_title': data['column_title']}, {'$set': data}, True):
                print(data['column_title'], 'Saving to MongoDB Successfully...')
            else:
                print(data['column_title'], 'Saving to MongoDB Failed')
        except:
            pass
    elif type == 'people':
        try:
            if mydb['zhihu_people'].update({'author_url_token': data['author_url_token']}, {'$set': data}, True):
                print(data['author_name'], 'Saving to MongoDB Successfully...')
            else:
                print(data['author_name'], 'Saving to MongoDB Failed')
        except:
            pass
    elif type == 'answer':
        try:
            if mydb['zhihu_answer'].update({'author_url_token': data['author_url_token']}, {'$set': data}, True):
                print(data['author_name'], 'Saving to MongoDB Successfully...')
            else:
                print(data['author_name'], 'Saving to MongoDB Failed')
        except:
            pass
