import subprocess
import sys
import oss2
import os
import re
import copy
import time
import argparse
#登录信息
endpoint = ''
accesskey_id = ""
accesskey_secret = ""
bucket_name = ""
DNA_list = []
RNA_list= []
all_list =[]
data_name = ""
virus_name =[]
has_run_root = []
# 本地文件保存路径前缀
download_local_save_prefix = ""
root_dir_list = []
data_download_name = [""]
continue_download =  False
'''
列举prefix全部文件
'''

def main (bucket,data_new_list,ddir,dname,vname):
    global continue_download
    if not os.path.exists(ddir):
        print(ddir)
        os.makedirs(ddir)
    for obj in oss2.ObjectIterator(bucket):
        key = obj.key
        rawdata_index = key.find("rawdata/")
        merge_index = key.find("/00.mergeRawFq")
        if merge_index > -1:
            prefix = key[(rawdata_index+8):(merge_index)]
            if (prefix in data_new_list) == False:  
                data_new_list.append(prefix)
    #获得oss上存在的数据
    all_file = os.listdir(ddir)
    print(all_file)
    print(data_new_list)


    
    for name in data_new_list:
    #获得本地已下载的数据名字，与oss上名字列表对比，本地不存在的数据会执行下载操作
        if (name in all_file) == False:
            ddir_output = os.path.join(ddir,name)
            print(f"{ddir_output}:start download")
            V_name_str = " ".join(vname)
            print(f"{name} is downloading")
            print(f"python oss_getdir.py -d {ddir_output} -ak - -s - -b - -ep - -data LZF -v {V_name_str} --date {name}")
            sys.stdout.flush()
            os.system(f"python oss_getdir.py -d {ddir_output} -ak - -s - -b - -ep - -data LZF -v {V_name_str} --date {name}")
            print(f"All data will run {vname} (R:RNA,P:PRRSV)")
            

if __name__ == '__main__':

    parser = argparse.ArgumentParser()
    parser.add_argument("-d",type =str,help = "download directory")
    parser.add_argument("-ak",type =str,help = "list of data")
    parser.add_argument("-s",type =str,help = "list of data")
    parser.add_argument("-ep",type =str,help = "list of data")
    parser.add_argument("-b",type =str,help = "list of data")
    parser.add_argument("-data",type =str,help = "list of data")
    parser.add_argument("-v",type =str,nargs="+",help = "list of data")
    parser.add_argument("--date",type =str,nargs="+",help = "list of data")
    args = parser.parse_args()
    virus_name = args.v
    download_local_save_prefix = args.d
    bucket_name = args.b
    accesskey_id = args.ak
    accesskey_secret = args.s
    endpoint = args.ep
    data_name = args.data
    data_download_name = args.date
    data_new_list = []
    if data_download_name is None:
       data_download_name = [""]
    
    auth = oss2.Auth(accesskey_id, accesskey_secret)
    bucket = oss2.Bucket(auth, endpoint, bucket_name)

    print(data_download_name)
    print(virus_name)
    print("AUTOstart \n")
    
    while 1 == 1:    
        try:
            main(bucket,data_new_list,download_local_save_prefix,data_name,virus_name)
            sys.stdout.flush()
            time.sleep(1800)
        except:
            time.sleep(1800)
        

    print("AUTOend \n")




       
    
        
