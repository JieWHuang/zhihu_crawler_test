import requests
import pymongo
import json
import time
import hashlib
import re
import sys
import multiprocessing
import user_agents
import random


class ZhiHuCommon(object):
    '''爬虫通用函数类'''
    with open('Cookies.txt') as f:  # 读取Cookies.txt内的Cookies
        Cookies = f.read()
    xsrf = re.findall('_xsrf=(.*?);', Cookies)  # 用正则表达式找到Cookies里面含有的_xsrf信息
    headers = {
        'Cookie': Cookies,
        'User-Agent': random.sample(user_agents.agents, 1)[0]
    }  # 请求头，通过Cookie登录知乎网
    data = {'_xsrf': str(xsrf[0])}  # POST请求需要传入的参数
    # 爬虫配置信息
    client = pymongo.MongoClient('localhost', 27017)  # 连接MongoDB数据库
    mydb = client['mydb']  # 创建数据库
    max_count = 5  # 最大尝试次数

    @staticmethod
    def get(url, count=1):  # GET请求
        # 显示get的传入参数，方便调试
        print('Crawling...', url)
        print('Trying Count...', count)
        if count >= ZhiHuCommon.max_count:
            print('Tried Too Many Times')
            return None
        try:
            response = requests.get(url, headers=ZhiHuCommon.headers)
            if response.status_code == 200:  # 状态码为200表示正常
                response.encoding = response.apparent_encoding  # 确保中文能正常显示
                return response.text  # 返回html文本
            return None
        except Exception:  # 若出现异常，则再次尝试，若尝试5次还是失败，则返回None
            print('GET Error! Retrying...')
            count += 1
            return ZhiHuCommon.get(url, count)

    @staticmethod
    def post(url, count=1):  # POST请求
        # 显示post的传入参数，方便调试
        print('Crawling...', url)
        print('Trying Count...', count)
        if count >= ZhiHuCommon.max_count:
            print('Tried Too Many Times')
            return None
        try:
            response = requests.post(url, data=ZhiHuCommon.data, headers=ZhiHuCommon.headers)
            if response.status_code == 200:  # 状态码为200表示正常
                response.encoding = response.apparent_encoding  # 确保中文能正常显示
                return response.text  # 返回html文本
            return None
        except Exception:  # 若出现异常，则再次尝试，若尝试5次还是失败，则返回None
            print('POST Error! Retrying...')
            count += 1
            return ZhiHuCommon.post(url, count)

    @staticmethod
    def save2mongodb(data, type):  # 保存数据到MongoDB数据库，方便数据被调用
        if type == 'topic':  # 通过判断数据信息类型，进行数据存储
            try:
                # 判断重复，若重复，则不保存
                if ZhiHuCommon.mydb['zhihu_topic'].update({'topic_id': data['topic_id']}, {'$set': data}, True):
                    print(data['topic_name'], 'Saving to mydb[\'zhihu_topic\'] Successfully...')
                else:
                    print(data['topic_name'], 'Saving to mydb[\'zhihu_topic\'] Failed...')
            except BaseException:
                pass
        elif type == 'question':
            try:
                if ZhiHuCommon.mydb['zhihu_question'].update({'question_id': data['question_id']}, {'$set': data},
                                                             True):
                    print(data['question_title'], 'Saving to mydb[\'zhihu_question\'] Successfully...')
                else:
                    print(data['question_title'], 'Saving to mydb[\'zhihu_question\'] Failed')
            except BaseException:
                pass
        elif type == 'column':
            try:
                if ZhiHuCommon.mydb['zhihu_column'].update({'column_title': data['column_title']}, {'$set': data},
                                                           True):
                    print(data['column_title'], 'Saving to mydb[\'zhihu_column\'] Successfully...')
                else:
                    print(data['column_title'], 'Saving to mydb[\'zhihu_column\'] Failed')
            except BaseException:
                pass
        elif type == 'people':
            try:
                if ZhiHuCommon.mydb['zhihu_people'].update({'author_url_token': data['author_url_token']},
                                                           {'$set': data}, True):
                    print(data['author_name'], 'Saving to mydb[\'zhihu_people\'] Successfully...')
                else:
                    print(data['author_name'], 'Saving to mydb[\'zhihu_people\'] Failed')
            except BaseException:
                pass
        elif type == 'answer':
            try:
                if ZhiHuCommon.mydb['zhihu_answer'].update({'author_name': data['author_name']},
                                                           {'$set': data}, True):
                    print(data['author_name'], 'Saving to mydb[\'zhihu_answer\'] Successfully...')
                else:
                    print(data['author_name'], 'Saving to mydb[\'zhihu_answer\'] Failed')
            except BaseException:
                pass

    @staticmethod
    def view_bar(num, total):  # 爬虫进度条
        rate = num / total
        rate_num = int(rate * 100)
        r = '\r爬虫总进度:%d/%d[%s%s]%d%%\n' % (num, total, "=" * rate_num, " " * (100 - rate_num), rate_num)
        sys.stdout.write(r)
        sys.stdout.flush()


