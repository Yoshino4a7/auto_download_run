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
has_RNA = False
# 本地文件保存路径前缀
download_local_save_prefix = ""
root_dir_list = []
data_download_name = [""]
'''
列举prefix全部文件
'''




def prefix_all_list_md5(bucket,ddname):
    # print("开始列举" + prefix + "全部文件")
    oss_file_size = 0


    for obj in oss2.ObjectIterator(bucket):
        key = obj.key
        # print(key)

        if key.find(ddname) > -1:
            rawdata_index = key.find("rawdata/")
            merge_index = key.find("/00.mergeRawFq")
            if merge_index > -1:
                prefix = key[(rawdata_index+8):(merge_index)]
            if (prefix in DNA_list) == False:
                DNA_list.append(prefix)
    all_list = RNA_list + DNA_list
    
    all_list_md5_dna(bucket,ddname)
    #all_list_md5_rna(bucket)
    
    


def all_list_md5_dna(bucket,ddname):
    data_len = 0
    print(DNA_list)
    global has_RNA
    for dna_dir in DNA_list:
        prefix = dna_dir
        
        list2 = [download_local_save_prefix,"rawdata"]
        if not os.path.exists("/".join(list2)):
            os.makedirs("/".join(list2))
        list = [download_local_save_prefix,"rawdata",prefix]
        dir = "/".join(list)
        if not os.path.exists(dir):
            os.makedirs(dir)
        
        key = os.path.join(f"rawdata/{prefix}", "MD5.txt")
        key = key.replace("\\","/")
        download_to_local(bucket, key, 0)
        
        root_dir = "/".join(list)
        print(root_dir)
        for obj in oss2.ObjectIterator(bucket):
            key = obj.key
            #print(key)
                        
            
            if key.endswith("/") and (key.find(ddname) > -1):
                
                dir = "/".join([download_local_save_prefix,key])
                if not os.path.exists(dir):
                    print(dir)
                    os.makedirs(dir)
                    continue
            
        run_py(virus_name,root_dir,data_name,data_len)        
        data_len = data_len + 1
    for obj in oss2.ObjectIterator(bucket):
        key = obj.key
        #print(key)
        if (key.find(ddname) > -1):
            if (key.find(f"00.mergeRawFq") > -1):
                for v in virus_name:
                    if (key.find(f"00.mergeRawFq/{v}") > -1):
                        if ((key.endswith("/") == False) ):
                            has_RNA = True
                            download_to_local(bucket, obj.key, 0)
                            pass
            else:
                if ((key.endswith("/") == False) ):
                    download_to_local(bucket, obj.key, 0)
                    pass
                
        
            



def root_directory_list_md5(bucket,ddname):
    # 设置Delimiter参数为正斜线（/）。
    num = 0
    try:
        for obj in oss2.ObjectIterator(bucket, delimiter='/'):
            # 通过is_prefix方法判断obj是否为文件夹。
            if obj.is_prefix():  # 文件夹
                global root_dir_DNA
                global root_dir_RNA
                #root_dir = f"{download_local_save_prefix}/{obj.key}"
                prefix_all_list_md5(bucket,ddname)
            #else:  # 文件
             
            #     # 下载根目录的单个文件
            #download_to_local(bucket,obj.key)
            #     num += 1
            #     # print(num)
    except OSError as e:
        print(e)
    return 1


'''
下载文件到本地
'''



def percentage(consumed_bytes, total_bytes):
    if total_bytes:
        rate = int(100 * (float(consumed_bytes) / float(total_bytes)))
        # rate表示下载进度。
        print('\r{0}% '.format(rate), end='')

        sys.stdout.flush()
