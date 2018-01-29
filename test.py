import pymongo

client = pymongo.MongoClient('localhost', 27017)  # 连接MongoDB数据库
mydb = client['mydb']  # 创建数据库
print(mydb['zhihu_topic'] .count())
# count = 0
# for item in mydb['zhihu_topic'].find():
#     if item['topic_level'] == 1:
#         count +=1
# print(count)


def get_topic_count(topic_level,collection_name):
    count = 0
    for item in mydb[collection_name].find():
        if item['topic_level'] == topic_level:
            count += 1
    return count

print(get_topic_count(2,'zhihu_topic'))

# import sys
# import time
#
#
# def view_bar(num, total):
#     rate = num / total
#     rate_num = int(rate * 100)
#     r = '\r[%s%s]%d%%' % ("=" * num, " " * (100 - num), rate_num,)
#     sys.stdout.write(r)
#     sys.stdout.flush()
#
#
# if __name__ == '__main__':
#     for i in range(0, 101):
#         time.sleep(0.1)
#         view_bar(i, 100)