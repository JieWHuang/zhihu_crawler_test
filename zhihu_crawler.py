import requests
import pymongo
import json
import time
import string
import random
import re


class ZhiHuCommon(object):
    '''爬虫通用函数类'''
    headers = {
        'Cookie': 'q_c1=1883f1840aae4da282d328092b586954|1514120291000|1514120291000;'
                  ' __utmz=51854390.1514120292.1.1.utmcsr=baidu|utmccn=(organic)|utmcmd=organic;'
                  ' _zap=084caaf9-3293-40b4-801b-29a61c87a04a; aliyungf_tc=AQAAAPRB6x2dgwwA/k7T3zehfNVlrCWF;'
                  ' l_n_c=1; l_cap_id="MGFiM2M0MGVmOGQ5NDA1YWFmOWI1MzQyMmFmNmUyMGM=|1516372907|7e2585641df1410ea469fa764ec9a57d480917fe";'
                  ' r_cap_id="YzI2NDBiZWFiMWYxNGExZDg1MjAzMjY5MTI3NTgwMmU=|1516372907|60207a4912110eb8457a69b79b9f2baaad4bf204";'
                  ' cap_id="YzdmNmFlZjIzNjFhNGIxZmEyNjkyZGVhZmVjNmY3ZmM=|1516372907|d7e523abe32982696a07048f416a0bf750bf5fae";'
                  ' n_c=1; d_c0="ADBte0HLAw2PTtJd_5kMd03T8T8o8JKTEWI=|1516372908"; _xsrf=d2e2e2ce-72d2-414f-9fec-f9db9a42d3e7;'
                  ' capsion_ticket="2|1:0|10:1516372936|14:capsion_ticket|44:ZGQ1N2QwYWNhZDM4NDg3Y2JlYTQyMjNiY2IwN2ZjYTM='
                  '|b6be1ad61612c5f74665cebb94d6c2dac0824312a29e40582a502dcc4c4c9c9a";'
                  ' z_c0="2|1:0|10:1516372942|4:z_c0|92:Mi4xdkpOZEF3QUFBQUFBTUcxN1Fjc0REU1lBQUFCZ0FsVk56bEZQV3dBb3R2Q2VoMzlnUUFYb05rL'
                  'TZLS2JUSC1Sa1BB|ba39ec284785b5e9b20f010f7d6d51c3da0f00ee09d1899ddc4edfdd00d0226a";'
                  ' __utma=51854390.1991264370.1514120292.1514120292.1516372944.2; __utmb=51854390.0.10.1516372944;'
                  ' __utmc=51854390; __utmv=51854390.100--|2=registration_date=20160818=1^3=entry_date=20160818=1',
        'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) '
                      'Chrome/63.0.3239.132 Safari/537.36',
    }  # 请求头，通过Cookie登录知乎网
    data = {'_xsrf': 'd2e2e2ce-72d2-414f-9fec-f9db9a42d3e7'}  # POST请求需要传入的参数
    client = pymongo.MongoClient('localhost', 27017)  # 连接MongoDB数据库
    mydb = client['mydb']  # 创建数据库
    max_count = 5  # 最大尝试次数

    @staticmethod
    def get(url, count=1):  # GET请求
        print('Crawling...', url)
        print('Trying Count...', count)
        if count >= ZhiHuCommon.max_count:
            print('Tried Too Many Times')
            return None
        try:
            response = requests.get(url, headers=ZhiHuCommon.headers)
            if response.status_code == 200:
                response.encoding = response.apparent_encoding  # 确保中文能正常显示
                return response.text
            return None
        except Exception:  # 若出现异常，则再次尝试，若尝试5次还是失败，则返回None
            print('GET Error! Retrying...')
            count += 1
            return ZhiHuCommon.get(url, count)

    @staticmethod
    def post(url, count=1):  # POST请求
        print('Crawling...', url)
        print('Trying Count...', count)
        if count >= ZhiHuCommon.max_count:
            print('Tried Too Many Times')
            return None
        try:
            response = requests.post(url, data=ZhiHuCommon.data, headers=ZhiHuCommon.headers)
            if response.status_code == 200:
                response.encoding = response.apparent_encoding  # 确保中文能正常显示
                return response.text
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
                    print(data['topic_name'], 'Saving to MongoDB Successfully...')
                else:
                    print(data['topic_name'], 'Saving to MongoDB Failed...')
            except:
                pass
        elif type == 'question':
            try:
                if ZhiHuCommon.mydb['zhihu_question'].update({'question_id': data['question_id']}, {'$set': data},
                                                             True):
                    print(data['question_title'], 'Saving to MongoDB Successfully...')
                else:
                    print(data['question_title'], 'Saving to MongoDB Failed')
            except:
                pass
        elif type == 'column':
            try:
                if ZhiHuCommon.mydb['zhihu_column'].update({'column_title': data['column_title']}, {'$set': data},
                                                           True):
                    print(data['column_title'], 'Saving to MongoDB Successfully...')
                else:
                    print(data['column_title'], 'Saving to MongoDB Failed')
            except:
                pass
        elif type == 'people':
            try:
                if ZhiHuCommon.mydb['zhihu_people'].update({'author_url_token': data['author_url_token']},
                                                           {'$set': data},
                                                           True):
                    print(data['author_name'], 'Saving to MongoDB Successfully...')
                else:
                    print(data['author_name'], 'Saving to MongoDB Failed')
            except:
                pass
        elif type == 'answer':
            try:
                if ZhiHuCommon.mydb['zhihu_answer'].update({'author_url_token': data['author_url_token']},
                                                           {'$set': data},
                                                           True):
                    print(data['author_name'], 'Saving to MongoDB Successfully...')
                else:
                    print(data['author_name'], 'Saving to MongoDB Failed')
            except:
                pass


