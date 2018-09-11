# coding:utf-8

import os
import sys
from sklearn.decomposition import PCA
from sklearn.preprocessing import Normalizer
from sklearn.preprocessing import scale

import numpy as np


print '实验对于略微差异的多组数据其Nomalizer与PCA-2/scale的影响...\n'

Test_lst = []
Test_lst.append([2.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0])
Test_lst.append([0.0,0.0,0.0,0.0,2.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0])

# Normalzier结果，默认2范数
Test_array = np.array(Test_lst)
Test_array_nor = Normalizer().fit_transform(Test_array)
print 'Normalizer is ', Test_array_nor, '\n'

# PCA结果
pca = PCA(n_components=2)
Test_array_nor_pca_0 = pca.fit_transform(Test_array_nor[:,:4])
print 'PCA is ', Test_array_nor_pca_0, '\n'

# scale结果
Test_array_nor_pca_scale = scale(Test_array_nor_pca_0)
print 'Scale is ', Test_array_nor_pca_scale, '\n'


# scale测试
a = [14, -11, 8, -6, -4, 5, -2, -4, 3, 1, -4, 1, 0, 1, -2, 0, 1, -1, 1]
a_array = np.array(a)
print 'a after scale is ', scale(a), '\n'
sys.exit()