def download_to_local(bucket, object_name,option):
    url = download_local_save_prefix
    # print(object_name)
    # 文件名称
    # file_name = url[url.rindex("/") + 1:]

    # file_path_prefix = url.replace(file_name, "")
    # if False == os.path.exists(object_name):
    #     os.makedirs(file_path_prefix)
    #     print("directory don't not makedirs " + file_path_prefix)

    # 下载OSS文件到本地文件。如果指定的本地文件存在会覆盖，不存在则新建。
 
    list = [download_local_save_prefix, object_name]
    down_dir = "/".join(list)
    dir = down_dir.replace("\\", "/")
    
    if not os.path.exists(dir):
        print(dir)
        try:
            oss2.resumable_download(bucket,object_name, dir, progress_callback=percentage)
        except KeyboardInterrupt:
            sys.exit()
        except:
            download_to_local(bucket, object_name,option)
        print("")
        
        
def run_py(virus,root_dir,name,dlen):
    if (root_dir in has_run_root) == False:
        
        if "R" in virus :
            
            has_run_root.append(root_dir)
            change_data(root_dir,"submit.sh",f'{root_dir}/submit_{name}_{dlen}_R.sh',dlen,"R",name)
            os.system(f"sbatch {root_dir}/submit_{name}_{dlen}_R.sh")
        

        pass
                
        if "P" in virus:
           
            has_run_root.append(root_dir)
            change_data(root_dir,"submit.sh",f'{root_dir}/submit_{name}_{dlen}_P.sh',dlen,"P",name)
            os.system(f"sbatch {root_dir}/submit_{name}_{dlen}_P.sh")
        pass
        

def change_data(da,pfile,npfile,data_len,vname,name):
        #print(da)
        
        with open(f"{npfile}","w") as file:
            list = []
            with open(f"{pfile}","r") as f:
                content = f.readlines()
                
                for line in content:
                    
                    if line.startswith("#SBATCH --error"):
                        s =f'#SBATCH --error={da}/error_{name}_{data_len}_{vname}\n'
                        list.append(s)
                    elif line.startswith("#SBATCH -o"):
                        s =f'#SBATCH -o {da}/output_{name}_{data_len}_{vname}\n'
                        list.append(s)
                    elif line.startswith("#SBATCH -J"):
                        s =f'#SBATCH -J auto_{name}_{data_len}_{vname}\n'
                        list.append(s)
                    elif line.startswith("python"):
                        s =f'python file_check.py -d {da} -data {data_name} -v {vname}'
                        list.append(s)
                    else:
                        list.append(line)
            str1 = "".join(list)
            
            file.write(str1)
def get_data_name(bucket,data_list):
    data_new_list = []
    if data_list[0] == "":
        for obj in oss2.ObjectIterator(bucket):
            key = obj.key
            rawdata_index = key.find("rawdata/")
            merge_index = key.find("/00.mergeRawFq")
            if merge_index > -1:
                prefix = key[(rawdata_index+8):(merge_index)]
                if (prefix in data_new_list) == False:
                    data_new_list.append(prefix)
        return data_new_list
        
    else:
        for date in data_list:
            # for obj in oss2.ObjectIterator(bucket):
                # key = obj.key
                # if key.find(date) > -1:
                    # rawdata_index = key.find("rawdata/")
                    # merge_index = key.find("/00.mergeRawFq")
                    # if merge_index > -1:
                        # prefix = key[(rawdata_index+8):(merge_index)]
                    # if (prefix in data_new_list) == False:
                        # data_new_list.append(prefix)
            data_new_list.append(date)
        return data_new_list
        #return data_list

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
    if data_download_name is None:
       data_download_name = [""]
    
    auth = oss2.Auth(accesskey_id, accesskey_secret)
    bucket = oss2.Bucket(auth, endpoint, bucket_name)
    data_download_name = get_data_name(bucket,data_download_name)
    print(data_download_name)
    print(virus_name)
    for name in data_download_name:



        print("start \n")
   
        
        try:
            root_directory_list_md5(bucket,name)
        except:
            abs_dir = os.path.abspath(f"{download_local_save_prefix}/{name}")
            

            #os.system(f"python send_email_download.py {abs_dir} '下载失败'")
            exit()
        abs_dir = os.path.abspath(f"{download_local_save_prefix}/{name}")
        if (has_RNA == True):
            print("Send Email")
            os.system(f"python send_email_download.py {abs_dir} '下载成功' RNA")
        print("end \n")
    
        