class ZhiHuTopicCrawler(object):
    def __init__(self):
        self.start_url = 'https://www.zhihu.com/topic/19776749/organize/entire'  # 知乎话题树首页
        self.max_level = 2  # 设置爬取深度

    def get_first_level_topic_url(self, url):  # 广度优先遍历根话题下第一层话题
        topic_level = 1  # 设置第一层话题的深度为1
        html = ZhiHuCommon.post(url)  # 知乎话题树的请求方式是POST
        json_data = json.loads(html)  # 解析json网页内容
        for item in json_data['msg'][1]:
            topic_name = item[0][1]  # 话题名称
            topic_id = item[0][2]  # 话题id
            if topic_id != '19776751':  # 「未归类」话题，多是话题别名，不作考虑
                # 解析话题信息，保存成字典
                topic_info = {
                    'type': item[0][0],
                    'topic_name': topic_name,
                    'topic_id': topic_id,
                    'topic_level': topic_level,
                    'parent_topic_name': json_data['msg'][0][1],
                    'parent_topic_id': json_data['msg'][0][2]
                }
                print(topic_info)  # 打印话题信息，调试用
                ZhiHuCommon.save2mongodb(topic_info, topic_info['type'])  # 保存
                yield self.start_url + '?child=&parent={}'.format(topic_id)  # 生成第二层话题的地址

    def get_topic_info(self, url, topic_level=2):  # 从第二层话题开始遍历
        try:
            if topic_level <= self.max_level:  # 判断话题爬虫深度
                html = ZhiHuCommon.post(url)
                json_data = json.loads(html)
                # 解析话题信息，保存成字典
                for item in json_data['msg'][1]:
                    topic_name = item[0][1]
                    topic_id = item[0][2]
                    if topic_name != '加载更多':  # 负责处理话题信息
                        topic_info = {
                            'type': item[0][0],
                            'topic_name': topic_name,
                            'topic_id': topic_id,
                            'topic_level': topic_level,
                            'parent_topic_name': json_data['msg'][0][1],
                            'parent_topic_id': json_data['msg'][0][2]
                        }
                        print(topic_info)
                        # ZhiHuCommon.save2mongodb(topic_info, topic_info['type'])
                    if item[0][1] == '加载更多':  # 负责翻页，实现广度遍历
                        next_page_url = self.start_url + '?child={}&parent={}'.format(item[0][2], item[0][3])
                        self.get_topic_info(next_page_url, topic_level)
                    else:
                        if len(item) == 2:  # 判断是否有'显示子话题'，有则递归调用本身，实现深度遍历
                            child_topic_url = self.start_url + '?child=&parent={}'.format(item[0][2])
                            child_topic_level = topic_level + 1
                            self.get_topic_info(child_topic_url, child_topic_level)
        except BaseException:
            pass

    def topic_crawler(self):
        # 非多进程 耗时189秒
        time1 = time.time()
        for url in self.get_first_level_topic_url(self.start_url):
            self.get_topic_info(url)
        print('耗时' + str(int(time.time() - time1)) + '秒')

        # 多进程 耗时190秒
        # time1 = time.time()
        # pool = multiprocessing.Pool(4)
        # url = [url for url, topic_level in self.get_first_level_topic_url(self.start_url)]
        # topic_level = [topic_level for url, topic_level in self.get_first_level_topic_url(self.start_url)]
        # print(url)
        # print(topic_level)
        # pool.map(self.get_topic_info, url)
        # print('耗时' + str(int(time.time() - time1)) + '秒')


