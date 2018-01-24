import json
import zhihu_common
from zhihu_common import mydb
import re

user_begin_url = 'https://www.zhihu.com/api/v4/members/'

# 完整include
# include = 'headline,locations,employments,gender,educations,business,voteup_count,thanked_Count,follower_count,following_count,' \
#           'cover_url,following_topic_count,following_question_count,following_favlists_count,following_columns_count,' \
#           'avatar_hue,answer_count,articles_count,pins_count,question_count,columns_count,commercial_question_count,' \
#           'favorite_count,favorited_count,logs_count,included_answers_count,included_articles_count,included_text,' \
#           'message_thread_token,account_status,is_active,is_bind_phone,is_force_renamed,is_bind_sina,is_privacy_protected,' \
#           'sina_weibo_url,sina_weibo_name,show_sina_weibo,is_blocking,is_blocked,is_following,is_followed,' \
#           'is_org_createpin_white_user,mutual_followees_count,vote_to_count,vote_from_count,thank_to_count,thank_from_count,' \
#           'thanked_count,description,hosted_live_count,participated_live_count,allow_message,industry_category,org_name,' \
#           'org_homepage,badge[?(type=best_answerer)].topics'


include = 'headline,gender,locations,business,employments,educations,description,answer_count,question_count,articles_count,' \
          'columns_count,following_count,follower_count,voteup_count,thanked_count'


def get_zhihu_user_url():
    for item in mydb['zhihu_answer'].find():
        zhihu_user_url = user_begin_url + item['author_url_token'] + '?include={}'.format(include)
        yield zhihu_user_url


def parse_zhihu_user(url):
    html = zhihu_common.get(url)
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
            'headline': re.compile(r'<[^>]+>', re.S).sub('', headline),
            'gender': gender,
            'locations': locations,
            'business': business,
            'employments': employments,
            'educations': educations,
            'description': re.compile(r'<[^>]+>', re.S).sub('', description),
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


def main():
    for zhihu_user_url in get_zhihu_user_url():
        user_info = parse_zhihu_user(zhihu_user_url)
        print(user_info)
        # zhihu_common.save2mongodb(user_info, user_info['type'])


if __name__ == '__main__':
    main()