class ZhiHuTopicCrawler(object):
    def __init__(self):
        self.start_url = 'https://www.zhihu.com/topic/19776749/organize/entire'
        self.max_level = 2  # 设置爬取深度

    def get_first_level_topic_url(self, url):  # 广度优先遍历根话题下第一层话题
        topic_level = 1  # 设置第一层话题的深度为1
        html = ZhiHuCommon.post(url)  # 知乎话题树的请求方式是POST
        json_data = json.loads(html)  # 解析json网页内容
        for item in json_data['msg'][1]:
            topic_name = item[0][1]  # 话题名称
            topic_id = item[0][2]  # 话题id
            if topic_id != '19776751':  # 「未归类」话题，多是话题别名，不作考虑
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
                yield self.start_url + '?child=&parent={}'.format(topic_id), topic_level + 1  # 生成第二层话题的地址和深度

    def get_topic_info(self, url, topic_level):  # 深度优先遍历
        # time.sleep(1)
        try:
            if topic_level <= self.max_level:  # 判断话题爬虫深度
                html = ZhiHuCommon.post(url)
                json_data = json.loads(html)
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
        except:
            print('Get_Topic_Info Error!')  # 若发生异常，则重新调用方法

    def topic_crawler(self):
        for url, topic_level in self.get_first_level_topic_url(self.start_url):
            self.get_topic_info(url, topic_level)


class ZhiHuQuestionCrawler(object):
    def __init__(self):
        self.topic_begin_url = 'https://www.zhihu.com/api/v4/topics/'
        self.topic_level = 1  # 设置爬取深度
        self.limit = 20  # 设置每页展示信息个数
        self.max_offset = 200  # 设置最大页数，最大为1000

    def get_zhihu_topic(self):  # 用生成器的方式从MongoDB数据库中取出话题数据
        for item in ZhiHuCommon.mydb['zhihu_topic'].find():
            if item['topic_level'] == self.topic_level:
                yield item['topic_id'], item['topic_name']

    def parse_topic(self, url, topic_id, topic_name):  # 解析话题URL，得到问题、专栏、用户数据
        html = ZhiHuCommon.get(url)
        json_data = json.loads(html)
        try:
            for item in json_data['data']:
                if item['target'].get('question'):
                    question_title = item['target']['question']['title']
                    question_id = item['target']['question']['id']
                    question_info = {
                        'type': item['target']['question']['type'],
                        'question_title': question_title,
                        'question_id': question_id,
                        'topic_name': topic_name,
                        'topic_id': topic_id
                    }
                    print(question_info)
                    ZhiHuCommon.save2mongodb(question_info, question_info['type'])
                elif item['target'].get('column'):
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
                    print(column_info)
                    ZhiHuCommon.save2mongodb(column_info, column_info['type'])
                    user_info = {
                        'type': item['target']['column']['author']['type'],
                        'author_name': author_name,
                        'author_url_token': author_url_token
                    }
                    print(user_info)
                    ZhiHuCommon.save2mongodb(user_info, user_info['type'])
        except:
            pass

    def question_crawler(self):
        for topic_id, topic_name in self.get_zhihu_topic():
            for offset in range(0, self.max_offset, self.limit):  # 生成话题URL
                url = self.topic_begin_url + '{}/feeds/essence?limit={}&offset={}'.format(topic_id, self.limit, offset)
                self.parse_topic(url, topic_id, topic_name)


