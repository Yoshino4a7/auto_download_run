import os
import subprocess
import sys
import hashlib
import time
import shutil
import yagmail
file_execute_DNA = {}
file_execute_RNA = {}
DNA_dir_list = []
RNA_dir_list = []
mergeRawFq_dir_list = []
mergeRawFq_file_list_RNA ={}
mergeRawFq_file_list_DNA ={}
ok_filelist_DNA = {}
ok_filelist_RNA = {}
exc_file_DNA = 0 
exc_file_RNA = 0
data_name = ""
virus_name = ""
rnareport_running = False
def init(old_file_list,option):
    for dir in old_file_list.values():
        if option == 0:
            if (dir in file_execute_DNA.keys()) is False:
                file_execute_DNA[dir] = False
        if option == 1:
            if (dir in file_execute_RNA.keys()) is False:
                file_execute_RNA[dir]= False
        #if dir.startswith("D"):
        #    copy_file_DNA(dir)
        #else:
        #    copy_file_RNA(dir)
    # print(file_execute)

def copy_file_DNA(dir):
    run_dir = os.path.join(mergeRawFq_dir, dir)
    modify_parm(dir)
    copyTo(run_dir,"./run_dna.sh","run_dna.sh")
    copyTo(run_dir,"./parameters.txt","parameters.txt")
    copyTo(run_dir,"./parametersI.txt","parametersI.txt")
    copyTo(run_dir,"./ASFV_mix_12-II.py","ASFV_mix_12-II.py")
    copyTo(run_dir,"./ASFV_mix_T.py","ASFV_mix_T.py")

def copy_file_RNA(dir):
    run_dir = os.path.join(mergeRawFq_dir, dir)
    #modify_parm(dir)
    modify_parm_rna(dir)
    copyTo(run_dir,"./run_rna.sh","run_rna.sh")
    copyTo(run_dir,"./report_code12.py","report_code12.py")
    copyTo(run_dir,"./consensus.py","consensus.py")
    copyTo(run_dir,"./yankuo1.R","yankuo1.R")
    copyTo(run_dir,"./report_codejingjian.py","report_codejingjian.py")
    copyTo(run_dir,"./rna_qc_classification_update_megahit_tayankuo.py","rna_qc_classification_update_megahit_tayankuo.py")
    try:
        src = "./env"
        dis = os.path.join(run_dir,"env")
        shutil.copytree(src,dis)
    except FileExistsError:
        pass
    

def copyTo(run_dir,src,d):
    dis = os.path.join(run_dir, d)
    try:
        if os.path.isdir(dis):
            shutil.copytree(src,dis)
        else:
            shutil.copyfile(src,dis)
    except FileNotFoundError:
        pass

def run_py(virus,root_dir,name,dlen,dirname):
    
    if virus == "R":
        change_data_rnareport(dirname,"report_code12.py",f'{root_dir}/report_code12.py')
        change_data_sub_rnareport(root_dir,"report_code12.sh",f'{root_dir}/report_code12_{name}_{dlen}_{virus}_mod.sh',dlen,data_name,dirname)
        os.system(f"cp ./send_email.py {root_dir}/send_email.py")
        os.system(f"sbatch {root_dir}/report_code12_{name}_{dlen}_{virus}_mod.sh")    
        pass
        #执行R相关数据的脚本
    if virus == "P":
        change_data(root_dir,"prrsv.sh",f"{root_dir}/prrsv_{name}_{dlen}.sh",dlen,data_name)
        os.system(f"sbatch {root_dir}/prrsv_{name}_{dlen}.sh") 
        pass
        #执行prrsv相关数据的脚本

def change_data(da,pfile,npfile,data_len,name):
    print(da)
    with open(f"{npfile}","w") as file:
        list = []
        with open(f"{pfile}","r") as f:
            content = f.readlines()
            for line in content:
                if line.startswith("#SBATCH --error"):
                    s =f'#SBATCH --error={da}/prrsv_error_{name}_{data_len}\n'
                    list.append(s)
                elif line.startswith("#SBATCH -o"):
                    s =f'#SBATCH -o {da}/prrsv_output_{name}_{data_len}\n'
                    list.append(s)
                elif line.startswith("#SBATCH -J"):
                    s =f'#SBATCH -J AUTO_prrsv_{name}_{data_len}\n'
                    list.append(s)
                elif line.startswith("#SBATCH --chdir") and pfile == "report_code12.sh":
                    s =f'#SBATCH --chdir={da}\n'
                    list.append(s)
                elif line.startswith("python"):
                    s =f'python prrsv_if.py -p 80.0 -d {da} -r 0.33 -qc 70.0 -ql 13000.0 -id {data_len} -name {data_name}'
                    list.append(s)
                else:
                    list.append(line)
        str1 = "".join(list)
        file.write(str1)
