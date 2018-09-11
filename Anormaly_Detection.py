# coding:utf-8

import os
import sys
import numpy as np

from sklearn.preprocessing import Normalizer
from sklearn.preprocessing import scale
from sklearn.decomposition import PCA
from sklearn.preprocessing import MinMaxScaler

# 定义一个异常检测函数模块，输入要分析的Day_Features, 比较的Normal_Features，
# 列异常阈值（标准差倍数）K_std, 域异常阈值K_domain, 记录异常阈值K_day
def Anormaly_Detection(Day_Features, Normal_Features, K_std, K_domain, K_day):
    # 首先分别提取各个行为域的特征
    Logon_feats = []
    File_feats = []
    HTTP_feats = []
    Device_feats = []
    Email_feats = []
    Day_Features_pca = []
    Analytic_Matrix = []
    for line in Normal_Features:
        Analytic_Matrix.append(line)
    print Day_Features, '\n'
    Analytic_Matrix.append(Day_Features)
    # 对于当天的记录，对于所有的域行为进行Normalizer，而非仅针对单一的域
    Analytic_Matrix_lst= []
    for line in Analytic_Matrix:
        tmp = []
        for ele in line:
            tmp.extend(ele)
        Analytic_Matrix_lst.append(tmp)
    Analytic_Matrix_array = np.array(Analytic_Matrix_lst)
    # Analytic_Matrix_nor = Normalizer().fit_transform(Analytic_Matrix_array)
    Cnt_No= 0
    for line in Analytic_Matrix_array:
        print Cnt_No, ': line is', len(line), line, '\n'
        Cnt_No += 1
        Logon_feats.append(line[:12])
        File_feats.append(line[12:24])
        HTTP_feats.append(line[24:36])
        Device_feats.append(line[36:48])
        Email_feats.append(line[48:])
    Logon_feats_array = np.array(Logon_feats)
    File_feats_array = np.array(File_feats)
    HTTP_feats_array = np.array(HTTP_feats)
    Device_feats_array = np.array(Device_feats)
    Email_feats_array = np.array(Email_feats)

    # 在PCA--2前首先进行Normalizer化
    #Logon_feats_nor = Normalizer(norm='l2').fit_transform(Logon_feats_array)
    #File_feats_nor = Normalizer(norm='l2').fit_transform(File_feats_array)
    #HTTP_feats_nor = Normalizer(norm='l2').fit_transform(HTTP_feats_array)
    #Device_feats_nor = Normalizer(norm='l2').fit_transform(Device_feats_array)
    #Email_feats_nor = Normalizer(norm='l2').fit_transform(Email_feats_array)

    # 在PCA-2前首先进行MinMax，避免量纲的影响
    #min_max = MinMaxScaler()
    #Logon_feats_nor = min_max.fit_transform(Logon_feats_array)
    #File_feats_nor = min_max.fit_transform(File_feats_array)
    #HTTP_feats_nor = min_max.fit_transform(HTTP_feats_array)
    #Device_feats_nor = min_max.fit_transform(Device_feats_array)
    #Email_feats_nor = min_max.fit_transform(Email_feats_array)



    # 如果跳过按域：时间段的Normalizer
    Logon_feats_nor = Logon_feats_array
    File_feats_nor = File_feats_array
    HTTP_feats_nor = HTTP_feats_array
    Device_feats_nor = Device_feats_array
    Email_feats_nor = Email_feats_array

    # PCA到2
    # pca = PCA(n_components=2)
    pca = PCA(n_components=1)
    Logon_feats_pca = []
    File_feats_pca = []
    HTTP_feats_pca = []
    Device_feats_pca = []
    Email_feats_pca = []
    # 在Normalizer的基础上，对于每个域行为而言，根据不同的时间段分别PCA-2
    print 'Logon_feats is ', Logon_feats[0], '\n'
    print 'Logon_feats_array is ', Logon_feats_array[0], '\n'
    Logon_0_pca = pca.fit_transform(Logon_feats_nor[:,0:4])
    Logon_1_pca = pca.fit_transform(Logon_feats_nor[:,4:8])
    Logon_2_pca = pca.fit_transform(Logon_feats_nor[:,8:])

    # 计算File在三个时段pca后的数据特征
    File_0_pca = pca.fit_transform(File_feats_nor[:,:4])
    File_1_pca = pca.fit_transform(File_feats_nor[:,4:8])
    File_2_pca = pca.fit_transform(File_feats_nor[:,8:])
    # 计算HTTP在三个时段PCA后的数据特征
    HTTP_0_pca = pca.fit_transform(HTTP_feats_nor[:,:4])
    HTTP_1_pca = pca.fit_transform(HTTP_feats_nor[:,4:8])
    HTTP_2_pca = pca.fit_transform(HTTP_feats_nor[:,8:])

    # Device在三个时段pca后的数据特征
    Device_0_pca = pca.fit_transform(Device_feats_nor[:,:4])
    Device_1_pca = pca.fit_transform(Device_feats_nor[:,4:8])
    Device_2_pca = pca.fit_transform(Device_feats_nor[:,8:])

    # Email在三个时段后pca的数据特征
    Email_0_pca = pca.fit_transform(Email_feats_nor[:,:8])
    Email_1_pca = pca.fit_transform(Email_feats_nor[:,8:16])
    Email_2_pca = pca.fit_transform(Email_feats_nor[:,16:])
    i = 0
    while i < len(Logon_0_pca):
        # 依次将Logon/File/HTTP/Device/Email五个域三个时段的特征计算为平方和，然后计算scale
        Day_feats_pca = []
        Day_feats_pca.append(Logon_0_pca[i][0])
        Day_feats_pca.append(Logon_1_pca[i][0])
        Day_feats_pca.append(Logon_2_pca[i][0])
        Day_feats_pca.append(File_0_pca[i][0])
        Day_feats_pca.append(File_1_pca[i][0])
        Day_feats_pca.append(File_2_pca[i][0])
        Day_feats_pca.append(HTTP_0_pca[i][0])
        Day_feats_pca.append(HTTP_1_pca[i][0])
        Day_feats_pca.append(HTTP_2_pca[i][0])
        Day_feats_pca.append(Device_0_pca[i][0])
        Day_feats_pca.append(Device_1_pca[i][0])
        Day_feats_pca.append(Device_2_pca[i][0])
        Day_feats_pca.append(Email_0_pca[i][0])
        Day_feats_pca.append(Email_1_pca[i][0])
        Day_feats_pca.append(Email_2_pca[i][0])


        #Day_feats_pca.append(Logon_0_pca[i][0] * Logon_0_pca[i][0] + Logon_0_pca[i][1] * Logon_0_pca[i][1])
        #Day_feats_pca.append(Logon_1_pca[i][0] * Logon_1_pca[i][0] + Logon_1_pca[i][1] * Logon_1_pca[i][1])
        #Day_feats_pca.append(Logon_2_pca[i][0] * Logon_2_pca[i][0] + Logon_2_pca[i][1] * Logon_2_pca[i][1])
        #Day_feats_pca.append(File_0_pca[i][0] * File_0_pca[i][0] + File_0_pca[i][1] * File_0_pca[i][1])
        #Day_feats_pca.append(File_1_pca[i][0] * File_1_pca[i][0] + File_1_pca[i][1] * File_1_pca[i][1])
        #Day_feats_pca.append(File_2_pca[i][0] * File_2_pca[i][0] + File_2_pca[i][1] * File_2_pca[i][1])
        #Day_feats_pca.append(HTTP_0_pca[i][0] * HTTP_0_pca[i][0] + HTTP_0_pca[i][1] * HTTP_0_pca[i][1])
        #Day_feats_pca.append(HTTP_1_pca[i][0] * HTTP_1_pca[i][0] + HTTP_1_pca[i][1] * HTTP_1_pca[i][1])
        #Day_feats_pca.append(HTTP_2_pca[i][0] * HTTP_2_pca[i][0] + HTTP_2_pca[i][1] * HTTP_2_pca[i][1])
        #Day_feats_pca.append(Device_0_pca[i][0] * Device_0_pca[i][0] + Device_0_pca[i][1] * Device_0_pca[i][1])
        #Day_feats_pca.append(Device_1_pca[i][0] * Device_1_pca[i][0] + Device_1_pca[i][1] * Device_1_pca[i][1])
        #Day_feats_pca.append(Device_2_pca[i][0] * Device_2_pca[i][0] + Device_2_pca[i][1] * Device_2_pca[i][1])
        #Day_feats_pca.append(Email_0_pca[i][0] * Email_0_pca[i][0] + Email_0_pca[i][1] * Email_0_pca[i][1])
        #Day_feats_pca.append(Email_1_pca[i][0] * Email_1_pca[i][0] + Email_1_pca[i][1] * Email_1_pca[i][1])
        #Day_feats_pca.append(Email_2_pca[i][0] * Email_2_pca[i][0] + Email_2_pca[i][1] * Email_2_pca[i][1])

        Day_Features_pca.append(Day_feats_pca)
        i += 1
    print '当天特征pca计算单项平方和完成...\n'
    print '示例：', Day_Features_pca[0], '\n'

    # 标准化
    Day_Features_pca_scale = scale(Day_Features_pca, axis=0)

    # 对每天的特征基于每天的单域上异常时间段的新特征
    # 如[2,1,0,2]
    Day_Features_Domain_Labels = []
    # 开始从每个域进行判断
    for feat in Day_Features_pca_scale:
        Day_feat_Domain_Labels = []
        # 分析Logon行为
        Cnt_Logon_Domain = 0
        if abs(feat[0]) > K_std:
            Cnt_Logon_Domain += 1
        if abs(feat[1]) > K_std:
            Cnt_Logon_Domain += 1
        if abs(feat[2]) > K_std:
            Cnt_Logon_Domain += 1
        Day_feat_Domain_Labels.append(Cnt_Logon_Domain)

        # 分析File行为
        Cnt_File_Domain = 0
        if abs(feat[3]) > K_std:
            Cnt_File_Domain += 1
        if abs(feat[4]) > K_std:
            Cnt_File_Domain += 1
        if abs(feat[5]) > K_std:
            Cnt_File_Domain += 1
        Day_feat_Domain_Labels.append(Cnt_File_Domain)

        # 分析HTTP行为
        Cnt_HTTP_Domain = 0
        if abs(feat[6]) > K_std:
            Cnt_HTTP_Domain += 1
        if abs(feat[7]) > K_std:
            Cnt_HTTP_Domain += 1
        if abs(feat[8]) > K_std:
            Cnt_HTTP_Domain += 1
        Day_feat_Domain_Labels.append(Cnt_HTTP_Domain)

        # 分析Device行为
        Cnt_Device_Domain = 0
        if abs(feat[9]) > K_std:
            Cnt_Device_Domain += 1
        if abs(feat[10]) > K_std:
            Cnt_Device_Domain += 1
        if abs(feat[11]) > K_std:
            Cnt_Device_Domain += 1
        Day_feat_Domain_Labels.append(Cnt_Device_Domain)

        # 分析Email行为
        Cnt_Email_Domain = 0
        if abs(feat[12])> K_std:
            Cnt_Email_Domain += 1
        if abs(feat[13]) > K_std:
            Cnt_Email_Domain += 1
        if abs(feat[14]) > K_std:
            Cnt_Email_Domain += 1
        Day_feat_Domain_Labels.append(Cnt_Email_Domain)

        Day_Features_Domain_Labels.append(Day_feat_Domain_Labels)
    print '当天域标签处理完成...\n'
    print '原始的当天各域时间段特征会返回到最后一行即分析天的特征feat，供查询处理...\n'

    # 接着需要处理当天的Day_feat_Domain_Labels，其中每个字段说明该域行为偏离K_std的时间段行为个数
    # 与K_domain进一步比较确定异常的天
    Day_Features_Day_Labels = []
    for feat in Day_Features_Domain_Labels:
        Cnt_Day_Label = 0
        for ele_domain in feat:
            if ele_domain >= K_domain:
                Cnt_Day_Label += 1
        Day_Features_Day_Labels.append(Cnt_Day_Label)

    # 将该天异常的域个数直接与K_day比较
    if Day_Features_Day_Labels[-1] >= K_day:
        return Day_Features_pca_scale[-1], 'Abnormal'
    else:
        return Day_Features_pca_scale[-1], 'Normal'














