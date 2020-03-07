#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Oct 19 12:31:32 2019

@author: nirmalenduprakash
"""
import json
from sklearn.metrics.pairwise import cosine_similarity,euclidean_distances
from sklearn.feature_extraction.text import TfidfVectorizer
import numpy as np
import re
import nltk
import random
import datetime
import ast
import string
from nltk.stem import WordNetLemmatizer
from nltk import word_tokenize

np.random.seed(123)

class CoverLetter:

    def __init__(self,para1,para2,para3,para4):
        
#        jobs = Job.query.filter_by().all()
#        resume =  Resume.query.filter_by().first()
#        
#        for job in jobs:
#            job[""]
#        with open(jobPath,'r',encoding="utf-8") as f:
#            self.job=json.loads(f.read())
#        with open(resumePath,'r',encoding="utf-8") as f:
#            self.resume=json.loads(f.read())  
        
#        self.resume=json.load(resumePath)
        self.para1=para1
        self.para2=para2
        self.para3=para3
        self.para4=para4
        
        self.jobtype=''
        self.jobfield=''
        self.jobfieldtypes=['AI','software']
        self.resumetype=''
        self.years=''
        self.university=''
        self.degreeyear=''
        self.workexline1=''
        self.workexline2=''
        self.email=''
        self.phoneNumber=''
        self.totalexp=0
        self.company=''
        self.companyList=''
        
    def removedot(self,doc):
        tokens = word_tokenize(doc)
        toks = [re.sub(r'([^\u2022]*\u2022.*?)', ' ', t) for t in tokens]
        return " ".join(toks)

    def LemTokens(self,tokens):
        lemmer = nltk.stem.WordNetLemmatizer()
        return [lemmer.lemmatize(token) for token in tokens] 
    
    def LemNormalize(self,text):
        remove_punct_dict = dict((ord(punct), None) for punct in string.punctuation)
        return self.LemTokens(nltk.word_tokenize(text.lower().translate(remove_punct_dict)))

    def create_letter(self,resume,jobs):
        TfidfVec = TfidfVectorizer(tokenizer=self.LemNormalize, stop_words='english')
        
        self.resume=resume
        self.jobs=jobs
        print('Extracting email...')
        try:
            if(self.resume['email']!=''):
                self.email=self.resume['email']
        except Exception as e:
            # raise(e)
            print('Error extracting email') 

        print('Extracting phone...')
        try:            
            if(self.resume['phone']!=''):    
                self.phoneNumber=self.resume['phone']
        except Exception as e:
            # raise(e)
            print('Error extracting phone')        

        print('Extracting json from project and education experience...')
        try:            
            education=ast.literal_eval(self.resume['education_experience'])
            print(education)
            self.degreeYear=education[0]['date']
            self.university=education[0]['school']
        except Exception as e:
            # raise(e)
            print('Error extracting project and education')    

        print('setting derived fields...')
        try:
            self.resumetype=self.resume['type']
            if(self.resumetype=='UX'):
                self.resumetype='UX designer'
            elif(self.resumetype=='AI'):
                self.resumetype='data scientist'
        except Exception as e:
            # raise(e)
            print('Error setting derived fields')            
        
        cover_letters=[]
        
        for job in self.jobs: 
            self.totexp=0
            print('Extracting job information...')
            try:
                print(ast.literal_eval(job['description']))
                print("1")
                print(ast.literal_eval(job['requirement']))
                print("2")
                self.job=job
                role=ast.literal_eval(job['description'])
                req=ast.literal_eval(job['requirement'])
                roledesc=None
                reqdesc=None
                print("123")
                self.jobtype=job['type']
                print(self.jobtype)
                if(self.jobtype=='AI'):
                    self.jobfield=self.jobfieldtypes[0]
                    self.jobtype='data scientist'
                else:
                    self.jobfield=self.jobfieldtypes[1]
                    self.jobtype='software engineer'
                
                
                bulletregex=re.compile('/\d\.\s+|[a-z]\)\s+|•\s+|[A-Z]\.\s+|[IVX]+\.\s+/g')
        
                if(len(list(role.keys()))>0):
                    roledesc=' '.join([' '.join(v) for k,v in role.items()])
                    
                if(len(list(req.keys()))>0):
                    reqdesc=' '.join([' '.join(v) for k,v in req.items()]) 
            except Exception as e:
                # raise(e)
                print('Error extratcing job information')               

            print('Extracting project information...')
            try:
                projects=ast.literal_eval(self.resume['project_experience'])
                projdesc=[[self.removedot(k['summary'])] for k in projects if 'summary' in k]
                exp=[k['date'] for k in projects if 'date' in k ]
                scores=[]
                indx=0
                
                for p in projdesc:
                    sent=nltk.sent_tokenize('.'.join(p))
                    print(sent)
                    if(len(sent)<2):
                        projdesc.remove(p)
                        del exp[indx]
                    else:
                        score=0
                        if(roledesc is not None):
                            tfidf=TfidfVec.fit_transform([roledesc,'.'.join(p)])
                            score=0.5*cosine_similarity(tfidf[-1],tfidf)[0][0]
                        if(reqdesc is not None):    
                            tfidf=TfidfVec.fit_transform([reqdesc,'.'.join(p)])
                            score+=cosine_similarity(tfidf[-1],tfidf)[0][0]
                        scores.append(score)
                        indx+=1
                print('Extracting total workex and relevant workex years...')
                try:
                    for ex in exp:
                        if(ex!=''):
                            if('present' in ex.lower().strip()):
                                ex=ex.lower().replace('present',str(datetime.datetime.now().year))
                            wyears=[w for w in ex.strip() if w.isnumeric()]
                            if(len(wyears)==4):
                                wyears=''.join(wyears)
                                wexp=1
                            else:
                                wyears=[''.join(wyears[:4]),''.join(wyears[4:])]
                                wexp=int(wyears[len(wyears)-1])-int(wyears[0])            
                             
                            self.totalexp+=wexp
                    if(len(scores)>1):
                        self.years=exp[np.argmax(scores)]
                    else:
                        self.years=exp[0]    
                except Exception as e:
                    # raise(e)
                    print('Error extracting workex')    

                print('Forming workex sentences...')
                try:  
                    if(len(scores)>1):      
                        projdesc=projdesc[np.argmax(scores)]
                        self.company=[k['company'] for k in projects if 'company' in k][np.argmax(scores)]
                    else:
                        projdesc=projdesc[0]
                        self.company=[k['company'] for k in projects if 'company' in k][0]
                    # print(self.company)
                    self.companyList=','.join([k['company'] for k in projects if 'company' in k])

                    sents=nltk.sent_tokenize(' '.join(projdesc).replace('..','.'))    
                    if(len(sents)>0):
                        #identify top 2 matching sentences
                        scores=[]
                        for sent in sents:          
                            score=0
                            if(roledesc is not None):
                                tfidf=TfidfVec.fit_transform([roledesc,sent])
                                score=0.5*cosine_similarity(tfidf[-1],tfidf)[0][0]
                            if(reqdesc is not None):    
                                tfidf=TfidfVec.fit_transform([reqdesc,sent])
                                score+=cosine_similarity(tfidf[-1],tfidf)[0][0]
                            scores.append(score) 
                        
                        # self.workexline1=sents[np.argmax(scores)] 
                        sortedScores=np.argsort(scores)
                        # self.workexline1=sents[sortedScores[-1]]
                        # self.workexline2=sents[sortedScores[-2]]
                        if len(sortedScores) >= 2:
                            self.workexline1=sents[sortedScores[-1]]
                            self.workexline2=sents[sortedScores[-2]]
                        else:
                            self.workexline1=sents[sortedScores[-1]]
                        # sents.remove(self.workexline1)
                        # self.workexline2=sents[np.argmax(scores)] 
                        
                        if self.workexline1:
                            while('  ' in self.workexline1):
                                self.workexline1=self.workexline1.replace('  ',' ') 
                            if(self.workexline1[-1]=='.'):
                                self.workexline1=self.workexline1[:-1]
                        if self.workexline2:
                            while('  ' in self.workexline2):
                                self.workexline2=self.workexline2.replace('  ',' ')  
                            if(self.workexline2[-1]=='.'):
                                self.workexline2=self.workexline2[:-1]    
                except Exception as e:
                    print('Error forming workex sentences')
                if('present' in self.years.strip().lower()):
                    self.years='Since '+ self.years.lower().replace('present','')
                elif(self.years!=''):
                    self.years=[w for w in self.years if w.isnumeric()]
                    # print(self.years)
                    if(len(self.years)>4):
                        # if(years[0].strip()!=years[1].strip()):
                        self.years='From '+''.join(self.years[:4]) + ' to '+ ''.join(self.years[4:])
                        # else:
                            # years='In '+ years[0]
                    else:
                         self.years='In '+ ''.join(self.years)        
                # self.years=years
                para1_sents=self.para1.split('*****')
                para2_sents=self.para2.split('*****')
                para3_sents=self.para3.split('*****')
                para4_sents=self.para4.split('*****')       
                
                para1=random.choice(para1_sents)
                para2=random.choice(para2_sents)
                para3=random.choice(para3_sents)
                para4=random.choice(para4_sents)

                if self.workexline1 and self.workexline2:
                    for key in ['[jobtype]','[resumetype]','[jobfield]','[totalexp]','[years]','[company]',
                            '[workexline1]','[workexline2]','[phoneNumber]','[email]','[university]','[degreeYear]','[companyList]']:
                        para1=para1.replace(key,str(self.__dict__[key[1:][:-1]]))
                        para2=para2.replace(key,str(self.__dict__[key[1:][:-1]]))
                        para3=para3.replace(key,str(self.__dict__[key[1:][:-1]]))
                        para4=para4.replace(key,str(self.__dict__[key[1:][:-1]]))
                elif not self.workexline2:
                    for key in ['[jobtype]','[resumetype]','[jobfield]','[totalexp]','[years]','[company]',
                            '[workexline1]','[phoneNumber]','[email]','[university]','[degreeYear]','[companyList]']:
                        para1=para1.replace(key,str(self.__dict__[key[1:][:-1]]))
                        para2=para2.replace(key,str(self.__dict__[key[1:][:-1]]))
                        para3=para3.replace(key,str(self.__dict__[key[1:][:-1]]))
                        para4=para4.replace(key,str(self.__dict__[key[1:][:-1]]))
                    para1=para1.replace('[workexline2]','')
                    para2=para2.replace('[workexline2]','')
                    para3=para3.replace('[workexline2]','')
                    para4=para4.replace('[workexline2]','')

                cover_letters.append({'letter':[para1,para2,para3,para4]})
    
            except Exception as e:
                print(e)
                raise(e)
                print('Error extracting project information')    
        return cover_letters
            
#       print(years)
#    def create(self,para1,para2,para3,para4):
#       para1_sents=para1.split('*****')
#       para2_sents=para2.split('*****')
#       para3_sents=para3.split('*****')
#       para4_sents=para4.split('*****')       
#       
#       para1=random.choice(para1_sents)
#       para2=random.choice(para2_sents)
#       para3=random.choice(para3_sents)
#       para4=random.choice(para4_sents)
#       
#       for key in ['[jobtype]','[resumetype]','[jobfield]','[totexp]','[years]','[company]',
#                   '[workexline1]','[workexline2]','[phoneNumber]','[email]','[university]']:
#           para1=para1.replace(key,str(self.__dict__[key[1:][:-1]]))
#           para2=para2.replace(key,str(self.__dict__[key[1:][:-1]]))
#           para3=para3.replace(key,str(self.__dict__[key[1:][:-1]]))
#           para4=para4.replace(key,str(self.__dict__[key[1:][:-1]]))
#       print(para1)
#       print(para2)
#       print(para3)
#       print(para4) 
#       return {'para1':para1,'para2':para2,'para3':para3}