import json
import zhihu_common
from zhihu_common import mydb
import string
import random
import re

question_begin_url = 'https://www.zhihu.com/api/v4/questions/'

include = 'data[*].is_normal,voteup_count,content'
limit = 20


def random_str():  # 生成随机字符串
    random_str_len = 10
    random_str = ''.join(random.sample(string.ascii_letters + string.digits, random_str_len))
    return random_str


def get_zhihu_question_id():  # 从MongoDB数据库中取出问题数据
    for item in mydb['zhihu_question'].find():
        yield item['question_id'], item['question_title']


def get_answer_count(url):  # 得到问题回答的总数
    html = zhihu_common.get(url)
    json_data = json.loads(html)
    answer_count = json_data['paging']['totals']
    return answer_count


def get_zhihu_answer_url(question_id, question_title):  # 拼接问题URL
    question_start_url = question_begin_url + '{}/answers?include={}&offset=0&limit={}&sort_by=default'.format(
        question_id, include, limit)
    answer_count = get_answer_count(question_start_url)
    max_offset = int(answer_count / limit) * limit
    for offset in range(0, max_offset, limit):
        question_url = question_begin_url + '{}/answers?include={}&offset={}&limit={}&sort_by=default'.format(
            question_id, include, offset, limit)
        yield question_title, question_url


def parse_zhihu_answer(url):
    html = zhihu_common.get(url)
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
                    'random_number': random_str()
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


def main():
    for question_id, question_title in get_zhihu_question_id():
        for question_title, question_url in get_zhihu_answer_url(question_id, question_title):
            for answer_info in parse_zhihu_answer(question_url):
                print(answer_info)
                zhihu_common.save2mongodb(answer_info, answer_info['type'])


if __name__ == '__main__':
    main()
