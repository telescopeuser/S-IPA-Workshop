#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Oct 16 20:33:55 2019

@author: nirmalenduprakash
"""
import os
from os import chdir
import glob
from time import sleep
import re
import calendar
import string
from sklearn.metrics.pairwise import cosine_similarity,euclidean_distances
from sklearn.feature_extraction.text import TfidfVectorizer
import numpy as np
import subprocess
from lxml import html
import nltk
from nltk.stem import WordNetLemmatizer

np.random.seed(1234)

class util:
    def __init__(self):
        self.output=[]
    def reemovNestings(self,l): 
        for i in l: 
            if type(i) == list: 
                self.reemovNestings(i) 
            else: 
                self.output.append(i)
        return self.output
    
import Stemmer
english_stemmer = Stemmer.Stemmer('en')
class StemmedTfidfVectorizer(TfidfVectorizer):
    def build_analyzer(self):
        analyzer = super(TfidfVectorizer,self).build_analyzer()
        return lambda doc: english_stemmer.stemWords(analyzer(doc))

class Resume:
        
    def __init__(self,resumeLoc,fileFormat='pdf'):
#        chdir(os.path.dirname(fileLoc))
        self.resumeLoc=resumeLoc
        self.fileFormat=fileFormat
        
    def convert(self,fileLoc=None):
        print('Converting pdf to html and txt file ...')
        try:
            if(fileLoc is None):
                fileLoc=self.resumeLoc  
            chdir(os.path.dirname(fileLoc))
            fileName=os.path.basename(fileLoc)
            self.name = fileName.replace('.pdf','')
            # subprocess.check_output(['pdftohtml','-s','-i',fileName],shell=False)
            subprocess.check_output(['pdftohtml','-s','-i',fileLoc])
            subprocess.check_output(['pdftotext','-layout','-enc','UTF-8',fileLoc])
            sleep(3)
            self.html=fileLoc.replace('.pdf','-html.html')
            self.txt=fileLoc.replace('.pdf','.txt')
        except:
            print('Error converting files')    
        
    def extract_projects(self,documents,htmlfile=None,txtfile=None):
        TfidfVec = StemmedTfidfVectorizer(stop_words=None,analyzer='word',encoding='utf-8')
        
        RE_INT = re.compile(r'[0-9]{4}$')
        print('Extracting project information...')
        try:
            if(htmlfile is None):
                htmlfile=self.html
            if(txtfile is None):
                txtfile=self.txt
            #read html
            classes=[]
            headings=[]
            with open(htmlfile,'r',encoding='utf-8') as f:
                page=f.read()
            tree=html.fromstring(page)
            headings.append(tree.xpath('//b/text()'))
            output=[]
            headings=util().reemovNestings(headings)
            headings=[h.replace('\xa0',' ').strip() for h in headings if h!='' and len(h)>1]
            with open(txtfile,'r',encoding='utf-8') as f:
                lst=f.read().split('\n')
                self.lst=lst
                
            cleaned_headings=[]
            for indx,h in enumerate(headings):
                hext=''
                for i in range(0,len(lst)):
                    if lst[i]==h:
                        lst[i]=lst[i]+'-->'+str(indx)
                        j=i-1
                        while(j>=0 and lst[j].strip()!=''):
                            hext=lst[j]+'\n'+hext
                            j-=1
                        break
                if(hext!=''):
                    cleaned_headings.append(hext+'\n'+h+'-->'+str(indx))
                else:
                    cleaned_headings.append(h+'-->'+str(indx))
            
            headermap=[]
            tag=''
            for i in range(len(lst)):
                itm=lst[i]
                for h in cleaned_headings:
                    if(itm!='' and itm in h.replace('\n\n','').replace('\n',' ')):
                        tag=h
                        break
                if tag!='' and itm not in tag.replace('\n\n','').replace('\n',' ') and itm!='':
                    headermap.append((tag,itm))

            mapping={}
            for k,v in headermap:
                if(k in mapping):
                    mapping[k.replace('','.').replace('','.')].append(v.replace('','.').replace('','.'))
                else:
                    mapping[k.replace('','.').replace('','.')]=[v.replace('','.').replace('','.')]
            for heading in cleaned_headings:
                if(heading not in list(mapping.keys())):
                    mapping[heading]=''
    #        self.mapping=mapping
            # print(mapping)
            #compare each heading in mapping with existing proj desc datasbase

            projtypScore={}
            for jobtyp,desc in documents.items():
                projectsScore=[]
                for k,v in mapping.items():
                    try:
                        desc.append('.'.join(mapping[k]))
                        tfidf=TfidfVec.fit_transform(desc)
                        similarityval=np.average(cosine_similarity(tfidf[-1],tfidf)[:,:-1])
                        # print(similarityval)
                        if(similarityval>=0.01):
                            projectsScore.append((k,similarityval))
                        desc=desc[:-1]
                    except:
                        similarityval=np.nanmean(cosine_similarity(tfidf[-1],tfidf)[:,:-1])
                        # print(similarityval)
                        if(similarityval>=0.01):
                            projectsScore.append((k,similarityval))
                        desc=desc[:-1]
                projtypScore[jobtyp]=projectsScore.copy()
        
            typscores=[]
            for idx,scores in projtypScore.items():
                typscores.append(np.average([float(s[1]) for s in scores]))
            
            maxIndx=np.argmax(typscores)
            
            self.resumeType= list(projtypScore.keys())[maxIndx]
            if(np.max(typscores)<0.01):
                self.resumeType='other'
#             print(typscores)
#             print(self.resumeType)
            if(self.resumeType!='other'):
                self.projects=projtypScore[self.resumeType]
                
            

            self.mapping={}
            for k,v in mapping.items():
                words=nltk.word_tokenize(' '.join(v).replace('.',' ').replace(',',' '))
                if(k in [k[0] for k in projtypScore[jobtyp]]):
                    dates=[]                
                    for w in words:
                        if(RE_INT.match(w) or w.lower()=='present'):
                            dates.append(w)
                    if(len(dates)==0):
                        words=nltk.word_tokenize(k)
                        for w in words:
                            if(RE_INT.match(w.strip())):
                                dates.append(w)          
                    self.mapping[k]=('-'.join(dates),v)#.replace('•','.').replace('','.')
        except Exception as e:
            print(e)
            raise(e)
            print('Error extracting project information')
        if not self.resumeType :
            self.resumeType = 'AI'

        return self.resumeType,self.mapping
    
    def extract_school(self,mapping=None):
        if(mapping is None):
            mapping=self.mapping
        punctuation=[s for s in string.punctuation]
        RE_INT=re.compile(r'[0-9]{4}$')
        MONTHS_LONG=[calendar.month_name[i] for i in range(0,13)][1:]
        MONTHS_SHORT=[calendar.month_abbr[i] for i in range(0,13)][1:]
        SCHOOL=['school','university','academy','institute','college','polytechnic']
        education=[]
#        for k,v in mapping.items():
#            if(v==''):
#                text=[k]
#            else:
#                text=v
#            for text in [[k],v]:
        for txt in self.lst:
            years=[]
            months=[]
            school=''
            for itm in txt.split('\n'):
                for t in itm.split(' '):
                    if(RE_INT.match(t)):
                        years.append(t)
                    elif(t in MONTHS_LONG or t in MONTHS_SHORT):
                        months.append(t)
                for sch in SCHOOL:
                    if(sch in itm.lower()):
                        for s in punctuation:
                            itm=itm.replace(s,',')
                        for t in itm.split(','):
                            if(sch in t.lower()):
                                school=t
#            print((years,months,school))
            if(school!=''):
                education.append((years,months,school.replace('','.').replace('','.')))
        self.education=education
        return education
    
    def extract_personalInfo(self):
        self.email=''
        self.ph=''
        r = re.compile(r'[\w\.-]+@[\w\.-]+')
        for sent in self.lst:
            email=r.findall(sent)
            if len(email)>0:
                self.email=email
                break
        r=re.compile('^[+-]?[0-9]*[-]?[0-9]{6,}')
        
        words=nltk.word_tokenize(' '.join(self.lst).replace('.',' ').replace(',',' '))
        for w in words:
            if(r.match(w)):
                self.ph=w
                break
#                        
#        for sent in self.lst:
#            ph=r.findall(sent)
#            if len(ph)>0:
#                self.ph=ph
#                break
        return self.email,self.ph

    def extract(self,documents,fileLoc=None):
        if(fileLoc is None):
            fileLoc=self.resumeLoc
        self.convert(fileLoc)
        self.extract_projects(documents)
        self.extract_school()
        self.extract_personalInfo()


        os.remove(os.path.join(fileLoc.split(fileLoc.split("/")[-1])[0], fileLoc.split("/")[-1].replace(".pdf","-html.html")))
        os.remove(os.path.join(fileLoc.split(fileLoc.split("/")[-1])[0], fileLoc.split("/")[-1].replace(".pdf",".txt")))
        os.remove(os.path.join(fileLoc.split(fileLoc.split("/")[-1])[0], fileLoc.split("/")[-1].replace(".pdf","s.html")))
        os.remove(os.path.join(fileLoc.split(fileLoc.split("/")[-1])[0], fileLoc.split("/")[-1]))

        return {'resume_type':self.resumeType,'projects':self.mapping,'education':self.education,'name':self.name,
                'email':self.email,'phone':self.ph}
    
class ApplicantDB:
    def __init__(self,folderLoc):
        self.folderLoc=folderLoc
        # read work ex into a list(remove duplicates)
        os.chdir(folderLoc)
        self.documents={}
        thisdir = os.getcwd()
        for subdir in os.listdir(thisdir):  
            if subdir[0] != '.':
                for item in os.walk(subdir):
                    files=item[2]
                    workex=[]
                    for file in files:
                        if(file.startswith('workex') and file.endswith('.txt')):
                            with open(subdir + '/'+ file,'r',encoding='utf-8') as f:
                                text=f.read()
                                if(text not in workex):
                                    workex.append(text)                                
                    self.documents[subdir]=workex.copy() 

class JobDB:
    def __init__(self,folderLoc):
        self.folderLoc=folderLoc
        # read work ex into a list(remove duplicates)
        os.chdir(folderLoc)
        self.documents={}
        thisdir = os.getcwd()
        for subdir in os.listdir(thisdir):
            if subdir[0] != '.':
                if(subdir!='Manager'):
                    for item in os.walk(subdir):
                        files=item[2]
                        jobDesc=[]
                        for file in files:
                            if(file.endswith('.txt')):
                                with open(subdir + '/'+ file,'r',encoding="unicode_escape") as f:
                                    text=f.read()
                                    if(text not in jobDesc):
                                        jobDesc.append(text)                                
                        self.documents[subdir]=jobDesc.copy()

class Job:
    def __init__(self,jobFilePath,fileFormat='pdf'):
        self.jobFileLoc=jobFilePath
        self.fileFormat=fileFormat
        
    def convert(self,fileLoc=None):
        print('Converting job pdf to html and txt...')
        try:
            if(fileLoc is None):
                fileLoc=self.jobFileLoc    
            chdir(os.path.dirname(fileLoc))
            fileName=os.path.basename(fileLoc)
            if(os.path.exists(fileLoc.replace('.pdf','-html.html'))):
                os.remove(fileLoc.replace('.pdf','-html.html'))
            if(os.path.exists(fileLoc.replace('.pdf','.txt'))):
                os.remove(fileLoc.replace('.pdf','.txt'))
                
            subprocess.check_output(['pdftohtml','-s','-i',fileLoc])
            subprocess.check_output(['pdftotext','-layout','-enc','UTF-8',fileLoc])
            sleep(2)
            self.html=fileName.replace('.pdf','-html.html')
            self.txt=fileName.replace('.pdf','.txt')
        except:
            print('Error creating html\txt file')

    def extract(self,roleDocuments,reqDocuments,htmlfile=None,txtfile=None):
        print('Extracting job information...')
        try:
            TfidfVec = StemmedTfidfVectorizer(min_df=1, stop_words='english',analyzer='word')
            if(htmlfile is None):
                htmlfile=self.html
            if(txtfile is None):
                txtfile=self.txt
            #read html
            headings=[]
            with open(htmlfile,'r',encoding='utf-8') as f:
                page=f.read()
            tree=html.fromstring(page)
            headings.append(tree.xpath('//b/text()'))
            
            headings=util().reemovNestings(headings)
            headings=[h.replace('\xa0',' ').strip() for h in headings if h!='' and len(h)>1]
            
            with open(txtfile,'r',encoding="unicode_escape") as f:
                lst=f.read().split('\n') 
                
            cleaned_headings=[]
    #        print(headings)
            for indx,h in enumerate(headings):
                hext=''
                for i in range(0,len(lst)):        
                    if lst[i].strip()==h:
                        lst[i]=lst[i]+'-->'+str(indx)
                        j=i-1
                        while(j>=0 and lst[j].strip()!=''):
                            hext=lst[j]+'\n'+hext
                            j-=1
                        break    
                if(hext!=''):                
                    cleaned_headings.append(hext+'\n'+h+'-->'+str(indx))
                else:
                    cleaned_headings.append(h+'-->'+str(indx))     

            headermap=[]
            tag=''
            for i in range(len(lst)):
                itm=lst[i]
                for h in cleaned_headings:
                    if(itm!='' and itm in h.replace('\n\n','').replace('\n',' ')):
                        tag=h
                        break                
                if tag!='' and itm not in tag.replace('\n\n','').replace('\n',' ') and itm!='':
                    headermap.append((tag,itm))
                    
            mapping={}
            for k,v in headermap:
                if(k in mapping):
                    mapping[k].append(v)
                else:
                    mapping[k]=[v]   
            for heading in cleaned_headings:
                if(heading not in list(mapping.keys())):
                    mapping[heading]=''
    #        print(mapping)
            reqDesctypScore={}
    #        print(reqDocuments['UX']+ roleDocuments['UX'])
    #        combined={key:reqDocuments[key]+roleDocuments[key] for key in list(reqDocuments.keys())}
            
            for typ,desc in reqDocuments.items():
                scores=[]
                for k,v in mapping.items():
                    desc.append('.'.join(mapping[k]))
                    tfidf=TfidfVec.fit_transform(desc)
                    similarityval=np.average(cosine_similarity(tfidf[-1],tfidf)[:,:-1])
                    # print(k,similarityval)
                    if(similarityval>=0.01):
                        scores.append((k,similarityval))
                    desc=desc[:-1]    
                reqDesctypScore[typ]=scores.copy()
            
            typscoresReq=[]
            for idx,scores in reqDesctypScore.items(): 
                typscoresReq.append(np.average([float(s[1]) for s in scores]))
    #        print(typscores) 
            
            for typ,desc in roleDocuments.items():
                scores=[]
                for k,v in mapping.items():
                    desc.append('.'.join(mapping[k]))
                    tfidf=TfidfVec.fit_transform(desc)
                    similarityval=np.average(cosine_similarity(tfidf[-1],tfidf)[:,:-1])
                    # print(k,similarityval)
                    if(similarityval>=0.01):
                        scores.append((k,similarityval))
                    desc=desc[:-1]    
                reqDesctypScore[typ]=scores.copy()    
            
            typscoresRole=[]
            for jpbtyp,scores in reqDesctypScore.items(): 
                typscoresRole.append(np.average([float(s[1]) for s in scores]))
            
            # print([t[0]+0.5*t[1] for t in zip(typscoresReq,typscoresRole)])
            # print(list(reqDesctypScore.keys()))
            maxIndx=np.argmax([t[0]+0.5*t[1] for t in zip(typscoresReq,typscoresRole)])
            maxval=np.max([t[0]+0.5*t[1] for t in zip(typscoresReq,typscoresRole)])
            
            if(maxval<0.01):
                self.jobType='other'
            else:
                self.jobType= list(reqDesctypScore.keys())[maxIndx]
                
            #compare each heading in mapping with existing role desc datasbase        
            # print(self.jobType)
            
            desc =reqDocuments[self.jobType]
            scores=[]
            self.reqMapping={}
            for k,v in mapping.items():
                desc.append('.'.join(mapping[k]))
                tfidf=TfidfVec.fit_transform(desc)
                similarityval=np.average(cosine_similarity(tfidf[-1],tfidf)[:,:-1])
    #                print(similarityval)
                if(similarityval>=0.04):
                    self.reqMapping[k]=v
                desc=desc[:-1]
                
    #        print(roleDocuments[self.jobType])        
            desc =roleDocuments[self.jobType]
            scores=[]
            self.roleMapping={}
            for k,v in mapping.items():
                desc.append('.'.join(mapping[k]))
                tfidf=TfidfVec.fit_transform(desc)
                similarityval=np.average(cosine_similarity(tfidf[-1],tfidf)[:,:-1])
    #                print(similarityval)
                if(similarityval>=0.04 and k not in list(self.reqMapping.keys())):
                    self.roleMapping[k]=v
                desc=desc[:-1] 
        except:
            print('Error extracting job information')
                
         
        # print('role:',self.roleMapping) 
        # print('req:',self.reqMapping) 
        return self.jobType,self.roleMapping,self.reqMapping