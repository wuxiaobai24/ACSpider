# -*- coding: utf-8 -*-
"""
Spyder Editor

Spider for LeetCode
"""

import requests
import re
from bs4 import BeautifulSoup
from requests_toolbelt import MultipartEncoder
import md2html
import time
import codecs
import os
import argparse


base_url = 'https://leetcode.com'
login_url = r'https://leetcode.com/accounts/login/'
submission_url = r'https://leetcode.com/submissions/'
user_agent = 'Mozilla/5.0 (X11; Linux x86_64; rv:39.0)' \
    ' Gecko/20100101 Firefox/39.0'

with open('./template.md', 'r') as f:
    template = f.read()


def gen_md_text(title, problem, code, lang):
    date_and_time = time.strftime("%Y-%m-%d %H:%M:%S",
                                  time.localtime(time.time()))
    lower_title = title.strip().lower().replace(' ', '-')
    url=  "https://leetcode.com/problems/%s/description/" % lower_title
    s = template % (title, date_and_time,
                    title, url, problem, lang, code)
    return s


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
            attrs={'name': 'description'})['content'].replace('\r\n', '\n')
        pattern = re.compile(r"submissionCode: '(.*?)'")
        code = re.findall(pattern, res.text)[0]
        code = codecs.decode(code, 'unicode-escape')
        return problem_descripton, code

    def update_md(self, ac_flag=True):
        ac = self.get_all_ac_problem()
        for title, problem in ac.items():
            path = title2path(title)
            if os.path.exists(path):
                print('exist',path)
                continue
            slug = ac[title]['stat']['question__title_slug']
            submission = self.get_submission(slug)
            print('%s saving' % title)
            lang = submission['lang']
            problem, code = self.get_problem_and_code(
                    base_url + submission['url'])
            s = gen_md_text(title, problem, code, lang)
            with open(path, 'w') as f:
                f.write(s)
        print('Update Successfully!!')

    def islogin(self, username):
        url = 'https://leetcode.com/api/problems/all/'
        res = self.get(url)
        return res.json()['username'] == username

    def get(self,url):
        self.session.headers['Referer'] = url
        return self.session.get(url)
    
    def get_submission(self, title):
        url = 'https://leetcode.com/api/submissions/%s' % title
        fail_count = 0
        offset, gap = 0, 10
        while True:
            r = self.session.get(
                    url,
                    params={'offset': str(offset), 'limit': str(gap)})
            if r.status_code != requests.status_codes.codes.ok:
                print('get fail and state code is ', r.status_code)
                fail_count += 1
                if fail_count > 10:
                    print('fail count > 10')
                    break
                continue
            
            r_json = r.json()
            submissions_dump = r_json['submissions_dump']
            for submission in submissions_dump:
                if submission['status_display'] == 'Accepted':
                        return submission
            offset += gap


    def get_all_ac_problem(self):
        url = 'https://leetcode.com/api/problems/all'
        res = self.get(url)
        problems = res.json()['stat_status_pairs']
        ac = {}
        for problem in problems:
            if problem['status'] == 'ac':
                ac[problem['stat']['question__title']] = problem
        return ac

def title2path(title: str):
    return './md/' + title.strip().replace(' ', '-') + '.md'


def loginspider(username, passwd):
    spider = LeetCodeSpider()
    spider.login(username, passwd)
    return spider


def main():
    loginspider().update_md()
    mdfiles = os.listdir('./md')
    for file in mdfiles:
        html_name = '%s/%s.html' % ('./html', file[:-3])
        if not os.path.isdir(file) and not os.path.exists(html_name):
            md2html.md2html(file, html_name)

def parse_arg():
    parser = argparse.ArgumentParser()
    parser.add_argument("-u", "-username", help='username',
                        type = str, dest='username', required=True)
    parser.add_argument("-p", "-passwd", help='password',
                        type = str, dest='passwd', required=True)
    parser.add_argument("-update", type=str, help='update', dest="update", 
                        choices=['md', 'html'])
    return parser.parse_args()


if __name__ == '__main__':
    args = parse_arg()
    print(args)
    spider = loginspider(args.username, args.passwd)
    spider.update_md()
    if args.update == 'html':
        for file in mdfiles:
            html_name = '%s/%s.html' % ('./html', file[:-3])
            if not os.path.isdir(file) and not os.path.exists(html_name):
                md2html.md2html(file, html_name)
    
