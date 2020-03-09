"""
 Create by jiachenx on 2019/3/11
"""
__author__ = 'jiachenx'

import operator

#  generate_detail
# 该函数会比较传入的两个对象的每个参数的异同，将不同的属性返回
def generate_detail(newData, oldData):
        different_parameter = {}
        if str(oldData.__class__.__name__) == str(newData.__class__.__name__):
            for field in oldData.fields:
                if oldData[field] != newData[field]:
                    different_parameter[field] = str(oldData[field]) + \
                        " to " + str(newData[field])
        return different_parameter

def replace_char_for_latex(str,chars):
    for char in chars:
        str =  str.replace(char,'\\'+char)
    return str
