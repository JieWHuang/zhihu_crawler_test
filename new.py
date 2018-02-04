import requests
import pymongo
import json
import time
import hashlib
import re
import user_agents
import cookies
import random
import sys


class ZhiHuCommon(object):
    '''爬虫通用函数类'''
    Cookies = random.sample(cookies.cookies, 1)[0]  # 从Cookies池随机获取
    User_Agent = random.sample(user_agents.agents, 1)[0]  # 从User-Agent池随机获取
    _xsrf = re.findall('_xsrf=(.*?);', Cookies)  # 用正则表达式找到Cookies里面含有的_xsrf信息
    headers = {
        'Cookie': Cookies,
        'User-Agent': User_Agent
    }  # 请求头，通过Cookie登录知乎网
    data = {'_xsrf': str(_xsrf[0])}  # POST请求需要传入的参数
    # 爬虫配置信息
    client = pymongo.MongoClient('localhost', 27017)  # 连接MongoDB数据库
    ZhiHu_db = client['ZhiHu_db']  # 创建数据库
    max_count = 5  # 最大尝试次数

    @staticmethod
    def get(url, count=1):  # GET请求
        # 显示get的传入参数，方便调试
        print('第{}次尝试爬取:{}'.format(count, url))
        if count >= ZhiHuCommon.max_count:
            print('尝试次数过多...')
            return None
        else:
            try:
                response = requests.get(url, headers=ZhiHuCommon.headers)
                if response.status_code == 200:  # 状态码为200表示正常
                    response.encoding = response.apparent_encoding  # 确保中文能正常显示
                    return response.text  # 返回html文本
                return None
            except Exception:  # 若出现异常，则再次尝试，若尝试5次还是失败，则返回None
                print('GET请求出错! 正在重试...')
                count += 1
                return ZhiHuCommon.get(url, count)

    @staticmethod
    def post(url, count=1):  # POST请求
        # 显示post的传入参数，方便调试
        print('第{}次尝试爬取:{}'.format(count, url))
        if count >= ZhiHuCommon.max_count:
            print('尝试次数过多...')
            return None
        else:
            try:
                response = requests.post(url, data=ZhiHuCommon.data, headers=ZhiHuCommon.headers)
                if response.status_code == 200:  # 状态码为200表示正常
                    response.encoding = response.apparent_encoding  # 确保中文能正常显示
                    return response.text  # 返回html文本
                return None
            except Exception:  # 若出现异常，则再次尝试，若尝试5次还是失败，则返回None
                print('POST请求出错! 正在重试...')
                count += 1
                return ZhiHuCommon.post(url, count)

    @staticmethod
    def save2mongodb(data, type):  # 保存数据到MongoDB数据库，方便数据被调用
        if type == 'topic':  # 通过判断数据信息类型，进行数据存储
            try:
                # 判断重复，若重复，则不保存
                if ZhiHuCommon.ZhiHu_db['topic'].update({'topic_id': data['topic_id']}, {'$set': data}, True):
                    print('话题:\'{}\'保存到数据库成功...'.format(data['topic_name']))
                else:
                    print('话题:\'{}\'保存到数据库失败...'.format(data['topic_name']))
            except Exception:
                pass
        elif type == 'question':
            try:
                if ZhiHuCommon.ZhiHu_db['question'].update({'question_id': data['question_id']}, {'$set': data}, True):
                    print('问题:\'{}\'保存到数据库成功...'.format(data['question_title']))
                else:
                    print('问题:\'{}\'保存到数据库失败...'.format(data['question_title']))
            except Exception:
                pass
        elif type == 'column':
            try:
                if ZhiHuCommon.ZhiHu_db['column'].update({'column_id': data['column_id']}, {'$set': data}, True):
                    print('专栏:\'{}\'保存到数据库成功...'.format(data['column_title']))
                else:
                    print('专栏:\'{}\'保存到数据库失败...'.format(data['column_title']))
            except Exception:
                pass
        elif type == 'people':
            try:
                if ZhiHuCommon.ZhiHu_db['people'].update({'author_url_token': data['author_url_token']}, {'$set': data},
                                                         True):
                    print('用户:\'{}\'保存到数据库成功...'.format(data['author_name']))
                else:
                    print('用户:\'{}\'保存到数据库失败...'.format(data['author_name']))
            except Exception:
                pass
        elif type == 'answer':
            try:
                if ZhiHuCommon.ZhiHu_db['answer'].update({'answer_content': data['answer_content']}, {'$set': data},
                                                         True):
                    print('用户:\'{}\'保存到数据库成功...'.format(data['author_name']))
                else:
                    print('用户:\'{}\'保存到数据库失败...'.format(data['author_name']))
            except Exception:
                pass

    @staticmethod
    def sec2time(seconds):
        m, s = divmod(seconds, 60)
        h, m = divmod(m, 60)
        return "%02d:%02d:%02d" % (h, m, s)

    @staticmethod
    def view_bar(num, total, st=time.clock()):  # 爬虫进度条
        rate = num / total
        rate_num = int(rate * 100)
        duration = int(time.clock() - st)
        remaining = int(duration * 100 / (0.01 + rate_num) - duration)
        r1 = '\r爬虫总进度:{0}/{1}[{2}{3}]{4}%'.format(num, total, "=" * rate_num, " " * (100 - rate_num), rate_num)
        r2 = '\t耗时:{0},预计需要:{1}\n'.format(ZhiHuCommon.sec2time(duration), ZhiHuCommon.sec2time(remaining))
        sys.stdout.write(r1 + r2)
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
                # print(topic_info)  # 打印话题信息，调试用
                # ZhiHuCommon.save2mongodb(topic_info, topic_info['type'])  # 保存
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
                        ZhiHuCommon.save2mongodb(topic_info, topic_info['type'])
                    if item[0][1] == '加载更多':  # 负责翻页，实现广度遍历
                        next_page_url = self.start_url + '?child={}&parent={}'.format(item[0][2], item[0][3])
                        self.get_topic_info(next_page_url, topic_level)
                    else:
                        if len(item) == 2:  # 判断是否有'显示子话题'，有则递归调用本身，实现深度遍历
                            child_topic_url = self.start_url + '?child=&parent={}'.format(item[0][2])
                            child_topic_level = topic_level + 1
                            self.get_topic_info(child_topic_url, child_topic_level)
        except Exception:
            pass

    def topic_crawler(self):
        for url in self.get_first_level_topic_url(self.start_url):
            self.get_topic_info(url)


