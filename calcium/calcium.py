#!/usr/bin/env python2
# coding: utf-8

import re, urllib2, json, datetime
from bs4 import BeautifulSoup

class Calcium:
    def __init__(self, name, search_at=None):
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
            self.code = self.findResult[0].code
        else:
            return self.findResult

    def select(self, code):
        self.code = code

    def get(self, year=None, month=None):
        date = datetime.date.today()
        if type(year) !== 'int' or type(month) !== 'int':
            raise ValueError, 'Invalid arguments (int excepted)'
        if not year:
            year = date.year
        if not month:
            month = date.month
        
        req = urllib2.Request('http://%s/sts_sci_md00_001.do?schulCode=%ㄴ&schulCrseScCode=4&schYm=%04d.%02d' \
            % (self.domain, self.code, year, month)
            )

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
