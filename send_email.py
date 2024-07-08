import yagmail
import sys
import time
data_name = sys.argv[1]
data_dir = sys.argv[2]


yag_server_qq = yagmail.SMTP(user='1497990745@qq.com',password="-",host='smtp.qq.com')


email_to_163 = [-]
email_to_qq = [-]
email_to_scau =[-]
email_title = f'{data_name} 执行完毕'
email_attachments = ['./鸣人佐助.jpg']
email_content = f"{data_dir} {data_name} 代码执行完毕 "
print("Send Email")
#
while 1==1:
    try:
        print("Send email to 163")
        yag_server_qq.send(email_to_163,email_title,email_content)
        break
    except e:
        print(e)
        continue
while 1==1:
    try:
        print("Send email to qq")
        yag_server_qq.send(email_to_qq,email_title,email_content)
        break
    except e:
        print(e)
        continue
while 1==1:
    try:
        print("Send email to scau")
        yag_server_qq.send(email_to_scau,email_title,email_content)
        break
    except e:
        print(e)
        continue

