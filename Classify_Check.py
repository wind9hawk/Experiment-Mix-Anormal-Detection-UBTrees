# coding:utf-8

# 本模块主要用于分析基础异常检测得到的结果，即判断出的Abnormal Days中有多少是TP/FP，还有Recall率
# 需要针对每个用户建立四元组，其中包含：
# user_id = [Cnt_Insiders_Days, Cnt_Normal_Days, Cnt_TP_Days, Cnt_FP_Days]
# 之所以需要分别对每个用户进行单独计数，是为了既可以显示基础异常检测算法在每个用户上的检测效果，又可以体现对于所有1000个用户的整体效果

import os
import sys
import numpy as np


# 定义一个时间提取函数
def Extract_Date(date):
    # 01/02/2010 02:19:18
    year = date[6:10]
    month = date[0:2]
    day = date[3:5]
    hour = date[11:13]
    minute = date[14:16]
    seconds = date[17:]
    # 字符串类型用于比价是否存在，float后用于比较时间先后
    return year, month, day, hour, minute,  seconds

# 给定user_id与数据目录，返回该用户对应的真实的恶意记录
def Extract_Insider_Days(user_id, Insiders_Days_Path):
    # 确定该用户的数据位置
    #for user in os.listdir(Insiders_Days_Path):
    #    if user_id in user:
    # 构造该用户对应的恶意数据文件路径
    Insider_Path = Insiders_Days_Path + '\\' + user_id
    print Insider_Path, '\n'
    f_insider = open(Insider_Path, 'r')
    f_insider_lst = f_insider.readlines()
    f_insider.close()
    return f_insider_lst


# 给定一组数据记录，自动提取出其中包含的所有天数
def Extract_Days(f_lst):
    Days = []
    for line in f_lst:
        line_lst = line.strip('\n').strip(',').split(',')
        # logon,{K3V4-Y4OK65SI-1583GEOQ},10/23/2010 01:34:19,AAM0658,PC-9923,Logon
        year, month, day, hour, minute,  seconds = Extract_Date(line_lst[2])
        date_0 = year + '-' + month + '-' + day # 2010-10-23
        if date_0 not in Days:
            Days.append(date_0)
            continue
        else:
            continue
    return Days



print '统计所有用户的四元组...\n'

Root_Results_Path = r'H:\CERT_Result\Experiment\Experiment-Mix-Anormal Detection-UBTrees\CERT4.2_Daily_Features'
Insiders_Days_Path = r'H:\CERT_Result\Experiment\Experiment-Mix-Anormal Detection-UBTrees\r4.2_insiders'

# 需要将Results与Insiders_Days_Path进行比较
# 对于Normal_Users只需要统计FP

print '初始化Insiders用户列表...\n'
Insiders_lst = []
for user in os.listdir(Insiders_Days_Path):
    # r4.2-1-AAM0658
    Insiders_lst.append(user)
print 'Len of Insiders is ', len(Insiders_lst), '\n'
print Insiders_lst[0:10], '\n'
print '初始化四元组..\n'
Users_4_Results_lst = []


