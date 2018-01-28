import pymongo

client = pymongo.MongoClient('localhost', 27017)  # 连接MongoDB数据库
mydb = client['mydb']  # 创建数据库
print(mydb.collection_names())
if 'zhihu' in mydb.collection_names():
    print('true')
else:
    print('f')