# PmCompQC

颗粒物组分数据质量控制(Particle Matters Composition Data Quality Control)是针对组分网获取的全国各超级站颗粒物组分数据进行质量控制。
由于全国各地超级站正在建设并陆续接入观测数据，目前进行算法实验和质控测试的数据是基于2019年历史数据，该数据的描述请参考 [Pm_comp](http://47.92.132.84:3000/data/Pm_comp)。

### 0. 颗粒物组分

颗粒物组分包括以下各类组分：

+ 在线水溶性离子：Ca2+、Mg2+、K+、NH4+、Na+、SO42-、NO3-、Cl-、F-；
+ 在线碳组分离子：OC、EC；
+ 在线重金属离子：Pb、Se、Hg、Cr、Cd、Zn、Cu、Ni、Fe、Mn、Ti、Sb、Sn、V、Ba、As、Ca、K、Co、Mo、Ag、Sc、TI、Pd、Br、Te、Ga、Cs、Si、Al。


### 1. 输入数据

**Pm_comp** 数据集包含从数据库提取重构的2019年82个站点8760个逐小时观测数据，其中RAW目录下为原始数据，QC目录下为数据库质控表提取的数据**非本质控工具质控后**；
V0版本RAW、QC均为原始数据库提取结果；
V1版本RAW、QC为**质控需要**为V0版本RAW、QC中数据填补PM10、PM25后的质控输入数据集。

当前工具所需输入及依赖的环境、静态数据，已经整理上传至部门服务器/archive/share/Data/test/data_4_PmCompQC。构建项目工程同时可从以上目录中将同名目录中的内容copy到项目工程中。

**缺失数据由-999表示**


### 2. 算法简介

#### 2.1 质控需求

目前获取的2019年历史数据，进过分析发现存在的问题包括：数据缺失与数据异常。其中：
+ **数据缺失** 除中国环境检测总站，其他站点普遍存在的主要问题，各组分的缺失情况为 在线重金属 > PM颗粒物 > 水溶性离子 >= OCEC；
+ **数据异常** 包括：极高值，数据突变，数据无变化等；

#### 2.2 统计方法

+ 经验阈值
根据总站组分数据审核规范，提出水溶性离子、OCEC、重金属离子各项指标，包括：
    + 单组分经验阈值上下限
    + 单组分前后时次浮动变化经验
    + 多组分化学平衡、电荷平衡
    + 单组分、多组分与PM25相关性

+ 统计阈值
以上规范的指标均为确定数值，设计考虑不同区域、不同站点、不同历史条件下指标存在多样性，动态计算统计指定站点历史一段时间内以上相关指标的数据，综合经验阈值来对观测数据进行质控。

#### 2.3 机器学习方法

+ 异常识别
异常检测算法属于无监督学习的一种应用场景，其本质是基于数据密度、空间距离进行outlier detection，基于各站点各组分数据，训练识别单组分异常的模型用于质控判断，同时训练多个异常识别器，最后通过投票机制判断数据是否异常。

+ 数据填补
通过历史数据分析，发现几类组分与PM25相关性在0.7以上，通过训练与PM25的相关性模型，利用PM25的数据对目标组分进行数据填补；同理训练多个相关性回归模型，通过均值平滑不同模型在不同数据情况下的预测表现。


### 3. 运行环境

+ 部门服务器conda环境支持大部分模块需求，但是异常检测pyod与scikit-learn模块在版本上需要匹配，故建议手动配置项目运行环境内容。按照以下方式配置环境：

A. 从/archive/share/Data/test/data_4_PmCompQC/install目录获取Miniconda3-latest-Linux-x86_64.sh 

+ **Tips -> 不建议将此环境配置到自己环境变量，用到此环境输入绝对路径使用pip、conda、python即可**

B. 安装miniconda到指定目录，requirements.txt随仓可获取，执行
```
${miniconda_dirname}/miniconda/bin/conda install --yes --file requirements.txt
```

C. 检查相关模块是否安装成功 
```
${miniconda_dirname}/miniconda/bin/conda list
```


### 4. 部署

+ 配置以上环境后，克隆本仓库，无其他依赖框架
```
git clone ssh://git@47.92.132.84:2000/buzh/PmCompQC.git
```


### 5. 配置

+ 项目工程内部数据，可从 **/archive/share/Data/test/data_4_PmCompQC** 目录获取
+ 由于数据量较大，可以建立目录链接
    + /PmCompQC/data -> data_4_PmCompQC/data
    + /PmCompQC/models -> data_4_PmCompQC/models
    + /PmCompQC/input -> data_4_PmCompQC/input
+ 不同功能模块内部有独立配置文件，具体配置参考案例测试内容。

+ 获取工程配置好参考数据、输入数据、模型等内容后，项目结构如下：

```
[buzh@node1 PmCompQC]$ pwd
/public/home/buzh/PmCompQC
[buzh@node1 PmCompQC]$ ll
total 52
-rw-rw-r-- 1 buzh buzh  179 Jul  2 09:28 base_cfg.py
drwxrwxr-x 4 buzh buzh 4096 Jul  2 09:15 configs
lrwxrwxrwx 1 buzh buzh   45 Jul  2 09:26 data -> /archive/share/Data/test/data_4_PmCompQC/data
drwxrwxr-x 2 buzh buzh 4096 Jul  2 09:28 extract
drwxrwxr-x 3 buzh buzh 4096 Jul  2 09:28 fill_pm
lrwxrwxrwx 1 buzh buzh   46 Jul  2 09:26 input -> /archive/share/Data/test/data_4_PmCompQC/input
-rw-rw-r-- 1 buzh buzh 1077 Jul  2 09:15 LICENSE
lrwxrwxrwx 1 buzh buzh   47 Jul  2 09:25 models -> /archive/share/Data/test/data_4_PmCompQC/models
drwxrwxr-x 3 buzh buzh 4096 Jul  2 09:28 post_analysis
-rw-rw-r-- 1 buzh buzh 9162 Jul  2 09:24 README.md
-rw-rw-r-- 1 buzh buzh 1758 Jul  2 09:15 requirements.txt
drwxrwxr-x 6 buzh buzh 4096 Jul  2 09:28 src
drwxrwxr-x 2 buzh buzh 4096 Jul  2 09:28 visualization
```


### 6. 案例测试(不同模块功能介绍)

**Tips -> 运行不同模块会进入到该模块目录下，也可脚本输入绝对目录，调用miniconda的python执行相应脚本**


#### 6.1 base_cfg -- 公共配置文件

统一配置各模块公用的信息，主要修改项目路径。

#### 6.2 extract模块 -- 数据库提取、数据抽取模块

通过格式化拼接sql，从数据库提取每小时观测站点的所有组分数据；通过提取每小时站点数据拼接所有站点的一段时间的组分观测数据。

+ base_cfg.py - 为上层目录base_cfg.py软连接

+ cfg.py - 配置脚本
    + 大部分内容为静态配置
    + 修改提取时间段的起止时间
    + paths为相对目录，一般不需要修改 **也可按照喜好修改目录名称**

+ utils_workflow.py - 工具脚本
包括其他脚本需要的功能函数

+ main_db.py - 数据库提取主脚本
根据配置文件的数据库、站点、时间、路径信息，从数据库提取单小时观测数据，文件名称格式为：```obs_com_${yyyy}${mm}${dd}${HH}.txt```
执行过程
```
[buzh@node1 PmCompQC]$ cd extract/
[buzh@node1 extract]$ ll
total 20
lrwxrwxrwx 1 buzh buzh   14 Jul  2 09:57 base_cfg.py -> ../base_cfg.py
-rw-rw-r-- 1 buzh buzh 2749 Jul  2 09:57 cfg.py
-rw-rw-r-- 1 buzh buzh 6904 Jul  2 09:57 main_db.py
-rw-rw-r-- 1 buzh buzh 2047 Jul  2 09:57 main_extract.py
-rw-rw-r-- 1 buzh buzh 3136 Jul  2 09:57 utils.py
[buzh@node1 extract]$ /public/home/buzh/miniconda3/bin/python main_db.py
processing 2019-02-12 00 ...
processing 2019-02-12 01 ...
processing 2019-02-12 02 ...
processing 2019-02-12 03 ...
...
```

+ main_extract.py - 数据抽取
从单小时观测数据中提取单一站点起止时间内所有组分数据到独立文件，文件名称格式为 ```${站点编号}.txt```
执行
```
[buzh@node1 extract]$ ll
total 28
lrwxrwxrwx 1 buzh buzh   14 Jul  2 09:57 base_cfg.py -> ../base_cfg.py
-rw-rw-r-- 1 buzh buzh 2749 Jul  2 09:57 cfg.py
-rw-rw-r-- 1 buzh buzh 6904 Jul  2 09:57 main_db.py
-rw-rw-r-- 1 buzh buzh 2079 Jul  2 10:05 main_extract.py
drwxrwxr-x 2 buzh buzh 4096 Jul  2 10:00 obs_hourly_data
drwxrwxr-x 2 buzh buzh 4096 Jul  2 09:59 __pycache__
-rw-rw-r-- 1 buzh buzh 3136 Jul  2 09:57 utils.py
[buzh@node1 extract]$ /public/home/buzh/miniconda3/bin/python main_extract.py
handling station 1: 110000006
handling station 2: 371500001
handling station 3: 150100001
handling station 4: 1320100001
handling station 5: 410200001
...
```

#### 6.3 fill_pm模块 -- 填补PM10、PM25数据

目前数据库提取的组分观测数据中颗粒物PM数据大量缺失，设计匹配临近污染观测站点相同时间的PM10、PM25数据作为补充，其数据依赖于数据库提取的原始组分观测数据和匹配的临近污染观测站PM观测数据。

通过匹配生成input目录下2019年质控输入数据，以及data目录用于模型训练的数据集。

此功能目前是针对2019年全年数据量，咱不支持指定区间段的填补，**目前仅支持2019年全年数据的测试**。

+ base_cfg.py - 为上层目录base_cfg.py软连接

+ cfg.py - 本模块配置文件

+ fill_obs_pm.py - 提供小时分辨率文件 ```obs_comp_${yyyymmddHH}.txt``` 添加PM数据

+ fill_sta_pm.py - 提供单站点文件 ```${站点编号}.txt``` 添加PM数据

+ nearby.json - 组分观测站点与污染观测站点匹配文件 {k: v} = {组分观测站点编号: 污染观测站点编号}

+ nearby.txt - 匹配后的污染观测站点信息文件

#### 6.4 src 模块 -- 核心功能

包括数据质控、统计阈值计算写入配置文件、异常识别模型训练、数据填补模型训练等功能，其数据依赖于数据库提取、PM颗粒物填补后的各类数据。

+ base_cfg.py - 为上层目录base_cfg.py软连接

+ cfg.py - 本模块配置文件
    + 无监督异常识别模型配置
    + 回归补数模型配置
    + 计算统计指标统计上线分位数
    + 质控起止时间
    + 相关路径

+ calc_qc_index.py - 统计各站点历史数据各项指标并写入各站点的阈值文件，保存至 **configs** 目录

执行计算统计，则更新configs目录下各站点审核指标.ini文件中各类组分各项指标。

```
[buzh@node1 src]$ pwd
/public/home/buzh/PmCompQC/src
[buzh@node1 src]$ /public/home/buzh/miniconda3/bin/python calc_qc_index.py
***************************************************************************************************
1	Calc 371400002 ...
      PM10  PM25  F-  Cl-  NO3-  SO42-  Ca2+  ...  Ionic_ratio  SO42-NO3-_mol  NH4+_mol  SNA_balance  AE  CE  AECE_balance
4068  78.0  36.0 NaN  NaN   NaN    NaN   NaN  ...          0.0            NaN       NaN          NaN NaN NaN           NaN

[1 rows x 19 columns]
---------------------------------------------------------------------------------------------------
       PM10  PM25  OC  EC  OC/PM25  EC/PM25  OCEC/PM25  OC/EC
3430  107.0  18.0 NaN NaN      NaN      NaN        NaN    NaN
***************************************************************************************************
2	Calc 131100002 ...
...
```

+ qc_model_train.py - 训练无监督学习模型脚本，模型自动保存至 **models/qc_models** 目录

执行训练操作，读取配置中无监督学习配置内容，训练指定特征的无监督异常判别模型，并按照特征、模型名称保存。

**目前配置是直接link已训练好的模型，也可尝试删除链接，手动训练、更新无监督模型。**

```
[buzh@node1 src]$ pwd
/public/home/buzh/PmCompQC/src
[buzh@node1 src]$ /public/home/buzh/miniconda3/bin/python qc_model_train.py
```

+ fill_model_train.py - 训练回归补数模型脚本，模型自动保存至 **models/fill_models** 目录

执行训练操作，读取配置中监督回归学习配置内容，训练指定特征的回归补数机器学习模型，并按照特征、模型名称保存。

**目前配置是直接link已训练好的模型，也可尝试删除链接，手动训练、更新回归补数模型。**

```
[buzh@node1 src]$ pwd
/public/home/buzh/PmCompQC/src
[buzh@node1 src]$ /public/home/buzh/miniconda3/bin/python fill_model_train.py
```

+ main.py - 质控主脚本
    + 质控输入 input
    + 质控输出 output
    + 质控数据输出 output/qc_data
        + 质控剔除 qc_${yyyymmddHH}.txt
        + 质控填补 fill_${yyyymmddHH}.txt
    + 质控日志输出 output/qc_logs
        + 质控日志 qc_${yyyymmddHH}.json

output目录拉仓时没有创建，质控过程会自动创建，也可提取手动创建。质控过程打印大量中间结果，可以放后台处理.

**执行质控操作，系统自动针对配置时间段内数据进行质控操作，此时input为链接目录，为避免出现同时读取可复制input到项目所在目录；同时需注意由于质控过程考虑了前后时次数据，其时间起止设置与之前时间内会存在差别。**

```
[buzh@node1 src]$ pwd
/public/home/buzh/PmCompQC/src
[buzh@node1 src]$ /public/home/buzh/miniconda3/bin/python main.py>&qc.test.log&
```

+ utils - 工具

+ mylog - 日志记录

+ dao - data access object 数据读取

+ controllers - 质控控制类
    + 质控基类
    + 水溶性离子质控类
    + OCEC质控类
    + 重金属质控类


#### 6.5 post_analysis 模块 -- 提取原始、质控剔除、质控填补数据

分别提取质控站点在质控时间段内的观测原始、质控剔除、质控填补的数据，其输入数据依赖于质控过程的输入输出数据，形成三类数据用于绘图分析一段时间的质控效果。

+ base_cfg.py - 为上层目录base_cfg.py软连接

+ cfg.py - 本模块配置文件
    + 配置组分观测站点信息文件目录
    + 配置提取SRC项，如obs qc fill

+ main_extract.py - 数据提取脚本

**数据提取需分别配置，运行三次提取到质控站点质控期间obs qc fill三类数据集**

```
[buzh@node1 post_analysis]$ pwd
/public/home/buzh/PmCompQC/post_analysis
[buzh@node1 post_analysis]$ vim cfg.phy
[buzh@node1 post_analysis]$ /public/home/buzh/miniconda3/bin/python main_extract.py
handling station 1: 110000006
handling station 2: 371500001
handling station 3: 150100001
handling station 4: 1320100001
handling station 5: 410200001
handling station 6: 140100002
...
```

#### 6.6 visualization 模块 -- 可视化模块

质控可视化输入数据依赖于post_analysis模块提取质控时间段内的三类数据。

+ base_cfg.py - 为上层目录base_cfg.py软连接

+ utils.py - 工具

+ cfg.py - 本模块配置文件
    + 配置组分观测站点信息文件目录
    + 配置obs、qc、fill三类数据目录
    + 配置图片输出模块

+ sequence_plot.py - 绘制质控对比图

```
[buzh@node1 visualization]$ pwd
/public/home/buzh/PmCompQC/visualization
[buzh@node1 visualization]$ /public/home/buzh/miniconda3/bin/python  sequence_plot.py
2019-02-12 02:00:00 2019-02-13 21:00:00
Plot 1:	110000006
Plot 2:	371500001
Plot 3:	150100001
Plot 4:	1320100001
...
...
```


### 7. 输出

+ 质控输出目录结构：

```
[buzh@node1 output]$ pwd
/public/home/buzh/PmCompQC/output
[buzh@node1 output]$ tree -L 2
.
├── qc_data
    ├── fill_obs_2019021201.txt
    ├── fill_obs_2019021202.txt
    ├── fill_obs_2019021203.txt
    ...
    ├── qc_obs_2019021201.txt
    ├── qc_obs_2019021202.txt
    ├── qc_obs_2019021203.txt
    ...

└── qc_logs
    ├── qc_2019021201.json
    ├── qc_2019021202.json
    ├── qc_2019021203.json
    ...
```

+ 质控输出数据均为文本文件，可直接查看；质控日志为json文件，可直接查看也可以用文本编辑器查看。
