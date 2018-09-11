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

# 基于基础异常检测实验结果，开始对于异常检测方法进行改进
# 主要问题：
# 1. 对于HTTP异常记录而言，比如S-D模式出现数量异常，但是PCA-2后求和无法体现该项的变化，分析原因可能是异常体现在单个特征而非某些特征
# 的集合上，因此整体分析PCA-2结果不明显
# 2. 由于实现的分类方法中Normal集合自动更新，导致如果存在漏报则会触发雪崩效应，导致后续更多的漏报；

# 改进方法一：
# 对于单个域的异常判断进行改进，不再使用PCA，而是直接对原始列做ZScore，即scale标准化，从而表现出单个行为模式的数量异常
# 若某个行为域中，存在K_Mode个行为模式异常（如S-S或S-D），则判定该行为域当天异常；
# 接下来结合K_Domain与K_Day判断即可

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
    # Analytic_Metrix即我们要分析的特征矩阵
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
    # Logon_feats_nor = Normalizer(norm='l2').fit_transform(Logon_feats_array)
    # File_feats_nor = Normalizer(norm='l2').fit_transform(File_feats_array)
    # HTTP_feats_nor = Normalizer(norm='l2').fit_transform(HTTP_feats_array)
    # Device_feats_nor = Normalizer(norm='l2').fit_transform(Device_feats_array)
    # Email_feats_nor = Normalizer(norm='l2').fit_transform(Email_feats_array)

    # 在PCA-2前首先进行MinMax，避免量纲的影响
    # min_max = MinMaxScaler()
    # Logon_feats_nor = min_max.fit_transform(Logon_feats_array)
    # File_feats_nor = min_max.fit_transform(File_feats_array)
    # HTTP_feats_nor = min_max.fit_transform(HTTP_feats_array)
    # Device_feats_nor = min_max.fit_transform(Device_feats_array)
    # Email_feats_nor = min_max.fit_transform(Email_feats_array)



    # 提取出特征矩阵中对应的Logon/File/HTTP/Device/Email部分后，接下来开始针对每个域分别进行scale
    # 然后统计每个域中scale大于K_std的个数

    # 标准化
    Day_Features_logon_scale = scale(Logon_feats_array, axis=0)
    Day_Features_file_scale = scale(File_feats_array, axis=0)
    Day_Features_http_scale = scale(HTTP_feats_array, axis=0)
    Day_Features_device_scale = scale(Device_feats_array, axis=0)
    Day_Features_email_scale = scale(Email_feats_array, axis=0)

    Day_Features_scale = []
    j = 0
    while j < len(Day_Features_logon_scale):
        Day_feat_pca = []
        Day_feat_pca.append(Day_Features_logon_scale[j])
        Day_feat_pca.append(Day_Features_file_scale[j])
        Day_feat_pca.append(Day_Features_http_scale[j])
        Day_feat_pca.append(Day_Features_device_scale[j])
        Day_feat_pca.append(Day_Features_email_scale[j])
        j += 1
        Day_Features_scale.append(Day_feat_pca)

    # 对每天的特征基于每天的单域上异常时间段的新特征
    # 如[2,1,0,2]
    # Logon: [0, 0, 0, 0, 2.0, 0, 0, 0, 0, 0, 0, 0]
    # File: [0, 0, 0, 0, 0, 4.0, 0, 0, 0, 0, 0, 0]
    # HTTP: [0, 0, 0, 0, 29.0, 0, 0, 0, 0, 0, 0, 0]
    # Device: [0, 0, 0, 0, 6.0, 0, 0, 0, 0, 0, 0, 0]
    # Email: [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 3.0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
    Day_Features_Domain_Labels = []
    i = 0
    while i < len(Day_Features_logon_scale):
        Day_feat_Domain_Labels = []
        # 分析Logon
        Cnt_Logon_Domain = 0
        for feat in Day_Features_logon_scale[i]:
            if abs(feat) > K_std:
                Cnt_Logon_Domain += 1
            else:
                continue
        Day_feat_Domain_Labels.append(Cnt_Logon_Domain)

        # 分析file
        Cnt_File_Domain = 0
        for feat in Day_Features_file_scale[i]:
            if abs(feat) > K_std:
                Cnt_File_Domain += 1
            else:
                continue
        Day_feat_Domain_Labels.append(Cnt_File_Domain)

        # 分析HTTP
        Cnt_HTTP_Domain = 0
        for feat in Day_Features_http_scale[i]:
            if abs(feat) > K_std:
                Cnt_HTTP_Domain += 1
            else:
                continue
        Day_feat_Domain_Labels.append(Cnt_HTTP_Domain)

        # 分析Device
        Cnt_Device_Domain = 0
        for feat in Day_Features_device_scale[i]:
            if abs(feat) > K_std:
                Cnt_Device_Domain += 1
            else:
                continue
        Day_feat_Domain_Labels.append(Cnt_Device_Domain)

        # 分析Email
        Cnt_Email_Domain = 0
        for feat in Day_Features_email_scale[i]:
            if abs(feat) > K_std:
                Cnt_Email_Domain += 1
            else:
                continue
        Day_feat_Domain_Labels.append(Cnt_Email_Domain)
        Day_Features_Domain_Labels.append(Day_feat_Domain_Labels)

        i += 1
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
        return Day_Features_scale[-1], 'Abnormal'
    else:
        return Day_Features_scale[-1], 'Normal'














