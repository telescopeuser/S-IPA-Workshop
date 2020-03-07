
import inspect

from IPython.display import display, Markdown, Latex

##############################################################
# class Text(Dataset)
##############################################################

text_dataset_vectorize = '''
We can use the [`gensim.Dictionary.doc2idx`](https://radimrehurek.com/gensim/corpora/dictionary.html#gensim.corpora.dictionary.Dictionary.doc2idx) to **convert the tokenized sentence/document into a list of indices from the vocabulary**?

So the `vectorize()` would call the `Dictionary.doc2idx()` and the __getitem__ would simply wrap it into a dictionary and look like this:
'''

text_dataset_vectorize_code = '''
    t.init()
    for lecture in selected_lectures:
        t.url(lecture['iss_profile_link'])
        t.wait(3)
        t.snap('page', lecture['name'] + '_profile.png')
    t.close()

'''

exercise_one = '''
    t.init()
    t.url("https://www.iss.nus.edu.sg/")
    t.wait(5)
    t.hover('//a[@id="about"]')
    t.click('//a[contains(@href,"teaching-staff")]')
    t.wait(3)

    while True:
        current_page_num = t.count("//div[@class='block-profile-thumb']")
        for i in range(1,current_page_num+1):
            name = hover_and_read(f"(//div[@class='block-profile-thumb'])[{i}]//a[contains(@href,'/about-us/staff/detail')]")
            email_text = t.read(f"(//div[@class='block-profile-thumb'])[{i}]//a[contains(@onclick,'sendemail')]/@onclick")
            email = eval(email_text.replace('sendemail',''))[0] + '@' + eval(email_text.replace('sendemail',''))[1]
            iss_profile_link = t.read(f"(//div[@class='block-profile-thumb'])[{i}]//a[contains(@href,'/about-us/staff/detail')]/@href")
            print(name)
            print(email)
            print(iss_profile_link)
            print()

            lectures.append({'name':name,
                         'email':email,
                         'iss_profile_link':'https://www.iss.nus.edu.sg' + iss_profile_link})
        if t.present("//a[contains(@class,'catalogue_pagination_bttn pagination_next')]"): # the xpath of next page button
            t.click("//a[contains(@class,'catalogue_pagination_bttn pagination_next')]")
            t.wait(3)
        else:
            break
    t.close()

    selected_lectures = lectures[:10]
    # selected_lectures = lectures

    t.init()
    for lecture in selected_lectures:
        t.url(lecture['iss_profile_link'])
        t.wait(3)
        t.snap('page', ('exercise_1/' + lecture['name'] + '_profile.png').replace(' ',''))
        lecture['snapshot_location'] = ('exercise_1/' + lecture['name'] + '_profile.png').replace(' ','')
    t.close()
'''

exercise_two='''
    t.init()
    t.url('https://login.live.com/login.srf?wa=wsignin1.0&rpsnv=13&ct=1580788659&rver=7.0.6737.0&wp=MBI_SSL&wreply=https%3a%2f%2foutlook.live.com%2fowa%2f%3fnlp%3d1%26RpsCsrfState%3dd234420e-f55a-d62c-a8e6-c1c9a31e4e54&id=292841&aadredir=1&CBCXT=out&lw=1&fl=dob%2cflname%2cwld&cobrandid=90015')
    t.type('//input[@name="loginfmt"]', email_info['email'] + '[enter]')
    t.wait(0.5)
    t.type('//input[@name="passwd"]', email_info['password'] + '[enter]')

    count = 0
    while True:
        if count > 15:
            raise "Fail.Please Check your Internet Connection."
        if t.present('//a[@href="https://outlook.com"]'):
            t.wait(2)
            break
        else:
            t.wait(1)
            count = count + 1
    t.snap('page', 'exercise_2/email_snapshot.png')
    t.close()
'''

exercise_three='''
    t.init()
    t.url('https://www.bing.com/?scope=images&nr=1&FORM=NOFORM')
    t.click('//div[@id="sb_sbi"]')
    t.upload("input.fileinput",target_image)
    t.wait(3)
    t.click('//li[contains(string(),"Similar")]')
    image_nums = t.count('//a[@class="richImgLnk"]')
    limitation = 3
    for i in range(1,image_nums):
        if i <= 3:
            url = 'https://www.bing.com'+ t.read(f'(//a[@class="richImgLnk"])[{i}]/img/@src')
            t.download(url,'exercise_3/' + 'similar_'+str(i)+'.png')
    t.close()
'''


def hint_for_exercise_one():
    display(Markdown("## Hint for  `Exericse One`<br>"))
    display(Markdown(exercise_one))

def hint_for_exercise_two():
    display(Markdown("## Hint for  `Exericse Two`<br>"))
    display(Markdown(exercise_two))

def hint_for_exercise_three():
    display(Markdown("## Hint for  `Exericse Three`<br>"))
    display(Markdown(exercise_three))

__all__ = [
'hint_for_exercise_two','hint_for_exercise_one','hint_for_exercise_three'
]
