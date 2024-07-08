import yagmail
import sys
import time
data_name = sys.argv[1]
suc = sys.argv[2]
virus = sys.argv[3]

yag_server_qq = yagmail.SMTP(user='1497990745@qq.com',password="sxgyokqpwbcrfhee",host='smtp.qq.com')
#yag_server_163 = yagmail.SMTP(user='15976544633@163.com',password="sxgyokqpwbcrfhee",host='smtp.163.com')
#yag_server_scau = yagmail.SMTP(user='1497990745@qq.com',password="sxgyokqpwbcrfhee",host='smtp.scau.com')

email_to_163 = [-]
email_to_qq = [-]
email_to_scau =[-]
email_title = f'{data_name} {virus} 下载情况'
email_attachments = ['./夏天旧雨 好き.jpg']
email_content = f"{data_name} {virus} {suc} "
print("Send Email")
#
while 1==1:
    try:
        yag_server_qq.send(email_to_163,email_title,email_content)
        break
    except e:
        print(e)
        continue
while 1==1:
    try:
        yag_server_qq.send(email_to_qq,email_title,email_content)
        break
    except e:
        print(e)
        continue
while 1==1:
    try:
        yag_server_qq.send(email_to_scau,email_title,email_content)
        break
    except e:
        print(e)
        continue