class ZhiHuQuestionCrawler(object):
    def __init__(self):
        self.topic_begin_url = 'https://www.zhihu.com/api/v4/topics/'
        self.topic_level = 2  # 设置爬取深度
        self.limit = 100  # 设置每页展示信息个数
        self.max_offset = 1000  # 设置最大页数，最大为1000

    def get_topic_count(self, collection_name):  # 得到每层话题在数据库内的个数
        count = 0
        for item in ZhiHuCommon.mydb[collection_name].find():
            if item['topic_level'] == self.topic_level:
                count += 1
        return count

    def get_topic(self):  # 用生成器的方式从MongoDB数据库中取出话题数据
        for item in ZhiHuCommon.mydb['zhihu_topic_backup'].find():
            if item['topic_level'] == self.topic_level:
                yield item['topic_id'], item['topic_name']

    def parse_topic(self, url, topic_id, topic_name):  # 解析话题URL，得到问题、专栏、用户数据
        try:
            html = ZhiHuCommon.get(url)
            json_data = json.loads(html)
            for item in json_data['data']:
                if item['target'].get('question'):  # 话题内含有问题信息
                    question_title = item['target']['question']['title']
                    question_id = item['target']['question']['id']
                    question_info = {
                        'type': item['target']['question']['type'],
                        'question_title': question_title,
                        'question_id': question_id,
                        'topic_name': topic_name,
                        'topic_id': topic_id
                    }
                    # print(question_info)
                    ZhiHuCommon.save2mongodb(question_info, question_info['type'])
                elif item['target'].get('column'):  # 话题内含有专栏信息
                    column_title = item['target']['column']['title']
                    column_id = item['target']['column']['id']
                    author_name = item['target']['column']['author']['name']
                    author_url_token = item['target']['column']['author']['url_token']
                    column_info = {
                        'type': item['target']['column']['type'],
                        'column_title': column_title,
                        'column_id': column_id,
                        'author_name': author_name,
                        'author_url_token': author_url_token,
                        'topic_name': topic_name,
                        'topic_id': topic_id,
                    }
                    # print(column_info)
                    ZhiHuCommon.save2mongodb(column_info, column_info['type'])
                    # 解析专栏内作者信息
                    user_info = {
                        'type': item['target']['column']['author']['type'],
                        'author_name': author_name,
                        'author_url_token': author_url_token
                    }
                    print(user_info)
                    ZhiHuCommon.save2mongodb(user_info, user_info['type'])
        except BaseException:
            pass

    def question_crawler(self):
        # 如果是第一次运行的时候，备份话题信息数据库，实现断点续爬的准备
        if 'zhihu_topic_backup' not in ZhiHuCommon.mydb.collection_names():
            for item in ZhiHuCommon.mydb['zhihu_topic'].find():
                ZhiHuCommon.mydb['zhihu_topic_backup'].insert(item)

        # 解析话题，得到每个话题下的问题
        for topic_id, topic_name in self.get_topic():  # 从数据库拿到话题id和话题名字
            print('开始爬取\'{}\'下的数据...'.format(topic_name))
            current_page = 0
            for offset in range(0, self.max_offset, self.limit):  # 生成话题URL
                current_page += 1
                total_page = int(self.max_offset / self.limit)
                print('话题:\'{}\'下的数据,当前已经爬取到{}页,总页数:{}页'.format(topic_name, current_page, total_page))
                url = self.topic_begin_url + '{}/feeds/essence?limit={}&offset={}'.format(topic_id, self.limit, offset)
                self.parse_topic(url, topic_id, topic_name)  # 解析得到每个话题的问题信息
                # 每爬完一个话题下的问题，就删除备份数据库的这一个话题的信息，实现断点续爬
                if offset == self.max_offset - self.limit:  # 判断是否为最后一页
                    ZhiHuCommon.mydb['zhihu_topic_backup'].delete_one({"topic_name": topic_name})
                    print('已经爬完话题:\'{}\'下的数据,休息一下...'.format(topic_name))
                    time.sleep(5)  # 增加暂停时间，避免IP被封
                # 负责显示进度条
                num = self.get_topic_count('zhihu_topic') - self.get_topic_count('zhihu_topic_backup')
                count = self.get_topic_count('zhihu_topic')
                ZhiHuCommon.view_bar(num, count)
                time.sleep(2)  # 增加暂停时间，避免IP被封


