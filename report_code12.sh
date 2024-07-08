#!/bin/bash


#SBATCH -N 1   ##使用1个节点
#SBATCH -p sonmi   ##使用sonmi分区
#SBATCH -n 8   ##使用CPU核数为6
#SBATCH -o output  ##输出结果至output
#SBATCH --error=error
#SBATCH --exclude=sonmi,compute-0-3
#SBATCH -J report_code12  ##任务名为contig
#SBATCH --chdir=./

source ~/.bashrc

conda activate rnareport

export PATH=/share/apps/softwares/miniconda3/envs/R/bin/:$PATH
pip install yagmail
rm -r -f result/megahit_out
time snakemake -s report_code12.py -p -j 1 --cores 8 --rerun-incomplete --latency-wait 30 --keep-going --rerun-incomplete --unlock
time snakemake -s report_code12.py -p -j 1 --cores 8 --rerun-incomplete --latency-wait 30 --keep-going --rerun-incomplete  && rm -r ./bam/
python send_email.py
