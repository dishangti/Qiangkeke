import requests
import threading
import re

class Stu():

    def __init__(self, cookie, classid_list, grab_url, grab_referer, query_url):
        self.grab_url = grab_url
        self.query_url = query_url
        self.classid_list = classid_list
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.132 Safari/537.36',
            'Referer': grab_referer,
            'Cookie': cookie
        }
        self.grabbed = {}
        for classid in classid_list:
            self.grabbed[classid] = False
    
    def grab_class(self, classid):
        self.data = {
            'optype': 'true',
            'operator0': classid+':true:0',
            'lesson0': classid,
            'expLessonGroup_'+classid: 'undefined'
        }
        n=0
        while True:
            if self.grabbed[classid]: break
            n=n+1
            try:
                mes = requests.post(self.grab_url, headers=self.headers, data=self.data, verify=False)
            except:
                print(classid+'选课失败，正在进行第'+str(n)+'次尝试') 
                continue
            res=str(mes.content,'utf8')
            if '成功' in res:
                print(classid+"选课成功")
                self.grabbed[classid] = True
                break
            else:
                print(classid+'选课失败，正在进行第'+str(n)+'次尝试')            

    def grab_all(self):
        for classid in self.classid_list:
            thd = threading.Thread(target=self.grab_class, args=(classid,))
            thd.start()
    
    def thd_graball(self, thd_num):
        for i in range(0, thd_num):
            thd = threading.Thread(target=self.grab_all)
            thd.start()
    
    def query_info(self, classid):
        params = {
            'lesson.id': classid
        }
        res = str(requests.get(self.query_url, headers=self.headers,params=params, verify=False).content, 'utf8')
        if '登录' in res:
            return None
        content_pattern = r'<td class="content".*?</td>'
        sub_pattern = r'</?td.*?>'
        name_pattern = r'课程名称:</td>([\s\S]*?)<td.*?</td>'
        teacher_pattern = r'教师:</td>([\s\S]*?)<td.*?</td>'
        area_pattern = r'校区:</td>([\s\S]*?)<td.*?</td>'
        get_info = lambda pat: re.sub(sub_pattern, '',re.search(content_pattern, re.search(pat, res).group()).group())
        class_name = get_info(name_pattern).strip()
        class_teacher = get_info(teacher_pattern).strip()
        class_area = get_info(area_pattern).strip()
        return (class_name, class_teacher, class_area)
    
    def all_info(self):
        for classid in self.classid_list:
            print(classid, *self.query_info(classid))