class ZhiHuAnswerCrawler(object):
    def __init__(self):
        self.question_begin_url = 'https://www.zhihu.com/api/v4/questions/'
        self.include = 'data[*].is_normal,voteup_count,content'
        self.limit = 20  # 设置每页展示信息个数

    def create_user_id(self):  # 利用时间戳生成不重复匿名用户ID
        user_id = hashlib.md5(str(time.clock()).encode('utf-8'))  # 将当前时间戳转成md5
        return user_id.hexdigest()

    def get_question_id(self):  # 从MongoDB数据库中取出问题数据
        for item in ZhiHuCommon.mydb['zhihu_question_backup'].find():
            yield item['question_id'], item['question_title']

    def get_answer_count(self, url):  # 得到问题回答的总数
        html = ZhiHuCommon.get(url)
        json_data = json.loads(html)
        answer_count = json_data['paging']['totals']
        return answer_count

    def get_question_url(self, question_id):
        question_start_url = self.question_begin_url + '{}/answers?include={}&offset=0&limit={}&sort_by=default'.format(
            question_id, self.include, self.limit)
        answer_count = self.get_answer_count(question_start_url)
        max_offset = int(answer_count / self.limit) * self.limit
        total_page = int(max_offset / self.limit)
        current_page = 0
        # max_offset = 20  # 测试用
        for offset in range(0, max_offset, self.limit):
            current_page += 1
            question_url = self.question_begin_url + '{}/answers?include={}&offset={}&limit={}&sort_by=default'.format(
                question_id, self.include, offset, self.limit)
            yield question_url, offset, max_offset, current_page, total_page

    def parse_question(self, url):
        try:
            html = ZhiHuCommon.get(url)
            json_data = json.loads(html)
            for item in json_data['data']:
                author_name = item['author']['name']
                author_url_token = item['author']['url_token']
                question_title = item['question']['title']
                answer_content = re.compile(r'<[^>]+>', re.S).sub('', item['content']).replace('\n', ' ')
                answer_voteup_count = item['voteup_count']
                if author_name == '匿名用户':  # 判断是否为匿名用户，如果是，则将回答者名字改为匿名用户+随机id
                    author_name = {
                        'author_type': '匿名用户',
                        'random_number': self.create_user_id()
                    }
                    author_url_token = '无'
                answer_info = {
                    'type': item['type'],
                    'question_title': question_title,  # 问题标题
                    'author_name': author_name,  # 回答者名字
                    'author_url_token': author_url_token,  # 回答者url_token
                    'answer_content': answer_content,  # 回答内容
                    'answer_content_length': len(answer_content),  # 回答长度
                    'answer_voteup_count': answer_voteup_count  # 回答赞同人数
                }
                # print(answer_info)
                ZhiHuCommon.save2mongodb(answer_info, answer_info['type'])
        except BaseException:
            pass

    def answer_crawler(self):
        if 'zhihu_question_backup' not in ZhiHuCommon.mydb.collection_names():  # 如果是第一次运行的时候，备份话题信息数据库
            for item in ZhiHuCommon.mydb['zhihu_question'].find():
                ZhiHuCommon.mydb['zhihu_question_backup'].insert(item)
        for question_id, question_title in self.get_question_id():  # 从数据库拿到问题id
            print('开始爬取\'{}\'下的数据...'.format(question_title))
            for question_url, offset, max_offset, current_page, total_page in self.get_question_url(question_id):
                print('问题:\'{}\'下的数据,当前已经爬取到{}页,总页数:{}页'.format(question_title, current_page, total_page))
                self.parse_question(question_url)  # 解析得到每个问题下的回答信息
                # 每爬完一个问题下的回答，就删除备份数据库的这一个问题的信息，实现断点续爬
                if offset == max_offset - self.limit:  # 判断是否为最后一页，如果是，则从备份表内删除已爬取完的数据
                    ZhiHuCommon.mydb['zhihu_question_backup'].delete_one({"question_id": question_id})
                    print('已经爬完问题:\'{}\'下的数据,休息一下...'.format(question_title))
                    time.sleep(5)  # 增加暂停时间，避免IP被封
                # 负责显示进度条
                num = ZhiHuCommon.mydb['zhihu_question'].count() - ZhiHuCommon.mydb['zhihu_question_backup'].count()
                count = ZhiHuCommon.mydb['zhihu_question'].count()
                ZhiHuCommon.view_bar(num, count)
                time.sleep(2)  # 增加暂停时间，避免IP被封