def change_data_sub_rnareport(da,pfile,npfile,data_len,name,dirname):
    print(da)
    with open(f"{npfile}","w") as file:
        list = []
        with open(f"{pfile}","r") as f:
            content = f.readlines()
            for line in content:
                if line.startswith("#SBATCH --error"):
                    s =f'#SBATCH --error=rnareport_error_{name}_{data_len}\n'
                    list.append(s)
                elif line.startswith("#SBATCH -o"):
                    s =f'#SBATCH -o rnareport_output_{name}_{data_len}\n'
                    list.append(s)
                elif line.startswith("#SBATCH -J"):
                    s =f'#SBATCH -J AUTO_rnareport_{name}_{data_len}\n'
                    list.append(s)
                elif line.startswith("#SBATCH --chdir"):
                    s =f'#SBATCH --chdir={da}\n'
                    list.append(s)
                elif line.startswith("python"):
                    s =f'python send_email.py {da} {dirname}\n'
                    list.append(s)
                else:
                    list.append(line)
        str1 = "".join(list)
        file.write(str1)


def change_data_rnareport(da,pfile,npfile):
    #print(da)
    with open(f"{npfile}","w") as file:
        list = []
        with open(f"{pfile}","r") as f:
            content = f.readlines()
            for line in content:
                if line.startswith("REP_INDEX"):
                    s =f'REP_INDEX = "{da}_raw"\n'
                    list.append(s)
                else:
                    list.append(line)
        str1 = "".join(list)
        file.write(str1)


# for file_name in old_file_list:
#     os.system(f'md5sum  {file_name}  >> md5sum.txt')
# while True:

def check_file_list(mergeRawFq_dir_list):
    
    if len(mergeRawFq_dir_list) > 0:
        print(mergeRawFq_dir_list)
        RNA_dir_list = [dir for dir in mergeRawFq_dir_list if dir.startswith(virus_name)] #virus_name
        print(RNA_dir_list)
        
        for dir in RNA_dir_list:
            file_list = os.listdir(os.path.join(mergeRawFq_dir, dir))

            for name in file_list:
                # print(mergeRawFq_file_list_RNA.keys())

                if (name in mergeRawFq_file_list_RNA.keys()) is False:
                    mergeRawFq_file_list_RNA[name] = dir
        init(mergeRawFq_file_list_RNA, 1)
        
    else:
        pass


def md5_check():
    # print(mergeRawFq_file_list_RNA)
   
        for name,dir in mergeRawFq_file_list_RNA.items():
            if name in ok_filelist_RNA.keys():
                continue
            file_dir = os.path.join(os.path.join(mergeRawFq_dir,dir),name)
            if not file_dir.endswith(".fq.gz"):
                continue
            try:
                if os.path.isdir(file_dir):
                    continue
                with open(f"{file_dir}", "rb") as f:
                    content = f.read()
                    md5hash = hashlib.md5(content)
                    md5 = md5hash.hexdigest()
                #print(md5)

                if (md5 in md5_list) is True and name.endswith(".fq.gz"):
                    if (dir[0] == virus_name): #virus_name
                        ok_filelist_RNA[name] = dir                 
            except FileNotFoundError:
                continue
            except IsADirectoryError:
                continue
        

def ok_file_run_RNA():
    print(ok_filelist_RNA)
    
    global exc_file_RNA
    for name,dir in ok_filelist_RNA.items():
        
        if dir in file_execute_RNA.keys():
            if file_execute_RNA[dir] is True:
                # 该文件已执行过脚本 略过
                print(f"The {dir} has ran the RNA.py")

            else:
                # 该文件执行脚本
                file_1_name = dir + "_raw_1.fq.gz"
                file_2_name = dir + "_raw_2.fq.gz"
                run_dir = os.path.join(mergeRawFq_dir, ok_filelist_RNA[name])
                # print(run_dir)
                # print(os.path.join(mergeRawFq_dir, ok_filelist_RNA[name]))
                if (file_1_name in ok_filelist_RNA.keys()) ==True and (file_2_name in ok_filelist_RNA.keys()) ==True:
                        
                    print(f"{dir} run success")
                    print(run_dir)
                    file_execute_RNA[dir] = True
                    run_py(virus_name,run_dir,data_name,exc_file_RNA,dir) 
                    exc_file_RNA = exc_file_RNA + 1   
                    
                        
                else:
                    print(f"{dir} run Failed")

            sys.stdout.flush()

def transform_path(path):
    return 1