class ZhiHuAnswerCrawler(object):
    def __init__(self):
        self.question_begin_url = 'https://www.zhihu.com/api/v4/questions/'
        self.include = 'data[*].is_normal,voteup_count,content'
        self.limit = 20

    def random_str(self):  # 生成随机字符串
        random_str_len = 10
        random_str = ''.join(random.sample(string.ascii_letters + string.digits, random_str_len))
        return random_str

    def get_question_id(self):  # 从MongoDB数据库中取出问题数据
        for item in ZhiHuCommon.mydb['zhihu_question'].find():
            yield item['question_id'], item['question_title']

    def get_answer_count(self, url):  # 得到问题回答的总数
        html = ZhiHuCommon.get(url)
        json_data = json.loads(html)
        answer_count = json_data['paging']['totals']
        return answer_count

    def get_answer_url(self, question_id, question_title):  # 拼接问题URL
        question_start_url = self.question_begin_url + '{}/answers?include={}&offset=0&limit={}&sort_by=default'.format(
            question_id, self.include, self.limit)
        answer_count = self.get_answer_count(question_start_url)
        max_offset = int(answer_count / self.limit) * self.limit
        for offset in range(0, max_offset, self.limit):
            question_url = self.question_begin_url + '{}/answers?include={}&offset={}&limit={}&sort_by=default'.format(
                question_id, self.include, offset, self.limit)
            yield question_title, question_url

    def parse_answer(self, url):
        html = ZhiHuCommon.get(url)
        json_data = json.loads(html)
        try:
            for item in json_data['data']:
                author_name = item['author']['name']
                author_url_token = item['author']['url_token']
                question_title = item['question']['title']
                answer_content = re.compile(r'<[^>]+>', re.S).sub('', item['content']).replace('\n', ' ')
                answer_voteup_count = item['voteup_count']
                if author_name == '匿名用户':
                    author_name = {
                        'author_type': '匿名用户',
                        'random_number': self.random_str()
                    }
                    author_url_token = '无'
                answer_info = {
                    'type': item['type'],
                    'author_name': author_name,
                    'author_url_token': author_url_token,
                    'question_title': question_title,
                    'answer_content': answer_content,
                    'answer_content_length': len(answer_content),
                    'answer_voteup_count': answer_voteup_count
                }
                yield answer_info
        except:
            pass

    def answer_crawler(self):
        for question_id, question_title in self.get_question_id():
            for question_title, question_url in self.get_answer_url(question_id, question_title):
                for answer_info in self.parse_answer(question_url):
                    print(answer_info)
                    ZhiHuCommon.save2mongodb(answer_info, answer_info['type'])


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

    def get_user_url(self):
        for item in ZhiHuCommon.mydb['zhihu_answer'].find():
            if len(item['author_name']) != 2:
                zhihu_user_url = self.user_begin_url + item['author_url_token'] + '?include={}'.format(self.include)
                yield zhihu_user_url

    def parse_user_info(self, url):
        html = ZhiHuCommon.get(url)
        json_data = json.loads(html)
        try:
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
            return user_info
        except Exception as e:
            pass

    def user_crawler(self):
        for user_url in self.get_user_url():
            user_info = self.parse_user_info(user_url)
            print(user_info)
            ZhiHuCommon.save2mongodb(user_info, user_info['type'])


if __name__ == '__main__':
    # ZhiHuTopicCrawler = ZhiHuTopicCrawler()
    # ZhiHuTopicCrawler.topic_crawler()

    # ZhiHuQuestionCrawler = ZhiHuQuestionCrawler()
    # ZhiHuQuestionCrawler.question_crawler()

    # ZhiHuAnswerCrawler = ZhiHuAnswerCrawler()
    # ZhiHuAnswerCrawler.answer_crawler()

    ZhiHuUserCrawler = ZhiHuUserCrawler()
    ZhiHuUserCrawler.user_crawler()
