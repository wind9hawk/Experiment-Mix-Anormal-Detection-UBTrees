# coding:utf-8
# Normal_Features的示例：
# [[0, 0, 0, 0, 0, 1, 1, 0, 0, 0, 0, 0],
# [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
# [0, 0, 0, 0, 14, 15, 0, 0, 0, 0, 0, 0],
# [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
# [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]]

# 本模块主要进行完整的基础异常检测算法
# 1. 输入user_id与对应的DirPath，确定要分析的审计日志数据来源
# 2. 对于Normal数据训练Normal_Features与Normal_Records
# 3. 对于新一天的记录，进行异常检测测试算法分析：
# 3.1 对于新一天的数据构建其当天特征；
# 3.2 构建N+1天的特征矩阵，N代表Normal_Features的特征向量个数，问题转化为判断最后一行与前N行的偏移；
# 3.3 基于不同的域，即特征的五个子列表，分别针对三个时间段进行Normalized--->PCA-->2，以2项的平方和代表该时间段的对应域分数
# 3.4 对每列的域分数标准化，即计算Z分数的标准差倍数作为该天的特征；
# 3.5 对于每域而言，如果某列的分数超过2个标准差（+-），则标记该列异常；初始情况，若某域的三个时间段分数有一个异常，则该域异常；
# 3.6 若一天的记录中异常域的个数大于等于2，则标记该天异常；若异常则添加到Abnormal_Days，否则追加到Normal_Records中
# 上述充分考虑了用户行为变化对Normal_Model的影响，使得Normal_Model可以随时间进化

import os
import sys
import numpy as np

import WorkTime
import Train_Normal_Model
import Anormaly_Detection

from sklearn.preprocessing import Normalizer
from sklearn.decomposition import PCA
from sklearn.preprocessing import scale




print '基础异常检测的主函数，其关键参数有列异常阈值（标准差倍数）、域行为异常阈值（异常时间段个数）以及天行为异常阈值（异常域个数）...\n'
print '初始情况为最严格，即列异常阈值为+-2，域行为异常阈值为1， 天行为异常阈值为2...\n'

print '函数化实现，开始主函数...\n'
# 确定用户列表与共同的上级DirPath
# 一个用户为测试使用
user_id = 'AAM0658'
DirPath = r'H:\CERT_Result\Experiment\Experiment-Mix-Anormal Detection-UBTrees\CERT4.2_Daily_Insiders'
# 开始Normal_model的训练
Normal_Records = []
Normal_Features = []
Normal_Features_W = []
Abnormal_Features = []
Abnormal_Features_W = []
WorkOn_Time, WorkOff_Time = WorkTime.Ext_Work_Hours(user_id, DirPath)
Normal_Features, Normal_Records = Train_Normal_Model.Train_Normal_Model(user_id, DirPath, Normal_Records, Normal_Features)
print len(Normal_Features), '\t', Normal_Features[0], '\n'
print '初始Normal Model构建完毕...\n'
# sys.exit()
print '开始确定测试数据集，并提交给判断函数...\n'

# 确定用户对应的数据中测试部分
Day_Features_pca_scale = []
K_std = 2
K_domain = 1
K_day = 1
MonthPath = DirPath + '\\' + user_id
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
        print user_id, 'Test File ', file, ' 读取完毕...\n'
        Day_Features, Day_Records = Train_Normal_Model.Extract_Normal_Features(user_id, f_lst, Normal_Records, WorkOn_Time, WorkOff_Time)
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
DstDir = r'H:\CERT_Result\Experiment\Experiment-Mix-Anormal Detection-UBTrees'
DirName = 'CERT4.2_Daily_Features'
DirPath = DstDir + '\\' + DirName + '\\' + 'AAM0658'
NormalPath = DirPath + '\\' + 'Normal.csv'
AbnormalPath = DirPath + '\\' + 'Abnormal.csv'
PCA_Scale_Path = DirPath + '\\' + 'Day_Features_pca_scale.csv'

f_nor = open(NormalPath, 'w')
f_anor = open(AbnormalPath, 'w')
f_pca_scale = open(PCA_Scale_Path, 'w')

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

f_nor.close()
f_anor.close()
f_pca_scale.close()
sys.exit()