class ZhiHuQuestionCrawler(object):
    def __init__(self):
        self.topic_api = 'https://www.zhihu.com/api/v4/topics/'
        self.topic_level = 2  # 设置爬取深度
        self.limit = 20  # 设置每页展示信息个数

    def get_topic_count(self, collection_name):  # 得到每层话题在数据库内的个数
        count = 0
        for item in ZhiHuCommon.ZhiHu_db[collection_name].find():
            if item['topic_level'] == self.topic_level:
                count += 1
        return count

    def get_topic_from_db(self):  # 用生成器的方式从MongoDB数据库中取出话题数据
        for item in ZhiHuCommon.ZhiHu_db['topic_backup'].find():
            if item['topic_level'] == self.topic_level:
                yield item['topic_id'], item['topic_name']

    def parse_topic(self, url, topic_id, topic_name):
        try:
            time.sleep(2)  # 增加暂停时间，避免IP被封
            html = ZhiHuCommon.get(url)
            json_data = json.loads(html)
            is_end = json_data['paging']['is_end']
            # 由于解析出来的URL为http协议，但需要https协议的URL，通过切片，在URL中间加入s
            next_url = json_data['paging']['next'][:4] + 's' + json_data['paging']['next'][4:]
            if is_end == False:  # 判断是否为最后一页
                for item in json_data['data']:
                    if item['target'].get('question'):  # 话题内含有问题信息
                        created_time = item['target']['question']['created']
                        question_info = {
                            'type': item['target']['question']['type'],
                            'question_title': item['target']['question']['title'],
                            'question_id': item['target']['question']['id'],
                            'created_time': time.strftime("%Y-%m-%d", time.localtime(created_time)),
                            'topic_name': topic_name,
                            'topic_id': topic_id
                        }
                        # print(question_info)
                        ZhiHuCommon.save2mongodb(question_info, question_info['type'])
                    elif item['target'].get('column'):  # 话题内含有专栏信息
                        author_name = item['target']['column']['author']['name']
                        author_url_token = item['target']['column']['author']['url_token']
                        column_info = {
                            'type': item['target']['column']['type'],
                            'column_title': item['target']['column']['title'],
                            'column_id': item['target']['column']['id'],
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
                        # print(user_info)
                        ZhiHuCommon.save2mongodb(user_info, user_info['type'])
                # 负责显示进度条
                num = self.get_topic_count('topic') - self.get_topic_count('topic_backup')
                count = self.get_topic_count('topic')
                ZhiHuCommon.view_bar(num, count)
                self.parse_topic(next_url, topic_id, topic_name)  # 递归调用，解析下一页内容
            return True
        except Exception:
            pass

    def question_crawler(self):
        # 如果是第一次运行的时候，备份话题信息数据库，实现断点续爬的准备
        if 'topic_backup' not in ZhiHuCommon.ZhiHu_db.collection_names():
            for item in ZhiHuCommon.ZhiHu_db['topic'].find():
                ZhiHuCommon.ZhiHu_db['topic_backup'].insert(item)
        else:
            if ZhiHuCommon.ZhiHu_db['answer_backup'].count() != 0:
                print('正在恢复爬取进度...')
            else:
                print('已经爬取完成...')

        # 解析话题，得到每个话题下的问题
        for topic_id, topic_name in self.get_topic_from_db():  # 从数据库拿到话题id和话题名字
            print('开始爬取话题:\'{}\'下的数据...'.format(topic_name))
            start_url = self.topic_api + '{}/feeds/essence?limit={}&offset=0'.format(topic_id, self.limit)
            is_end = self.parse_topic(start_url, topic_id, topic_name)  # 解析得到每个话题的问题信息
            # 每爬完一个话题下的所有问题，就删除备份数据库的这一个话题的信息，实现断点续爬
            if is_end:
                ZhiHuCommon.ZhiHu_db['topic_backup'].delete_one({"topic_name": topic_name})
                print('已经爬完话题:\'{}\'下的数据,休息一下...'.format(topic_name))

                # 负责显示进度条
                num = self.get_topic_count('topic') - self.get_topic_count('topic_backup')
                count = self.get_topic_count('topic')
                ZhiHuCommon.view_bar(num, count)
                time.sleep(5)  # 增加暂停时间，避免IP被封


class ZhiHuAnswerCrawler(object):
    def __init__(self):
        self.question_api = 'https://www.zhihu.com/api/v4/questions/'
        self.question_api_parm = '{}/answers?include={}&offset=0&limit={}&sort_by=default'
        self.include = 'data[*].comment_count,voteup_count,content'
        self.limit = 20  # 设置每页展示信息个数

    def create_user_id(self):  # 利用时间戳生成不重复匿名用户ID
        user_id = hashlib.md5(str(time.clock()).encode('utf-8'))  # 将当前时间戳转成md5
        return user_id.hexdigest()

    def get_question_id(self):  # 从MongoDB数据库中取出问题数据
        for item in ZhiHuCommon.ZhiHu_db['question_backup'].find():
            yield item['question_id'], item['question_title']

    def get_answer_count(self, url):  # 得到问题回答的总数
        html = ZhiHuCommon.get(url)
        json_data = json.loads(html)
        answer_count = json_data['paging']['totals']
        return answer_count

    def get_question_url(self, question_id):
        question_start_url = self.question_api + self.question_api_parm.format(question_id, self.include, self.limit)
        answer_count = self.get_answer_count(question_start_url)
        max_offset = int(answer_count / self.limit) * self.limit
        total_page = int(max_offset / self.limit)
        current_page = 0
        # max_offset = 20  # 测试用
        for offset in range(0, max_offset, self.limit):
            current_page += 1
            question_url = self.question_api + self.question_api_parm.format(question_id, self.include, offset,self.limit)
            yield question_url, offset, max_offset, current_page, total_page

    def parse_question(self, url):
        try:
            time.sleep(2)  # 增加暂停时间，避免IP被封
            html = ZhiHuCommon.get(url)
            json_data = json.loads(html)
            for item in json_data['data']:
                author_name = item['author']['name']
                author_url_token = item['author']['url_token']
                question_title = item['question']['title']
                answer_content = re.compile(r'<[^>]+>', re.S).sub('', item['content']).replace('\n', ' ')
                answer_voteup_count = item['voteup_count']
                answer_comment_count = item['comment_count']
                answer_updated_time = time.strftime("%Y-%m-%d", time.localtime(item['updated_time']))
                answer_created_time = time.strftime("%Y-%m-%d", time.localtime(item['created_time']))
                if author_name == '匿名用户':  # 判断是否为匿名用户，如果是，则将回答者名字改为匿名用户+id
                    author_name = {
                        'author_type': '匿名用户',
                        'author_id': self.create_user_id()
                    }
                    author_url_token = '无'
                answer_info = {
                    'type': item['type'],
                    'question_title': question_title,  # 问题标题
                    'author_name': author_name,  # 回答者名字
                    'author_url_token': author_url_token,  # 回答者url_token
                    'answer_content': answer_content,  # 回答内容
                    'answer_content_length': len(answer_content),  # 回答长度
                    'answer_voteup_count': answer_voteup_count,  # 回答赞同数
                    'answer_comment_count': answer_comment_count,  # 回答评论数
                    'answer_updated_time': answer_updated_time,  # 回答编辑时间
                    'answer_created_time': answer_created_time  # 回答创建时间
                }
                # print(answer_info)
                ZhiHuCommon.save2mongodb(answer_info, answer_info['type'])
        except Exception:
            pass

    def answer_crawler(self):
        if 'question_backup' not in ZhiHuCommon.ZhiHu_db.collection_names():  # 如果是第一次运行的时候，备份话题信息数据库
            for item in ZhiHuCommon.ZhiHu_db['question'].find():
                ZhiHuCommon.ZhiHu_db['question_backup'].insert(item)
        else:
            if ZhiHuCommon.ZhiHu_db['question_backup'].count() != 0:
                print('正在恢复爬取进度...')
            else:
                print('已经爬取完成...')

        for question_id, question_title in self.get_question_id():  # 从数据库拿到问题id
            print('开始爬取\'{}\'下的数据...'.format(question_title))
            for question_url, offset, max_offset, current_page, total_page in self.get_question_url(question_id):
                print('问题:\'{}\'下的数据,当前已经爬取到{}页,总页数:{}页'.format(question_title, current_page, total_page))
                self.parse_question(question_url)  # 解析得到每个问题下的回答信息

                # 负责显示进度条
                num = ZhiHuCommon.ZhiHu_db['question'].count() - ZhiHuCommon.ZhiHu_db['question_backup'].count()
                count = ZhiHuCommon.ZhiHu_db['question'].count()
                ZhiHuCommon.view_bar(num, count)
                # 每爬完一个问题下的回答，就删除备份数据库的这一个问题的信息，实现断点续爬
                if offset == max_offset - self.limit:  # 判断是否为最后一页，如果是，则从备份表内删除已爬取完的数据
                    ZhiHuCommon.ZhiHu_db['question_backup'].delete_one({"question_id": question_id})
                    print('已经爬完问题:\'{}\'下的数据,休息一下...'.format(question_title))
                    time.sleep(5)  # 增加暂停时间，避免IP被封


class ZhiHuUserCrawler(object):
    def __init__(self):
        self.user_api = 'https://www.zhihu.com/api/v4/members/'
        # 要爬取的信息集合
        self.include = 'headline,gender,locations,business,employments,educations,description,answer_count,question_count,articles_count,' \
                       'columns_count,following_count,follower_count,voteup_count,thanked_count'

    def get_user_count(self, collection_name):  # 从数据表内获取除匿名用户外的用户总数
        count = 0
        for item in ZhiHuCommon.ZhiHu_db[collection_name].find():
            if type(item['author_name']) != dict:  # 排除匿名用户
                count += 1
        return count

    def get_user_url(self):
        for item in ZhiHuCommon.ZhiHu_db['answer_backup'].find():
            if type(item['author_name']) != dict:  # 排除匿名用户
                user_url = self.user_api + item['author_url_token'] + '?include={}'.format(self.include)
                yield user_url, item['author_url_token']

    def parse_user_info(self, url):
        try:
            time.sleep(2)  # 增加暂停时间，避免IP被封
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
            print(user_info)  # 调试用
            # ZhiHuCommon.save2mongodb(user_info, user_info['type'])  # 保存到数据库
        except Exception:
            pass

    def user_crawler(self):
        if 'answer_backup' not in ZhiHuCommon.ZhiHu_db.collection_names():  # 如果是第一次运行的时候，备份数据库
            for item in ZhiHuCommon.ZhiHu_db['answer'].find():
                ZhiHuCommon.ZhiHu_db['answer_backup'].insert(item)
        else:
            if ZhiHuCommon.ZhiHu_db['answer_backup'].count() != 0:
                print('正在恢复爬取进度...')
            else:
                print('已经爬取完成...')
        for user_url, author_url_token in self.get_user_url():  # 抽取用户数据，拼接用户主页URL
            # 解析用户数据
            self.parse_user_info(user_url)
            # 实现断点续爬
            ZhiHuCommon.ZhiHu_db['answer_backup'].delete_one({"author_url_token": author_url_token})
            # 负责显示进度条
            num = self.get_user_count('answer') - self.get_user_count('answer_backup')
            count = self.get_user_count('answer')
            ZhiHuCommon.view_bar(num, count)


class ZhiHuColumnCrawler(object):
    def __init__(self):
        self.column_api = 'https://zhuanlan.zhihu.com/api/columns/'

    def get_column_url(self):
        for item in ZhiHuCommon.ZhiHu_db['column_backup'].find():
            column_url = self.column_api + item['column_id']
            yield column_url, item['column_id']

    def parse_column(self, url, column_id):
        try:
            time.sleep(2)  # 增加暂停时间，避免IP被封
            html = ZhiHuCommon.get(url)
            json_data = json.loads(html)
            postTopics = []
            Topics = []
            column_title = json_data['name']
            column_intro = json_data['intro']
            column_followers = json_data['followersCount']
            postsCount = json_data['postsCount']
            for item in json_data['postTopics']:
                postTopics_name = item['name']
                postTopics_count = item['postsCount']
                postTopic = {
                    'postTopics_name': postTopics_name,
                    'postTopics_count': postTopics_count
                }
                postTopics.append(postTopic)
            for topic in json_data['topics']:
                topic_id = topic['id']
                topic_name = topic['name']
                topic_info = {
                    'topic_id': topic_id,
                    'topic_name': topic_name
                }
                Topics.append(topic_info)
            column_info = {
                'type': 'column',
                'column_id': column_id,
                'column_title': column_title,
                'column_intro': column_intro,
                'column_followers': column_followers,
                'postsCount': postsCount,
                'postTopics': postTopics,
                'Topics': Topics
            }
            print(column_info)
            ZhiHuCommon.save2mongodb(column_info, column_info['type'])
        except:
            pass

    def column_crawler(self):
        if 'column_backup' not in ZhiHuCommon.ZhiHu_db.collection_names():  # 如果是第一次运行的时候，备份数据库
            for item in ZhiHuCommon.ZhiHu_db['column'].find():
                ZhiHuCommon.ZhiHu_db['column_backup'].insert(item)
        for column_url, column_id in self.get_column_url():
            self.parse_column(column_url, column_id)
            # 实现断点续爬
            ZhiHuCommon.ZhiHu_db['column_backup'].delete_one({"column_id": column_id})
            # 负责显示进度条
            num = ZhiHuCommon.ZhiHu_db['column'].count() - ZhiHuCommon.ZhiHu_db['column_backup'].count()
            count = ZhiHuCommon.ZhiHu_db['column'].count()
            ZhiHuCommon.view_bar(num, count)


if __name__ == '__main__':
    # TopicCrawler = ZhiHuTopicCrawler()
    # TopicCrawler.topic_crawler()

    # QuestionCrawler = ZhiHuQuestionCrawler()
    # QuestionCrawler.question_crawler()

    AnswerCrawler = ZhiHuAnswerCrawler()
    AnswerCrawler.answer_crawler()

    # UserCrawler = ZhiHuUserCrawler()
    # UserCrawler.user_crawler()

    # ColumnCrawler = ZhiHuColumnCrawler()
    # ColumnCrawler.column_crawler()