for user in os.listdir(Root_Results_Path)[:]:
    # user_id = [Cnt_Insiders_Days, Cnt_Normal_Days, Cnt_TP_Days, Cnt_FP_Days]
    Users_4_Results_tmp = []
    # if user in Insiders_lst:
    Flag_insider = 0
    #
    #
    #
    # 特别注意：列表的in方法必须执行完美匹配，即匹配项user必须与列表中的项完全一样才可以得到正确结果
    for insider in Insiders_lst:
        if user in insider:
        # 这是一个恶意用户
            print user, 'is a insider..\n'
            Flag_insider += 1
            Insider_Record_lst = Extract_Insider_Days(insider, Insiders_Days_Path)
            print 'Insider_Record_lst is ', Insider_Record_lst, '\n'
            # 构造结果特征中的Abnormal与Normal文件路径
            User_Abnormal_Path = Root_Results_Path + '\\' + user + '\\' + 'Abnormal.csv'
            User_Normal_Path = Root_Results_Path + '\\' + user + '\\' + 'Normal.csv'
            f_abnormal = open(User_Abnormal_Path, 'r')
            f_abnormal_lst = f_abnormal.readlines()
            f_normal = open(User_Normal_Path, 'r')
            f_normal_lst = f_normal.readlines()
            f_normal.close()
            f_abnormal.close()
            # print user, '\t', f_abnormal_lst, '\n'
            # sys.exit()

            # 比较确定结果
            # user_id = [Cnt_Insiders_Days, Cnt_Normal_Days, Cnt_TP_Days, Cnt_FP_Days]

            Cnt_Insiders_Days = 0
            Cnt_Normal_Days = 0
            Cnt_TP_Days = 0
            Cnt_FP_Days = 0
            Insiders_Days_lst = []
            Normal_Days_lst = []
            TP_Days_lst = []
            FP_Days_lst = []

            Insiders_Days_lst = Extract_Days(Insider_Record_lst)
            print 'Insiders_Days_lst is ', Insiders_Days_lst, '\n'
            Cnt_Insiders_Days = len(Insiders_Days_lst)

            for line in f_abnormal_lst:
                line_lst = line.strip('\n').strip(',').split(',')
                if line_lst[0][0:10] in Insiders_Days_lst:
                    Cnt_TP_Days += 1
                else:
                    Cnt_FP_Days += 1
            Cnt_Normal_Days = len(f_abnormal_lst) + len(f_normal_lst) - Cnt_Insiders_Days
            Users_4_Results_tmp.append(user)
            Users_4_Results_tmp.append(Cnt_Insiders_Days)
            Users_4_Results_tmp.append(Cnt_Normal_Days)
            Users_4_Results_tmp.append(Cnt_TP_Days)
            Users_4_Results_tmp.append(Cnt_FP_Days)
            Users_4_Results_lst.append(Users_4_Results_tmp)
            break
        else:
            continue
    if Flag_insider == 0:
        # 正常用户
        User_Abnormal_Path = Root_Results_Path + '\\' + user + '\\' + 'Abnormal.csv'
        User_Normal_Path = Root_Results_Path + '\\' + user + '\\' + 'Normal.csv'
        f_abnormal = open(User_Abnormal_Path, 'r')
        f_abnormal_lst = f_abnormal.readlines()
        f_normal = open(User_Normal_Path, 'r')
        f_normal_lst = f_normal.readlines()
        f_normal.close()
        f_abnormal.close()
        Cnt_FP_Days = len(f_abnormal_lst)
        Cnt_TP_Days = 0
        Cnt_Insiders_Days = 0
        Cnt_Normal_Days = len(f_abnormal_lst) + len(f_normal_lst)
        Users_4_Results_tmp.append(user)
        Users_4_Results_tmp.append(Cnt_Insiders_Days)
        Users_4_Results_tmp.append(Cnt_Normal_Days)
        Users_4_Results_tmp.append(Cnt_TP_Days)
        Users_4_Results_tmp.append(Cnt_FP_Days)
        Users_4_Results_lst.append(Users_4_Results_tmp)



Recall_Rate = 0.0
TP_Rate = 0.0
FP_Rate = 0.0

Cnt_Insiders_Days_Sum = 0.0
Cnt_Normal_Days_Sum = 0.0
Cnt_TP_Days_Sum = 0.0
Cnt_FP_Days_Sum = 0.0

f_Users_4_Results = open(r'CERT4.2-2009-12-4Results.csv', 'w')
for line in Users_4_Results_lst:
    print line, '\n'
    Cnt_Insiders_Days_Sum += line[1]
    Cnt_Normal_Days_Sum += line[2]
    Cnt_TP_Days_Sum += line[3]
    Cnt_FP_Days_Sum += line[4]

    for ele in line:
        f_Users_4_Results.write(str(ele))
        f_Users_4_Results.write(',')
    f_Users_4_Results.write('\n')
f_Users_4_Results.close()

if Cnt_Insiders_Days_Sum == 0:
    Recall_Rate = 'none'
else:
    Recall_Rate = Cnt_TP_Days_Sum / Cnt_Insiders_Days_Sum
    TP_Rate = Cnt_TP_Days_Sum / (Cnt_TP_Days_Sum + Cnt_FP_Days_Sum)
    FP_Rate = Cnt_FP_Days_Sum / Cnt_Normal_Days_Sum

print 'Recall Rate is ', Recall_Rate, '\n'
print 'TP Rate is ', TP_Rate, '\n'
print 'FP Rate is ', FP_Rate, '\n'






