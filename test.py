import pymongo

client = pymongo.MongoClient('localhost', 27017)  # 连接MongoDB数据库
ZhiHu_db = client['ZhiHu_db']  # 创建数据库
count = 0
for item in ZhiHu_db['answer'].find():
    if item['author_name'][0:4] == '匿名用户':  # 排除匿名用户
        count += 1
print(count)