class ZhiHuUserCrawler(object):
    def __init__(self):
        self.user_begin_url = 'https://www.zhihu.com/api/v4/members/'
        # 完整include
        # self.include = 'headline,locations,employments,gender,educations,business,voteup_count,thanked_Count,follower_count,following_count,' \
        #                'cover_url,following_topic_count,following_question_count,following_favlists_count,following_columns_count,' \
        #                'avatar_hue,answer_count,articles_count,pins_count,question_count,columns_count,commercial_question_count,' \
        #                'favorite_count,favorited_count,logs_count,included_answers_count,included_articles_count,included_text,' \
        #                'message_thread_token,account_status,is_active,is_bind_phone,is_force_renamed,is_bind_sina,is_privacy_protected,' \
        #                'sina_weibo_url,sina_weibo_name,show_sina_weibo,is_blocking,is_blocked,is_following,is_followed,' \
        #                'is_org_createpin_white_user,mutual_followees_count,vote_to_count,vote_from_count,thank_to_count,thank_from_count,' \
        #                'thanked_count,description,hosted_live_count,participated_live_count,allow_message,industry_category,org_name,' \
        #                'org_homepage,badge[?(type=best_answerer)].topics'
        # 要爬取的信息集合
        self.include = 'headline,gender,locations,business,employments,educations,description,answer_count,question_count,articles_count,' \
                       'columns_count,following_count,follower_count,voteup_count,thanked_count'

    def get_user_count(self, collection_name):  # 从数据表内获取除匿名用户外的用户总数
        count = 0
        for item in ZhiHuCommon.mydb[collection_name].find():
            if len(item['author_name']) != 2:
                count += 1
        return count

    def get_user_url(self):
        for item in ZhiHuCommon.mydb['zhihu_answer_backup'].find():
            if len(item['author_name']) != 2:  # 排除匿名用户
                # 拼接URL
                zhihu_user_url = self.user_begin_url + item['author_url_token'] + '?include={}'.format(self.include)
                yield zhihu_user_url, item['author_url_token']

    def parse_user_info(self, url):
        try:
            html = ZhiHuCommon.get(url)
            json_data = json.loads(html)
            author_name = json_data['name']
            author_url_token = json_data['url_token']
            headline = json_data['headline']
            if json_data['gender']:
                gender = '男'
            else:
                gender = '女'
            if json_data.get('locations'):
                locations = json_data['locations'][0]['name']
            else:
                locations = '无'
            if json_data.get('business'):
                business = json_data['business']['name']
            else:
                business = '无'
            if json_data.get('employments'):
                employments = json_data['employments']
            else:
                employments = '无'
            if json_data.get('educations'):
                educations = json_data['educations']
            else:
                educations = '无'
            if json_data.get('description'):
                description = json_data['description']
            else:
                description = '无'
            answer_count = json_data['answer_count']
            question_count = json_data['question_count']
            articles_count = json_data['articles_count']
            columns_count = json_data['columns_count']
            following_count = json_data['following_count']
            follower_count = json_data['follower_count']
            voteup_count = json_data['voteup_count']
            thanked_count = json_data['thanked_count']
            user_info = {
                'type': json_data['type'],
                'author_name': author_name,
                'author_url_token': author_url_token,
                'headline': re.compile(r'<[^>]+>', re.S).sub('', headline),  # 数据清洗，将html标签过滤掉
                'gender': gender,
                'locations': locations,
                'business': business,
                'employments': employments,
                'educations': educations,
                'description': re.compile(r'<[^>]+>', re.S).sub('', description),  # 数据清洗，将html标签过滤掉
                'answer_count': answer_count,
                'question_count': question_count,
                'articles_count': articles_count,
                'columns_count': columns_count,
                'following_count': following_count,
                'follower_count': follower_count,
                'voteup_count': voteup_count,
                'thanked_count': thanked_count,
            }
            # print(user_info)  # 调试用
            ZhiHuCommon.save2mongodb(user_info, user_info['type'])  # 保存到数据库
        except Exception:
            pass

    def user_crawler(self):
        if 'zhihu_answer_backup' not in ZhiHuCommon.mydb.collection_names():  # 如果是第一次运行的时候，备份数据库
            for item in ZhiHuCommon.mydb['zhihu_answer'].find():
                ZhiHuCommon.mydb['zhihu_answer_backup'].insert(item)
        for user_url, author_url_token in self.get_user_url():  # 抽取用户数据，拼接用户主页URL
            # 解析用户数据
            self.parse_user_info(user_url)
            # 实现断点续爬
            ZhiHuCommon.mydb['zhihu_answer_backup'].delete_one({"author_url_token": author_url_token})
            # 负责显示进度条
            num = self.get_user_count('zhihu_answer') - self.get_user_count('zhihu_answer_backup')
            count = self.get_user_count('zhihu_answer')
            ZhiHuCommon.view_bar(num, count)
            time.sleep(2)  # 增加暂停时间，避免IP被封


if __name__ == '__main__':
    # TopicCrawler = ZhiHuTopicCrawler()
    # TopicCrawler.topic_crawler()

    # QuestionCrawler = ZhiHuQuestionCrawler()
    # QuestionCrawler.question_crawler()

    AnswerCrawler = ZhiHuAnswerCrawler()
    AnswerCrawler.answer_crawler()

    # UserCrawler = ZhiHuUserCrawler()
    # UserCrawler.user_crawler()
