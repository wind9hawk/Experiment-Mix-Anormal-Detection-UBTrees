# coding:utf-8

# 本模块用于利用提出的层次化特征方法来进行基础异常检测，目的是通过70个Insiders与70个NormalUsers的实验，
# 查看当前方法存在的问题，并根据其问题提出改进，完善深入现有的异常检测研究方法

# 主要工作算法：
# Step-1: 确定要分析的用户列表，从Insiders文件中读取全部70个恶意用户，然后从整体用户中不重复、随机抽取70个Normal Users。
# Step-2：针对每个用户，分别进行UBT检测：
# 2.1: 初始化工作（指定user_id, DirPath, 计算得到要分析的月份数据目录，计算出WorkOnTime与WorkOffTime，初始化相关列表、阈值判断）
# 2.2： UBT检测过程
# 2.3  输出保存到相应的Features目录
# 2.4: 重复分析所有的用户
# Step-3: 针对得到的所有用户的Features目录，根据其是否属于Insiders，计算其六元组：
# 3.1 user_id, Cnt_Pos_Days, Cnt_Normal_Days, Cnt_TP_Days, Cnt_FP_Days， Line_Recall Rate, Line_FP_Rate
# 3.2 四元组追加到Users_4_Results列表，存储为相应的文件
# Step-4: 针对六元组文件，计算整体的Recall/FP，即对应列的和的比值
# 可以根据k_std的范围绘制ROC曲线

import sys
import os
import numpy as np

import random

import Train_Normal_Model
import WorkTime
import Anormaly_Detection
import Anormaly_Detection_ColZScore

print '实验程序开始...\n'


print '读取确定要分析的用户列表（69Insiders + 70NormalUsers）...\n'
# 从CERT4.2-2009-12中读取用户列表
# 从CERT4.2_Daily_Insiders中读取所有的Insiders列表，放到最终Users_lst的前部
Users_lst = []
# 设置根目录，所有相关数据目录均在其下的子目录
Root_DirPath = r'H:\CERT_Result\Experiment\Experiment-Mix-Anormal Detection-UBTrees'
Insiders_DirPath = Root_DirPath + '\\' + 'CERT4.2_Daily_Insiders'
NormalUsers_FilePath = Root_DirPath + '\\' + 'CERT4.2-2009-12.csv'
for user in os.listdir(Insiders_DirPath):
    Users_lst.append(user)
print 'Insiders append success..\n'

# 读取Normal Users
f_nor_users = open(NormalUsers_FilePath, 'r')
f_nor_users_lst = f_nor_users.readlines()
f_nor_users.close()
print '构造user_id与email账户的映射列表...\n'
User_Map_Email = []
# employee_name,user_id,email,role,business_unit,functional_unit,department,team,supervisor
for line in f_nor_users_lst:
    line_lst = line.strip('\n').strip(',').split(',')
    if line_lst[1] == 'user_id':
        continue
    User_M_Map = []
    User_M_Map.append(line_lst[1])
    User_M_Map.append(line_lst[2])
    User_Map_Email.append(User_M_Map)
print 'user_id与Email关联列表建立完成...\n'

Cnt_Insiders = len(Users_lst)
i = 0
while i < Cnt_Insiders:
    # 从1-1000的索引中随机挑选，判断如果不在Users_lst中，则添加，否则继续挑选
    # employee_name,user_id,email,role,business_unit,functional_unit,department,team,supervisor
    x = random.randint(1, 1000)
    line_lst = f_nor_users_lst[x].strip('\n').strip(',').split(',')
    if line_lst[1] not in Users_lst:
        Users_lst.append(line_lst[1])
        i += 1
        continue
    else:
        continue
f_users = open(r'CERT4.2-2009-12-TestUsers.csv', 'w')
for user in Users_lst:
    f_users.write(user)
    f_users.write('\n')

f_users.close()
print '测试用户列表生成完毕，且存储在根目录下的CERT4-2009-12-TestUsers.csv中...\n'

print '开始对每个用户进行UBT检测...\n'

# 检测初始化
# 最终要得到的用户四元组
# 每个用户的四元组均应包含：
# 1. 该用户的恶意天数：Cnt_Insiders_Days
# 2. 该用户的正常天数：Cnt_NorUsers_Days
# 3. 该用户识别为异常的天数中的TP：Cnt_TP_Days
# 4. 该用户识别为异常的天数中的FP：Cnt_FP_Days
Users_4_Results_lst = []


