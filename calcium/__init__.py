#!/usr/bin/env python2
# coding: utf-8

import re, json, datetime
from bs4 import BeautifulSoup
from collections import defaultdict

try: # py2
    from urllib import urlencode
    from urllib2 import Request, urlopen
except ImportError: # py3
    from urllib.parse import urlencode
    from urllib.request import Request, urlopen

class Calcium:
    def __init__(self, name, search_at=None):
        self.cache = {}
        if not search_at:
            if not re.compile(r'^[B-KMNP-T][0-9]{9}$').match(name):
                raise ValueError('Invalid school code: %s' % name)
            self._set_neis_domain(name[0])
            self.code = name
        elif type(search_at) is str:
            self.code = self.find(name, search_at)
        else:
            raise ValueError('No (or invalid) arguments specified')

    def find(self, query, dep):
        self._set_neis_domain(dep)
        req = Request('http://%s/spr_ccm_cm01_100.do?%s' \
                % (self.domain, urlencode({
                    'kraOrgNm': query
                }))
            )
        res = urlopen(req).read()
        j = json.loads(res)
        l = j['resultSVO']['orgDVOList']

        self.findResult = map(lambda i: {
            'name': i['kraOrgNm'],
            'code': i['orgCode'],
            'type': i['schulCrseScCodeNm'],
            'address': i['zipAdres']
            }, l)

        if len(self.findResult) == 1:
            return self.findResult[0]['code']
        else:
            return None

    def results(self):
        return self.findResult

    def select(self, code):
        self.code = code

    def get(self, year=None, month=None):
        date = datetime.date.today()
        if not year:
            year = date.year
        if not month:
            month = date.month
        if type(year) != int or type(month) != int:
            raise ValueError('Invalid arguments (int excepted)')
        if self.code == None:
            raise ValueError('School not selected (use results() and select())')

        r = self._get_cache(year, month)
        if not r:
            r = {}
        else:
            return r

        req = Request('http://%s/sts_sci_md00_001.do' % self.domain)

        res = urlopen(req, urlencode({
          'schulCode': self.code,
          'schulCrseScCode': 4,
          'ay': year,
          'mm': str(month).zfill(2)
        }))
        res = res.read()
        soup = BeautifulSoup(res)

        for day in soup.select('.tbl_type3 td div'):

            contents = day.contents

            if not day or len(day) <= 1:
                continue

            date = int(contents[0])
            item = contents[2::2]

            r[date] = defaultdict(list)
            name = ''

            for i in item:
                if i.strip('[]') != i:
                    name = i.strip('[]')
                else:
                    r[date][name].append(i)

        self._set_cache(year, month, r)
        return r

    def _set_cache(self, year, month, value):
        if not self.cache.get('year'):
            self.cache[year] = {}

        self.cache[year][month] = value

    def _get_cache(self, year, month):
        return self.cache.get('year') and self.cache[year].get('month')

    def _strip_circles(self, string):
        return re.sub(r'[①-⑬]+', '', string)

    def _set_neis_domain(self, q):
        #     A : ??
        if   q in ['B', 'sen', 'seoul', '서울', '서울특별시']:
            self.domain = 'stu.sen.go.kr'
        elif q in ['C', 'pen', 'busan', '부산', '부산광역시']:
            self.domain = 'stu.pen.go.kr'
        elif q in ['D', 'dge', 'daegu', '대구', '대구광역시', '머구', '대집트']:
            self.domain = 'stu.dge.go.kr'
        elif q in ['E', 'ice', 'incheon', '인천', '인천광역시', '마계']:
            self.domain = 'stu.ice.go.kr'
        elif q in ['F', 'gen', 'gwangju', '광주', '광주광역시', '팡주']:
            self.domain = 'stu.gen.go.kr'
        elif q in ['G', 'dje', 'daejeon', '대전', '대전광역시', '머전']:
            self.domain = 'stu.dje.go.kr'
        elif q in ['H', 'use', 'ulsan', '울산', '울산광역시']:
            self.domain = 'stu.use.go.kr'
        elif q in ['I', 'sje', 'sejong', '세종', '세종시', '세종특별자치시']:
            self.domain = 'stu.sje.go.kr'
        elif q in ['J', 'goe', 'gyeonggi', '경기', '경기도']:
            self.domain = 'stu.goe.go.kr'
        elif q in ['K', 'gwe', 'gangwon', '강원', '강원도']:
            self.domain = 'stu.gwe.go.kr'
        #     L : ??
        elif q in ['M', 'cbe', 'chungbuk', '충북', '충청북도']:
            self.domain = 'stu.cbe.go.kr'
        elif q in ['N', 'cne', 'chungnam', '충남', '충청남도']:
            self.domain = 'stu.cne.go.kr'
        #     O : ??
        elif q in ['P', 'jbe', 'jeonbuk', '전북', '전라북도']:
            self.domain = 'stu.jbe.go.kr'
        elif q in ['Q', 'jne', 'jeonnam', '전남', '전라남도']:
            self.domain = 'stu.jne.go.kr'
        elif q in ['R', 'gbe', 'gyeongbuk', '경북', '경상북도']:
            self.domain = 'stu.gbe.kr'
        elif q in ['S', 'gne', 'gyeongnam', '경남', '경상남도']:
            self.domain = 'stu.gne.go.kr'
        elif q in ['T', 'jje', 'jeju', '제주', '제주도', '탐라', '탐라국']:
            self.domain = 'stu.jje.go.kr'
        else:
            raise NameError("No NEIS domain for prefix or query '%s' found" % query[0])
