#!/bin/bash
#SBATCH -N 1   ##使用1个节点
#SBATCH -p sonmi   ##使用WHEEL分区
#SBATCH -n 1   ##使用CPU核数为32
#SBATCH -o AUTO_output  ##输出结果至output
#SBATCH --error=AUTO_error
#SBATCH --nodelist=compute-0-4  ##使用scau-1-123节点
#SBATCH -J AUTO_RNA  ##任务名为VASP
#SBATCH --exclude=sonmi ##不使用sonmi主节点

python auto.py -d ../auto_all_RNA -ak - -s - -b - -ep - -data AUTO -v R
