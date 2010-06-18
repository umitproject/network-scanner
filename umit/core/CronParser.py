#!/usr/bin/env python
##
## CronParser.py
## 
## Copyright (C) 2006 Adriano Monteiro Marques
## This program is free software; you can redistribute it and/or modify
## it under the terms of the GNU General Public License as published by
## the Free Software Foundation; either version 2 of the License, or
## (at your option) any later version.
## 
## This program is distributed in the hope that it will be useful,
## but WITHOUT ANY WARRANTY; without even the implied warranty of
## MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
## GNU General Public License for more details.
## 
## You should have received a copy of the GNU General Public License
## along with this program; if not, write to the Free Software
## Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA 02111-1307 USA
##

import re

class CronParser:
    weekdays = {0:'SUN',
                1:'MON',
                2:'TUE',
                3:'WED',
                4:'THU',
                5:'FRI',
                6:'SAT',
                7:'SUN'}

    months = {1:'JAN',
              2:'FEB',
              3:'MAR',
              4:'APR',
              5:'MAY',
              6:'JUN',
              7:'JUL',
              8:'AUG',
              9:'SEP',
              10:'OCT',
              11:'NOV',
              12:'DEC'}
    
    re_number = '\d{1,2}'
    re_interval = re.compile('^(%s-%s)$' % (re_number, re_number))
    re_separated = re.compile('^(%s,%s)$' % (re_number, re_number))
    re_full = re.compile('^(\*)$')
    re_alone = re.compile('^(\d+)$')
    re_intercalated = re.compile('^(\d+)-(\d+)\b?/(\d+)$')
    re_full_intercalated = re.compile('^[\*]\b?/(\d+)$')
    re_zero_full_intercalated = re.compile('^0\b?/(\d+)$')
        
    def parse(self, expression, start=1, end=31, zero_full=False):
        result = []
        #expression_parts = expression.split(';')
        expression_parts = expression.split(',')

        for exp in expression_parts:
            # If it's full, don't verify the rest
            if self.re_full.match(exp):
                return range(start, end + 1)
            elif exp == '0' and zero_full:
                return range(start, end + 1)
            #elif exp == '0' and not zero_full: # what is this for ?
            #    return start
            elif self.re_full_intercalated.match(exp) or\
                     (self.re_zero_full_intercalated.match(exp) and zero_full):
                try:
                    step = int(self.re_full_intercalated.match(exp).groups()[0])
                except:
                    raise Exception("Wrong step!")
            
                return range(start, end + 1, step)
            elif self.re_interval.match(exp):
                intervals = self.re_interval.match(exp).groups()
                
                for inter in intervals:
                    numbers = re.findall("(%s)" % self.re_number, inter)
                    if len(numbers) != 2:
                        raise Exception("")
                
                    numbers_range = range(int(numbers[0]), int(numbers[1])+1)
                    result += numbers_range
            elif self.re_intercalated.match(exp):
                i = self.re_intercalated.match(exp).groups()
                result += range(int(i[0]),int(i[1]),int(i[2]))
            elif self.re_alone.match(exp):
                result.append(int(exp))
            else:
                raise Exception("Wrong parameter: '%s'" % exp)

        res = []
        for i in result:
            if not start <= i <= end:
                raise Exception("Expression '%s' out of boundaries. Start at \
%s until %s" % (i, start, end))

            if i not in res:
                res.append(i)
        del(result)
    
        res.sort()
        return res

    def parse_day(self, expression):
        return self.parse(expression, 1, 31)

    def parse_month(self, expression):
        return self.parse(self.__convert_expression(expression, self.months), 1, 12)

    def parse_hour(self, expression):
        return self.parse(expression, 0, 23)

    def parse_minute(self, expression):
        return self.parse(expression, 0, 59)

    def parse_weekday(self, expression):
        return self.parse(self.__convert_expression(expression, self.weekdays), 0, 7)

    def __convert_expression(self, expression, conv_dic):
        expression = expression.upper()
        for i in conv_dic:
            expression = str(i).join(expression.split(conv_dic[i]))
        return expression

if __name__ == '__main__':
    print "Result:", CronParser().parse('1-5/2,10-20/3,25-31')
    print "Result DAY:", CronParser().parse_day('1-5/2,10-20/3,25-31')
    print "Result: MONTH", CronParser().parse_month('jan-aug')
    print "Result: HOUR", CronParser().parse_hour('1-12/2')
    print "Result: MINUTE", CronParser().parse_minute('1-5/2,10-20/3,25-31')
    print "Result: WEEKDAY", CronParser().parse_weekday('mon-sat')
    print "Result: MINUTE", CronParser().parse_minute('0,30')
    print "Result: HOUR", CronParser().parse_hour('0')