def check_end():
    ok_file = len(ok_filelist_RNA.keys()) / 2
    time.sleep(5)
    excet_file = 0
    for k,v in file_execute_RNA.items():
        if v == True:
            excet_file = excet_file + 1 
    time.sleep(5)
    merge_list = os.listdir(mergeRawFq_dir)
    all_file = len([dir for dir in merge_list if dir.startswith(virus_name)]) #virus_name
    print(f"ok:{ok_file}")
    print(f"EX:{excet_file}")
    print(f"ALL:{all_file}")
    
    if (ok_file == excet_file) and (ok_file == all_file) and (excet_file == all_file) and (ok_file > 0):
        print("auto end")
        sys.exit()
    time.sleep(20)
    if (all_file == 0) and (ok_file == 0) and (excet_file == 0) :
        print("auto end")
        sys.exit()

          
def loop_task():
    mergeRawFq_dir_list = os.listdir(mergeRawFq_dir)
    #print(mergeRawFq_dir_list)
    check_file_list(mergeRawFq_dir_list)
    md5_check()
    ok_file_run_RNA()
    check_end()

def modify_parm(dir_name):
    with open("para.txt","r") as f:
        content = f.readlines()
        with open("parameters.txt","w+") as f_m:
            
            filename = '"'+dir_name+'_raw"' + "\n"
            rep = f"rep: {filename}"
            content[0] = rep
            #print(content)
            f_m.write("".join(content))
            f_m.flush()
        with open("parametersI.txt","w+") as f_m:
            
            filename = '"'+dir_name+'_raw"' + "\n"
            rep = f"rep: {filename}"
            content[0] = rep
            #print(content)
            f_m.write("".join(content))
            f_m.flush()
def modify_parm_rna(dir_name):
    with open("rna_code12.py","r") as f:
        content = f.readlines()
        with open("report_code12.py","w+") as f_m :
            filename = '"'+dir_name+'_raw"' + "\n"
            rep = f"REP_INDEX = {filename}"
            content[12] = rep
            #print(content)
            f_m.write("".join(content))
            f_m.flush()
        

if __name__== "__main__":
    command_list = ["-d", "--dicrectory","-e","--end","-dna","-rna","-data","-v"]
    
    dir_name = "."
    dna_name = "DNA.py"
    rna_name = "RNA.py"
    end_name = ".txt"
    if "-d" in sys.argv:
        try:
            j = sys.argv.index("-d")
            dir_name = sys.argv[j + 1]
        except IndexError:
            pass
    else:
        pass
    if "-data" in sys.argv:
        try:
            j = sys.argv.index("-data")
            data_name = sys.argv[j + 1]
        except IndexError:
            pass
    else:
        pass
    if "-v" in sys.argv:
        try:
            j = sys.argv.index("-v")
            virus_name = sys.argv[j + 1]
        except IndexError:
            pass
    else:
        pass


    if "--dicrectory" in sys.argv:
        try:
            j = sys.argv.index("-d")

            dir_name = sys.argv[j + 1]
        except IndexError:
            pass
    else:
        pass
    if "-e" in sys.argv:
        try:
            j = sys.argv.index("-e")
            end_name = sys.argv[j + 1]
        except IndexError:
            pass
    else:
        pass
    if "--end" in sys.argv:
        try:
            j = sys.argv.index("--end")
            end_name = sys.argv[j + 1]
        except IndexError:
            pass
    else:
        pass
    if "-dna" in sys.argv:
        try:
            j = sys.argv.index("-dna")
            list_dir = "/".join(sys.argv[j + 1].split("\\"))
            # list_dir.insert(2, "\\")
            dna_name = sys.argv[j + 1]
        except IndexError:
            pass
    else:
        pass
    if "-rna" in sys.argv:
        try:
            j = sys.argv.index("-rna")
            # list_dir = list("\\".join(sys.argv[j + 1].split("\\")))
            # list_dir.insert(2, "\\")
            # print(list_dir)
            rna_name = sys.argv[j + 1]

        except IndexError:
            pass
    else:
        pass

    dir_name = os.path.abspath(dir_name).replace("\\","/")
    print(dir_name)
    flag_dir = dir_name
    MD5_dir = os.path.join(dir_name, "MD5.txt").replace("\\\\","/")
    mergeRawFq_dir = os.path.join(dir_name, "00.mergeRawFq").replace("\\","/")
    mergeRawFq_dir_list = os.listdir(mergeRawFq_dir)
    md5_list = []

    with open(MD5_dir,"r") as md5_file:
        list = md5_file.readlines()
        md5_list = [line[:32] for line in list]
    i = 0

    while 1==1:
        
        loop_task()
        sys.stdout.flush()
        time.sleep(20)
        i = i + 1
    



