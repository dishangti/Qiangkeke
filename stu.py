import requests
from threading import Thread, Lock
import re
from time import sleep

class Stu():

    def __init__(self, cookie, classid_list, grab_url, grab_referer, query_url):
        self.grab_url = grab_url
        self.query_url = query_url
        self.classid_list = classid_list
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.0.0 Safari/537.36',
            'Referer': grab_referer,
            'Cookie': cookie
        }
        self.is_grabbed = {}
        self.grab_count = {}
        for classid in classid_list:
            self.is_grabbed[classid] = False
            self.grab_count[classid] = 0

        self.syn_lock = Lock()      # 线程互斥锁

        self.log_file = open('qiangkeke.log', 'w', encoding="utf8")

    def grab_class(self, classid, class_thd_num):
        data = {
            'optype': 'true',
            'operator0': classid+':true:0',
            'lesson0': classid,
            'expLessonGroup_'+classid: 'undefined'
        }

        grab_url = self.grab_url
        headers = self.headers

        syn_lock = self.syn_lock
        grab_count = self.grab_count
        is_grabbed = self.is_grabbed
        log_file = self.log_file

        while True:
            if is_grabbed[classid]: break
            try:
                mes = requests.post(grab_url, headers=headers, data=data, verify=False)
            except Exception:
                with syn_lock:
                    grab_count[classid] += 1
                    info = '课程'+classid+'线程'+str(class_thd_num)+'：第'+str(grab_count[classid])+'次尝试提交失败...'
                    log_file.write(info + '\n')
                print(info)
                continue
            else:
                res=str(mes.content,'utf8')
                if '成功' in res:
                    with syn_lock:
                        grab_count[classid] += 1
                        info = '课程'+classid+'线程'+str(class_thd_num)+'：第'+str(grab_count[classid])+'次选课成功，将停止其他抢课线程！'
                        log_file.write(info + '\n')
                    print(info)
                    is_grabbed[classid] = True
                    break
                else:
                    with syn_lock:
                        grab_count[classid] += 1
                        info = '课程'+classid+'线程'+str(class_thd_num)+'：第'+str(grab_count[classid])+'次尝试选课失败...'
                        log_file.write(info + '\n')
                    print(info)            

    def set_grab_thd(self, classid, thd_num):
        for class_thd_num in range(0, thd_num):
            thd = Thread(target=self.grab_class, args=(classid, class_thd_num))
            thd.start()
    
    def flush_log_buffer(self):
        log_file = self.log_file
        syn_lock = self.syn_lock
        while True:
            sleep(1)
            with syn_lock:
                log_file.flush()

    def set_thd(self, thd_num):
        for classid in self.classid_list:
            thd = Thread(target=self.set_grab_thd, args=(classid, thd_num))
            thd.start()
        thd= Thread(target=self.flush_log_buffer)
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
            info = str(classid) + ' ' + ' '.join(self.query_info(classid))
            with self.syn_lock:
                self.log_file.write(info + '\n')
            print(info)

    def __del__(self):
        self.log_file.close()