# import pymongo
#
# client = pymongo.MongoClient('localhost', 27017)  # 连接MongoDB数据库
# mydb = client['mydb']  # 创建数据库
# print(mydb['zhihu_topic'] .count())
# count = 0
# for item in mydb['zhihu_topic'].find():
#     if item['topic_level'] == 1:
#         count +=1
# print(count)


# def get_topic_count(topic_level,collection_name):
#     count = 0
#     for item in mydb[collection_name].find():
#         if item['topic_level'] == topic_level:
#             count += 1
#     return count
#
# print(get_topic_count(2,'zhihu_topic'))

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

import multiprocessing


# class MyTask(object):
#     def task(self, x):
#         return x*x
#
#     def run(self):
#         pool = multiprocessing.Pool(processes=3)
#
#         a = [1, 2, 3]
#         pool.map(self.task, a)


# if __name__ == '__main__':
#     t = MyTask()
#     t.run()

# def abc(a, b, c):
#     print(a*10000 + b*100 + c)
#
# list1 = [11,22,33]
# list2 = [44,55,66]
# list3 = [77,88,99]
# map(abc,list1,list2,list3)

import threading

#
# class Demo:
#     def __init__(self, thread_num=5):
#         self.thread_num = thread_num
#
#     def productor(self, i):
#         print("thread-%d start" % i)
#
#     def start(self):
#         threads = []
#         for x in range(self.thread_num):
#             t = threading.Thread(target=self.productor, args=(x,))
#             threads.append(t)
#         for t in threads:
#             t.start()
#         for t in threads:
#             t.join()
#         print('all thread end')
#
#
#
# demo = Demo()
# demo.start()
# import time, hashlib
#
#
# def create_id():
#     m = hashlib.md5(str(time.clock()).encode('utf-8'))
#     return m.hexdigest()
#
#
# if __name__ == '__main__':
#     print(type(create_id()))
#     print(create_id())
#     print(create_id())
#     print(create_id())
import user_agents
import random
get_headers = {
    'User-Agent': random.sample(user_agents.agents, 1)[0]
}
print(get_headers)