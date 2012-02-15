
import re

digital_re = re.compile(r'digital\s?(file)?[.]?')


# Test 300b values
test_300b = 'sd., col., digital file +'
test2_300b = 'sd., b&w., digital file.'
test3_300b = 'b&w., digital'
test4_300b = 'sd., col., digital.'



def validate300b(raw_string):
    good_300b = '%s, %s' % ('digital',digital_re.sub('',raw_string))
    last_char = good_300b[-1]
    if last_char == '+':
         if good_300b[-3] == ',':
             good_300b = good_300b[:-4] + ' + '
         else:
             good_300b = good_300b + ' '
    elif last_char == ',':
        good_300b = good_300b[:-1]
        if good_300b[-1] != '.':
            good_300b += '.'
    return good_300b    
 
