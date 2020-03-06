#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Oct 16 20:33:02 2019

@author: nirmalenduprakash
"""

from IPA import *
#applicationDB=ApplicantDB('/Users/nirmalenduprakash/Documents/Project/IPA/resumes/workex')
#
#os.chdir('/Users/nirmalenduprakash/Documents/Project/IPA/test_sales_resume')
#thisdir=os.getcwd()
#for item in os.walk(thisdir):
#    for file in item[2]:
#            if(file.endswith('.pdf')):
#                res=Resume(thisdir+'/'+file)
#                dict=res.extract(applicationDB.documents)
#                print(file,dict['resume_type'])


roleDB=JobDB('/Users/nirmalenduprakash/Documents/Project/IPA/JobResponsibility')
reqDB=JobDB('/Users/nirmalenduprakash/Documents/Project/IPA/JobRequirement')

#print(roleDB.documents)
job=Job('/Users/nirmalenduprakash/Documents/Project/IPA/Web Developer.pdf')
job.convert()
job.extract(roleDB.documents,reqDB.documents)