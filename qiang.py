from stu import Stu
import urllib3

cookie_f = open('cookie.txt')
classid_f = open('classid.txt')
url_f = open('url.txt')
cookie = cookie_f.readline().strip()
classid_list = classid_f.readlines()
for i, classid in enumerate(classid_list):
    classid_list[i] = classid.strip()
urls = url_f.readlines()
grab_url = urls[0].strip()
grab_referer = urls[1].strip()
query_url = urls[2].strip()

urllib3.disable_warnings()
stu = Stu(cookie, classid_list, grab_url, grab_referer, query_url)
print('待抢课程信息：')
stu.all_info()
thd_num = int(input('每门课抢课线程数：'))
yes = input('输入y并回车开始抢课：')
stu.thd_graball(thd_num)