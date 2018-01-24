import json
import zhihu_common
from zhihu_common import mydb

topic_begin_url = 'https://www.zhihu.com/api/v4/topics/'

question_level = 1
limit = 5
max_offset = 20  # 最大为1000


def get_zhihu_topic_id():
    for item in mydb['zhihu_topic_list'].find():
        if item['topic_level'] == question_level:
            yield item['topic_id'], item['topic_name']


def parse_topic(url, topic_id, topic_name):
    html = zhihu_common.get(url)
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
                zhihu_common.save2mongodb(question_info, question_info['type'])
            elif item['target'].get('column'):
                column_title = item['target']['column']['title']
                column_id = item['target']['column']['id']
                author_name = item['target']['column']['author']['name']
                author_url_token = item['target']['column']['author']['url_token']
                column_info = {
                    'type': item['target']['column']['type'],
                    'column_title': column_title,
                    'column_id': column_id,
                    'topic_name': topic_name,
                    'topic_id': topic_id,
                }
                print(column_info)
                # zhihu_common.save2mongodb(column_info, column_info['type'])
                user_info = {
                    'type': item['target']['column']['author']['type'],
                    'author_name': author_name,
                    'author_url_token': author_url_token
                }
                print(user_info)
                # zhihu_common.save2mongodb(user_info, user_info['type'])
    except:
        pass


def get_zhihu_question_list():
    for topic_id, topic_name in get_zhihu_topic_id():
        for offset in range(0, max_offset, limit):
            url = topic_begin_url + '{}/feeds/essence?limit={}&offset={}'.format(topic_id, limit, offset)
            parse_topic(url, topic_id, topic_name)


def main():
    get_zhihu_question_list()


if __name__ == '__main__':
    main()
