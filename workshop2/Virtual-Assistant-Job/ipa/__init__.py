import time
import os
import shutil
import subprocess
from collections import namedtuple
import random

from ipa.IPA import ApplicantDB, Job, JobDB, Resume
from ipa.CoverLetter import CoverLetter
from ipa.utils import replace_char_for_latex

SCRIPT_PATH = os.path.abspath('')
IPA_EXECUTE_PATH = os.path.join(SCRIPT_PATH,"ipa")
applicationDB = ApplicantDB(os.path.join(IPA_EXECUTE_PATH, "workex/"))
roleDB=JobDB(os.path.join(IPA_EXECUTE_PATH, "JobResponsibility"))
reqDB=JobDB(os.path.join(IPA_EXECUTE_PATH, "JobRequirement"))

class CoverLetterGenerator(object):
    

    def __init__(self,resume_file_path,jds_file_paths,name,phone,email):
        self.resume_file_path = resume_file_path
        self.jds_file_paths = jds_file_paths
        self.name = name
        self.phone = phone
        self.email = email


    def generate(self):
        resume_data = CoverLetterGenerator.resume_processor(self.resume_file_path)
        print("Processing the jds")
        job_data = []
        for jd in self.jds_file_paths:
            job_data.append(CoverLetterGenerator.job_processor(jd))
        print("Processing the jds,done")
        print("Generating CoverLetter")
        return CoverLetterGenerator.generate_coverletter(resume_data,job_data,self.name,self.phone,self.email)

    @staticmethod
    def resume_processor(resume_file_path):
        print("Processing the resume")
        fileName=os.path.basename(resume_file_path)
        shutil.copy(resume_file_path,
            os.path.join(IPA_EXECUTE_PATH, "exe/"+fileName))
        
        _resume = Resume(os.path.join(IPA_EXECUTE_PATH, "exe/"+fileName))
        # extraction
        _extracted = _resume.extract(applicationDB.documents)

        resume_type = _extracted['resume_type']
        project_experience = _extracted['projects']
        name = _extracted['name']
        email = _extracted['email']
        phone = _extracted['phone']
        project_infos = []

        for k,v in project_experience.items():
            _info = {}
            _info['type'] = k
            _info['company'] = ''
            _info['date'] = v[0]
            _info['summary'] = ''.join(v[1][0:])
            project_infos.append(_info)

        education_experience = _extracted['education']
        education_infos = []
        for education_info in education_experience:
            _info = {}
            _info['date'] = str(education_info[0]) + "-" + str(education_info[1])
            _info['school'] = education_info[2]
            education_infos.append(_info)

        resume_data = {}
        if isinstance(email,list):
            resume_data['email']= email[0]
        else:
            resume_data['email'] = email
        resume_data['name'] = name
        resume_data['phone'] = phone
        resume_data['type'] = resume_type
        resume_data['project_experience'] = str(project_infos)
        resume_data['education_experience'] = str(education_infos)
        print("Processing the resume done")
        print("Resume Type:" + resume_data['type'])
        return resume_data



    @staticmethod
    def job_processor(job_file_location):
        fileName=os.path.basename(job_file_location)
        print(fileName)
        shutil.copy(job_file_location,
            os.path.join(IPA_EXECUTE_PATH, "exe/"+fileName))
        _job = Job(os.path.join(IPA_EXECUTE_PATH, "exe/"+fileName))
        _job.convert()
        jobtype,role,req = _job.extract(roleDB.documents,reqDB.documents)

        job_data = {}
        job_data['email'] = ''
        job_data['description'] = str(req)
        job_data['requirement'] = str(role)
        job_data['type'] = jobtype
        os.chdir(SCRIPT_PATH)
        print("Job Type:" + job_data['type'])
        return job_data

    @staticmethod
    def generate_coverletter(resume,job_data,username,userphone,useremail):
        selected_jobs = []
        for job in job_data:
            if resume['type'].find('[')>=0:
                _str = resume['type'][1:-1]
                types = _str.split(',')
                _types = []
                for _temp in types:
                    _types.append(_temp.strip()[1:-1])
                if job['type'] in _types:
                    selected_jobs.append(job)
            else:
                if job['type'] == resume['type']:
                    selected_jobs.append(job)

        cv_temp_path = os.path.join(IPA_EXECUTE_PATH, "coverletter_temp")
        with open(os.path.join(cv_temp_path, "first_para.txt"),'r',encoding='utf-8') as f:
            para1=f.read()
        with open(os.path.join(cv_temp_path, "second_para.txt"),'r',encoding='utf-8') as f:
            para2=f.read()
        with open(os.path.join(cv_temp_path, "third_para.txt"),'r',encoding='utf-8') as f:
            para3=f.read()
        with open(os.path.join(cv_temp_path, "fourth_para.txt"),'r',encoding='utf-8') as f:
            para4=f.read()
        coverletter_generator = CoverLetter(para1,para2,para3,para4)
        
        coverletters = []
        _result =  coverletter_generator.create_letter(resume=resume,jobs=selected_jobs)
        for inx,item in enumerate(_result):
            # generate the coverletter
            sender_name = username
            sender_phone = userphone
            sender_email = useremail
            recipiant_title = "Dear Sir or Madam"
            date = time.strftime("%B %d %Y", time.localtime()) 
            first_paragraph = item['letter'][0]
            secend_paragraph = item['letter'][1]
            third_paragraph = item['letter'][2]
            fourth_paragraph = item['letter'][3]
            template = open(os.path.join(IPA_EXECUTE_PATH, "templates/templates.tex"), "r")
            content = template.read()
            content = content.replace('%[name]',sender_name)
            content = content.replace('%[phone]',sender_phone)
            content = content.replace('%[email]',sender_email.replace('_','\_'))
            content = content.replace('%[date]',date)
            content = content.replace('%[recipiant_title]',recipiant_title)
            content = content.replace('%[first_paragraph]',replace_char_for_latex(first_paragraph,['%','#']))
            content = content.replace('%[secend_paragraph]',replace_char_for_latex(secend_paragraph,['%','#']))
            content = content.replace('%[third_paragraph]', replace_char_for_latex(third_paragraph,['%','#']))
            content = content.replace('%[fourth_paragraph]',replace_char_for_latex(fourth_paragraph,['%','#']))
            _cover_letter_data = {
            'sender_name' :sender_name,
            'sender_phone' :sender_phone,
            'sender_email' :sender_email,
            'recipiant_title' :recipiant_title,
            'date' :date,
            'first_paragraph' :first_paragraph,
            'secend_paragraph' :secend_paragraph,
            'third_paragraph' :third_paragraph,
            'fourth_paragraph' :fourth_paragraph,
            }
            date = time.strftime("%Y%m%d", time.localtime())
            cover_letter_path = os.path.join(IPA_EXECUTE_PATH, "coverletter_"+str(date))
            isExists=os.path.exists(cover_letter_path)
            if not isExists:
                os.makedirs(cover_letter_path) 
            with open(os.path.join(cover_letter_path, "templates_"+str(inx)+".tex"),'w',encoding='utf-8') as f:
                f.write(content)
            # pdflatex  -output-directory="./" -job-name="coverletter"  .\templates.tex.bk
            return_code = os.system('pdflatex ' + \
                    '-output-directory="'+cover_letter_path+'" ' + \
                    '-job-name="coverletter_'+str(inx)+'" '+\
                    '"'+os.path.join(cover_letter_path, 'templates_'+str(inx)+'.tex'+'"'))
            
            print(return_code)

            # assert (return_code != 0), "pdf2latex error. Maybe Check your .tex file format"
            
            os.remove(os.path.join(cover_letter_path, "templates_"+str(inx)+".aux"))
            os.remove(os.path.join(cover_letter_path, "templates_"+str(inx)+".log"))
            os.remove(os.path.join(cover_letter_path, "templates_"+str(inx)+".out"))

            coverletters.append(os.path.join(cover_letter_path, 'templates_'+str(inx)+'.pdf'))

        return coverletters