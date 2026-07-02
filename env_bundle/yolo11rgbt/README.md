# yolo11rgbt 环境包

## 文件说明
- environment.yml: 跨机器推荐（conda 求解）
- explicit.txt: 同平台精确复刻
- requirements-pip.txt: pip 冻结清单
- install.sh: 一键安装脚本

## 在另一台机器安装
1. 复制本目录到目标机器
2. 执行：
   bash install.sh

## 手动命令（推荐）
conda env create -n yolo11rgbt -f environment.yml

## 手动命令（同平台精确复刻）
conda create -n yolo11rgbt --file explicit.txt
