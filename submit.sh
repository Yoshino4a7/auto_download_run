#!/bin/bash
#SBATCH -N 1   ##使用1个节点
#SBATCH -p sonmi   ##使用WHEEL分区
#SBATCH -n 1   ##使用CPU核数为32
#SBATCH -o output2  ##输出结果至output
#SBATCH --error=error2
##SBATCH --nodelist=compute-0-0  ##使用scau-1-123节点
#SBATCH -J litest  ##任务名为VASP
#SBATCH --exclude=sonmi ##不使用sonmi主节点

python file_check.py -spot {root_dir}