for user in Users_lst[:70]:
    if user != 'AAF0535':#''AAF0535':
        continue
    Cnt_Insiders_Days = 0
    Cnt_NorUsers_Days = 0
    Cnt_TP_Days = 0
    Cnt_FP_Days = 0

    # 开始Normal_model的训练
    Normal_Records = []
    Normal_Features = []
    Normal_Features_W = []
    Abnormal_Features = []
    Abnormal_Features_W = []
    WorkOn_Time, WorkOff_Time = WorkTime.Ext_Work_Hours(user, Insiders_DirPath)
    Normal_Features, Normal_Features_Ori_W, Normal_Records = Train_Normal_Model.Train_Normal_Model(user, Insiders_DirPath, Normal_Records, Normal_Features, User_Map_Email)
    print len(Normal_Features), '\t', Normal_Features[0], '\n'
    print '初始Normal Model构建完毕...\n'
    Normal_Features_Original = []
    for line in Normal_Features_Ori_W:
        Normal_Features_Original.append(line)
    # print Normal_Features_Original, '\n'
    for line in Normal_Features_Original:
        print line, '\n'
    # sys.exit()

    # 由于训练假设引入的收敛过程，导致第一周的S-D等属性异常，不能代表正常偏移，故去掉第一周（前5个特征），不参与后续特征矩阵异常检测
    i = 0
    while i < 5:
        print '第 ', i, '\t', Normal_Features[0], '\n'
        del Normal_Features[0]
        i += 1
    print 'Normal_Features 长度为： ', len(Normal_Features), '\n'
    print '删除前5个后第一个特征为： ', Normal_Features[0], '\n'
    j = 1
    for line in Normal_Features:
        print j, '\t', line, '\n'
        j += 1
    # sys.exit()

    print '开始确定测试数据集，并提交给判断函数...\n'

    # 确定用户对应的数据中测试部分
    Day_Features_pca_scale = []
    K_std = 3
    K_domain = 1
    K_day = 1
    MonthPath = Insiders_DirPath + '\\' + user
    Month_No = 1
    MonthList = os.listdir(MonthPath)
    while Month_No < len(MonthList):
        FilesDir = MonthPath + '\\' + MonthList[Month_No]
        Month_No += 1
        for file in os.listdir(FilesDir):
            filePath = FilesDir + '\\' + file
            f = open(filePath, 'r')
            f_lst = f.readlines()
            f.close()
            print user, 'Test File ', file, ' 读取完毕...\n'
            Day_Features, Day_Records = Train_Normal_Model.Extract_Normal_Features(user, f_lst, Normal_Records, WorkOn_Time, WorkOff_Time, User_Map_Email)
            # print Day_Features, '\n'
            # sys.exit()
            # 得到了新一天的行为特征，开始判断该天是否为异常，输入Day_Features, Normal_Features
            # 如果该天判断正常，则Day_Features添加到Normal_Features中，逐条记录添加到Normal_Records
            # 如果该天判断异常，则Day_Features添加到Abnormal_Features中
            # 定义一个异常检测函数，判断返回'A'或'N'
            feat, A_N_Flag = Anormaly_Detection.Anormaly_Detection(Day_Features, Normal_Features, K_std, K_domain, K_day)
            Day_tmp_pca_scale = []
            Day_tmp_pca_scale.append(file)
            Day_tmp_pca_scale.append(feat)
            Day_Features_pca_scale.append(Day_tmp_pca_scale)
            if A_N_Flag == 'Normal':
                Normal_Features.append(Day_Features)
                Normal_Features_tmp = []
                Normal_Features_tmp.append(file)
                Normal_Features_tmp.append(Day_Features)
                Normal_Features_W.append(Normal_Features_tmp)
                for line in Day_Records:
                    Normal_Records.append(line)
                print file, ' has been done...\n'
                continue
            else:
                Abnormal_Features.append(Day_Features)
                Abnormal_Features_tmp = []
                Abnormal_Features_tmp.append(file)
                Abnormal_Features_tmp.append(Day_Features)
                Abnormal_Features_W.append(Abnormal_Features_tmp)
                print file, ' has been done...\n'
                continue
    print '将处理的数据存放到指定目录...\n'
    DirName = 'CERT4.2_Daily_Features_AAF0535'
    Result_DirPath = Root_DirPath + '\\' + DirName + '\\' + user
    NormalPath = Result_DirPath + '\\' + 'Normal.csv'
    AbnormalPath = Result_DirPath + '\\' + 'Abnormal.csv'
    PCA_Scale_Path = Result_DirPath + '\\' + 'Day_Features_pca_scale.csv'
    NormalOriPath = Result_DirPath + '\\' + 'Normal_Original.csv'

    # utf-8编码下涉及中文字符时一定要decode('utf-8')才可以作为参数被python解释器识别
    isExit = os.path.exists(Result_DirPath.decode('utf-8'))
    print isExit,'\n'
    if isExit == False:
        os.makedirs(Result_DirPath.decode('utf-8'))

    f_nor = open(NormalPath, 'w')
    f_anor = open(AbnormalPath, 'w')
    f_pca_scale = open(PCA_Scale_Path, 'w')
    f_nor_ori = open(NormalOriPath, 'w')

    for line in Normal_Features_W:
        print line, '\n'
        for ele in line:
            f_nor.write(str(ele))
            f_nor.write(',')
        f_nor.write('\n')
    for line in Abnormal_Features_W:
        for ele in line:
            f_anor.write(str(ele))
            f_anor.write(',')
        f_anor.write('\n')
    for line in Day_Features_pca_scale:
        for ele in line:
            f_pca_scale.write(str(ele))
            f_pca_scale.write(',')
        f_pca_scale.write('\n')
    for line in Normal_Features_Original:
        for ele in line:
            f_nor_ori.write(str(ele))
            f_nor_ori.write(',')
        f_nor_ori.write('\n')
    f_nor.close()
    f_anor.close()
    f_pca_scale.close()
    print user, ' 分析完毕...\n'


print '基础检测程序执行完毕...\n'
sys.exit()



