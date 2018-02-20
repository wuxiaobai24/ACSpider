# -*- coding: utf-8 -*-
"""
Spyder Editor

Spider for LeetCode
r"""

import requests
import re
from config import get_last_url, get_user, update_last_url
from bs4 import BeautifulSoup
from requests_toolbelt import MultipartEncoder
import md2html
import time
import codecs
import os

base_url = 'https://leetcode.com'
login_url = r'https://leetcode.com/accounts/login/'
submission_url = r'https://leetcode.com/submissions/'
user_agent = 'Mozilla/5.0 (X11; Linux x86_64; rv:39.0)' \
    ' Gecko/20100101 Firefox/39.0'
last_url = base_url + get_last_url()
user = get_user()


class LoginError(Exception):
    pass


class LeetCodeSpider:

    def __init__(self):
        self.session = requests.Session()
        self.session.headers['User-Agent'] = user_agent

    def login(self, username, password):
        self.session.headers['Referer'] = login_url
        self.session.get(login_url)
        token = self.session.cookies['csrftoken']

        # bulid payload and set headers
        payload = {
            'login': username,
            'password': password,
            'csrfmiddlewaretoken': token
        }
        m = MultipartEncoder(payload)
        self.session.headers['Content-Type'] = m.content_type
        self.session.headers['Content-Length'] = str(m.len)

        r = self.session.post(login_url, data=m)

        if len(r.history) != 0 \
                and str(r.history[0].headers).find('Successfully') != -1:
            print('Login Successfully')
        else:
            print('Login Failed')
        del(self.session.headers['Content-Type'])
        del(self.session.headers['Content-Length'])

    def get_submissions_generator(self, offset=0, gap=20, ac_flag=True):
        fail_count = 0
        first = True
        while True:
            self.session.headers['Referer'] = submission_url
            r = self.session.get(
                'https://leetcode.com/api/submissions/',
                params={'offset': str(offset), 'limit': str(gap)})

            if r.status_code != requests.status_codes.codes.ok:
                print('get fail and state code is ', r.status_code)
                fail_count += 1
                if fail_count > 10:
                    print('fail count > 10')
                    break
            r_json = r.json()
            submissions_dump = r_json['submissions_dump']

            if first:
                update_last_url(submissions_dump[0]['url'])

            for submission in submissions_dump:
                if ac_flag:
                    if submission['status_display'] == 'Accepted':
                        yield submission
                else:
                    yield submission
                if submission['url'] == last_url:
                    r_json['has_next'] = False
                    break

                offset += 1
            if r_json['has_next'] is False:
                break

    def get_problem_description(self, title):
        '''just get the problem description'''
        t = title.strip().lower().replace(' ', '-')
        url = "https://leetcode.com/problems/%s/description/" % t
        res = self.session.get(url)
        soup = BeautifulSoup(res.text, 'html.parser')
        return soup.find(attrs={'name': 'description'})['content']

    def get_problem_and_code(self, url):
        '''get problem and code'''
        time.sleep(0.2)
        res = self.session.get(url)
        try:
            res.raise_for_status()
        except Exception as e:
            print(e.args)
            time.sleep(1)
            return self.get_problem_and_code(url)

        soup = BeautifulSoup(res.text, 'html.parser')
        # problem_title = soup.title.text
        problem_descripton = soup.find(
            attrs={'name': 'description'})['content'].replace('/r/n', '/n')
        pattern = re.compile(r"submissionCode: '(.*?)'")
        code = re.findall(pattern, res.text)[0]
        code = codecs.decode(code, 'unicode-escape')
        return problem_descripton, code

    def update_md(self, ac_flag=True):
        with open('./template.md', 'r') as f:
                template = f.read()

        for submission in self.get_submissions_generator():
            title = submission['title']
            path = title2path(title)
            if os.path.exists(path):
                break
            print('%s saving' % title)
            lang = submission['lang']
            problem, code = self.get_problem_and_code(
                    base_url + submission['url'])
            s = template % (title, problem, lang, code)
            with open(path, 'w') as f:
                f.write(s.replace('/r/n', '/n'))
        print('Update Successfully!!')


def title2path(title: str):
    return './md/' + title.strip().lower().replace(' ', '-') + '.md'


def loginspider():
    spider = LeetCodeSpider()
    spider.login(user['username'], user['password'])
    return spider


def main():
    loginspider().update_md()
    mdfiles = os.listdir('./md')
    for file in mdfiles:
        html_name = '%s/%s.html' % ('./html', file[:-3])
        if not os.path.isdir(file) and not os.path.exists(html_name):
            md2html.md2html(file)


if __name__ == '__main__':
    main()
