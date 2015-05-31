#!/usr/bin/env python2
# coding: utf-8

import re, urllib2, json, datetime
from bs4 import BeautifulSoup

class Calcium:
    def __init__(self, name, search_at=None):
        self.cache = {}
        if not search_at:
            if not re.compile(r'^[B-KMNP-T][0-9]{9}$').match(name):
                raise ValueError, 'Invalid school code:', name
            self._set_neis_domain(name[0])
            self.code = name
        elif type(search_at) is str:
            self.code = self.find(name, search_at)
        else:
            raise ValueError, 'No (or invalid) arguments specified'

    def find(self, query, dep):
        self._set_neis_domain(dep)
        req = urllib2.Request('http://%s/spr_ccm_cm01_100.do?kraOrgNm=%s' \
                % (self.domain, query)
            )
        res = urllib2.urlopen(req).read()
        j = json.loads(res)
        l = j['resultSVO']['orgDVOList']

        self.findResult = map(lambda i: {
            'name': i['kraOrgNm'],
            'code': i['orgCode'],
            'type': i['schulCrseScCodeNm'],
            'address': i['zipAdres']
            }, l)

        if len(self.findResult) == 1:
            self.code = self.findResult[0]['code']
        else:
            return self.findResult

    def select(self, code):
        self.code = code

    def get(self, year=None, month=None):
        date = datetime.date.today()
        if not year:
            year = date.year
        if not month:
            month = date.month
        if type(year) != type(0) or type(month) != type(0):
            raise ValueError, 'Invalid arguments (int excepted)'

        r = self._get_cache(year, month)
        if not r:
            r = []
        else:
            return r
        
        req = urllib2.Request('http://%s/sts_sci_md00_001.do?schulCode=%s&schulCrseScCode=4&schYm=%04d.%02d' \
            % (self.domain, self.code, year, month)
            )
        res = urllib2.urlopen(req).read()
        soup = BeautifulSoup(res)

        for day in soup.select('.tbl_type3 td div'):
            print day
            if not day or not day.find('<br>'):
                continue

            day = re.sub(r'[①-⑬]+', '', day)
            date = day.split('<br>')[0]
            item = day.split('<br>')[1:]
            r[date] = {}

            for i in range(1, item.length, 2):

                name = re.sub(r'(\[|\])', '', item[i])
                value = [ j for j in item[i+1].split('<br>') if j ]

                if name == '조식':
                    r[date].breakfast = value
                if name == '중식':
                    r[date].lunch = value
                if name == '석식':
                    r[date].dinner = value
  
        self._set_cache(year, month, r)
        return r
        
    def _set_cache(self, year, month, value):
        if not self.cache.get('year'):
            self.cache[year] = {}

        self.cache[year][month] = value

    def _get_cache(self, year, month):
        return self.cache.get('year') and self.cache[year].get('month')

    def _set_neis_domain(self, q):
        #     A : ??
        if q in ['B', 'sen', 'seoul', '서울', '서울특별시']:
            self.domain = 'hes.sen.go.kr'
        elif q in ['C', 'pen', 'busan', '부산', '부산광역시']:
            self.domain = 'hes.pen.go.kr'
        elif q in ['D', 'dge', 'daegu', '대구', '대구광역시', '머구', '대집트']:
            self.domain = 'hes.dge.go.kr'
        elif q in ['E', 'ice', 'incheon', '인천', '인천광역시', '마계']:
            self.domain = 'hes.ice.go.kr'
        elif q in ['F', 'gen', 'gwangju', '광주', '광주광역시', '팡주']:
            self.domain = 'hes.gen.go.kr'
        elif q in ['G', 'dje', 'daejeon', '대전', '대전광역시', '머전']:
            self.domain = 'hes.dje.go.kr'
        elif q in ['H', 'use', 'ulsan', '울산', '울산광역시']:
            self.domain = 'hes.use.go.kr'
        elif q in ['I', 'sje', 'sejong', '세종', '세종시', '세종특별자치시']:
            self.domain = 'hes.sje.go.kr'
        elif q in ['J', 'goe', 'gyeonggi', '경기', '경기도']:
            self.domain = 'hes.goe.go.kr'
        elif q in ['K', 'gwe', 'gangwon', '강원', '강원도']:
            self.domain = 'hes.gwe.go.kr'
        #     L : ??
        elif q in ['M', 'cbe', 'chungbuk', '충북', '충청북도']:
            self.domain = 'hes.cbe.go.kr'
        elif q in ['N', 'cne', 'chungnam', '충남', '충청남도']:
            self.domain = 'hes.cne.go.kr'
        #     O : ??
        elif q in ['P', 'jbe', 'jeonbuk', '전북', '전라북도']:
            self.domain = 'hes.jbe.go.kr'
        elif q in ['Q', 'jne', 'jeonnam', '전남', '전라남도']:
            self.domain = 'hes.jne.go.kr'
        elif q in ['R', 'gbe', 'gyeongbuk', '경북', '경상북도']:
            self.domain = 'hes.gbe.kr'
        elif q in ['S', 'gne', 'gyeongnam', '경남', '경상남도']:
            self.domain = 'hes.gne.go.kr'
        elif q in ['T', 'jje', 'jeju', '제주', '제주도', '탐라', '탐라국']:
            self.domain = 'hes.jje.go.kr'
        else:
            raise NameError, "No NEIS domain for prefix or query '%s' found" % query[0]
