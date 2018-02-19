# -*- coding: utf-8 -*-
"""
Spyder Editor

This is a temporary script file.
r"""

import requests
import re
from bs4 import BeautifulSoup
from requests_toolbelt import MultipartEncoder

login_url = r'https://leetcode.com/accounts/login/'
submission_url = r'https://leetcode.com/submissions/'
user_agent = 'Mozilla/5.0 (X11; Linux x86_64; rv:39.0) Gecko/20100101 Firefox/39.0'

headers_base = {
        'Accept':'*/*',
        'Accept-Encoding':'gzip, deflate, br',
        'Accept-Language':'zh-CN,zh;q=0.8,zh-TW;q=0.7,zh-HK;q=0.5,en-US;q=0.3,en;q=0.2',
        'Connection':'keep-alive',
        'Host':'leetcode.com',
        'User-Agent':'Mozilla/5.0 (X11; Linux x86_64…) Gecko/20100101 Firefox/58.0',
        'X-Requested-With':'XMLHttpRequest'
}


class LeetCodeSpider:
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers['User-Agent'] = user_agent
    
    def login(self, username, password):
        self.session.headers['Referer'] = login_url
        self.session.get(login_url)
        token = self.session.cookies['csrftoken']
        
        payload = {
            'login':username,
            'password':password,
            'csrfmiddlewaretoken':token
        }
        
        m = MultipartEncoder(payload)
        self.session.headers['Content-Type'] = m.content_type
        self.session.headers['Content-Length'] = str(m.len)
        r = self.session.post(login_url, data=m)
        if len(r.history) != 0 and str(r.history[0].headers).find('Successfully') != -1:
            print('Login Successfully')
        else:
            print('Login Failed')
        del(self.session.headers['Content-Type'])
        del(self.session.headers['Content-Length'])
        return r
    
    def get_submissions(self,offset = 0, gap = 20, ac_flag = False,stop = None):
        self.session.headers['Referer'] = submission_url
        
        fail_count = 0
        
        while True:
            r = self.session.get('https://leetcode.com/api/submissions/', 
                                 params ={'offset':str(offset), 'limit':str(gap)})
            
            if r.status_code != requests.status_codes.codes.ok:
                print('get fail and state code is ',r.status_code)
                fail_count += 1    
                if fail_count > 10:
                    print('fail count > 10')
                    break
            r_json = r.json()
            submissions_dump = r_json['submissions_dump']
            for submission in submissions_dump:
                if ac_flag:
                    if submission['status_display'] == 'Accepted':
                        yield submission
                else:
                    yield submission
                offset += 1
            if r_json['has_next'] == False:
                break;
    
    def get_problem_description(self, title):
        '''just get the problem description'''
        t = title.strip().lower().replace(' ','-')
        url = "https://leetcode.com/problems/%s/description/" % t
        res = self.session.get(url)
        soup = BeautifulSoup(res.text, 'html.parser')
        return soup.find(attrs={'name':'description'})['content']
    
    def get_problem_and_code(self, url):
        '''get problem and code'''
        res = self.session.get(url)
        soup =BeautifulSoup(res.text, 'html.parser')
        problem_title = soup.title.text
        problem_descripton = soup.find(attrs={'name':'description'})['content']
        pattern = re.compile(r"submissionCode: '(.*?)'")
        code = re.search(pattern, res.text).group(1)
        print(problem_title)
        print(problem_descripton)
        print(code)
        with open('code.cpp', 'w', encoding='utf-8') as f:
            f.write(code)

        return problem_title, problem_descripton, code

spider = LeetCodeSpider()
spider.login(username, password)
url = "https://leetcode.com/submissions/detail/141409877/"
spider.get_problem_and_code(url)
#submissions = list(spider.get_submissions(ac_flag = True, stop = 2))

#for submission in spider.get_submissions(ac_flag=True, stop = 2):
#    title = submission['title']
#    print(title)
#    print(spider.get_problem_description(title))
