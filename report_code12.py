##############################################################################################################################
#Created Time: 2023-08-09 实验室版权，严禁外传拷贝
#Author: Yankuo Sun 
#Scrrept Descrreption: RNA classification prepeline
#conda activate reportcoanf++++
#conda install samtools
#pip install metaphlan
#conda activate rnareport
#snakemake --use-conda -s report_code12.py -p -j 1 --core 200 --rerun-incomplete --latency-wait 5 --keep-going
##############################################################################################################################
#bwa index ASFV.fasta -p ASFV# When BWA calls a sequence, the sequence needs to have an index. 
import os
REP_INDEX = {"filename"}

#INDEX_Bow2host = "~/database1/genome/mouse/"  #小鼠
#INDEX_Bow2host = "~/database1/genome/Galgal4/" #鸡
#INDEX_Bow2host = "~/database1/genome/canfam4/"  #犬
#INDEX_Bow2host = "~/database1/genome/Felis_catus.Felis_catus_9.0/" #猫ddd
Kraken_standard = "/share/apps/kraken2_standard/"
blast_evrdnt = "/share/apps/database1/database1/evrd/evrd_nt/nt"
diamond_evrdnr = '/share/apps/database1/database1/evrd/evrd_aa/evrdnr'

rule all:
    input:
        expand("trimmomatic/{rep}.R1P_paired.fastq.gz",rep=REP_INDEX),
        expand("trimmomatic/{rep}.R1P_unpaired.fastq.gz",rep=REP_INDEX),
        expand("trimmomatic/{rep}.R2P_paired.fastq.gz",rep=REP_INDEX),
        expand("trimmomatic/{rep}.R2P_unpaired.fastq.gz",rep=REP_INDEX),
        expand("trimmomatic/{rep}_all_R1.fq.gz",rep=REP_INDEX),
        expand("trimmomatic/{rep}_all_R2.fq.gz",rep=REP_INDEX),
        expand("result/QC/{rep}_all_R1_fastqc.html",rep=REP_INDEX),
        expand("result/QC/{rep}_all_R1_fastqc.zip",rep=REP_INDEX),
        expand("result/QC/{rep}_all_R2_fastqc.html",rep=REP_INDEX),
        expand("result/QC/{rep}_all_R2_fastqc.zip",rep=REP_INDEX),
        expand("result/kraken2/{rep}.kreport",rep=REP_INDEX),
        expand("result/kraken2/{rep}.kraken",rep=REP_INDEX),
        expand("result/kraken2/{rep}.bracken",rep=REP_INDEX),
        expand("result/kraken2/{rep}.tsv",rep=REP_INDEX),
        expand("{rep}.html",rep=REP_INDEX),
        expand("result/kraken2/krona/{rep}.krona.html",rep=REP_INDEX),
        expand("result/megahit_out/{rep}.final.contigs.fasta",rep=REP_INDEX),
        expand("result/quast/{rep}_quast/report.html",rep=REP_INDEX),
        expand("result/classification/diamond/{rep}.diamond.csv",rep=REP_INDEX),
        expand("result/classification/processing/{rep}.virus.fasta",rep=REP_INDEX),
        expand("result/classification/uniquenr_{rep}.virus.csv",rep=REP_INDEX),
        expand("result/classification/{rep}_virus_diamond.txt",rep=REP_INDEX),
        expand("result/classification/uniqueblastn_{rep}.virus.csv",rep=REP_INDEX),
        expand("result/classification/zong/zong_{rep}.contigs.fa",rep=REP_INDEX),
        expand("result/classification/finaldiamond_{rep}.virus.fasta",rep=REP_INDEX),
        expand("result/classification/finalblastn_{rep}.virus.fasta",rep=REP_INDEX),
        expand("result/classification/zong/95zong_{rep}.contigs.fa",rep=REP_INDEX),
        expand("result/abandance/coverage/{rep}.cov.txt",rep=REP_INDEX),
        expand("result/abandance/rpkm/{rep}.rpkm.txt",rep=REP_INDEX),
        expand("result/abandance/histograms/{rep}.hist.txt",rep=REP_INDEX),

rule trimmomatic:
    input:
        "{rep}_1.fq.gz",
        "{rep}_2.fq.gz"
    output:
        "trimmomatic/{rep}.R1P_paired.fastq.gz",
        "trimmomatic/{rep}.R1P_unpaired.fastq.gz",
        "trimmomatic/{rep}.R2P_paired.fastq.gz",
        "trimmomatic/{rep}.R2P_unpaired.fastq.gz"
    log:
        "result/trimmomatic/{rep}.log"
    threads: 72
    shell:
       "trimmomatic PE -threads 60 {input[0]} {input[1]} {output[0]} {output[1]} {output[2]} {output[3]} \
        ILLUMINACLIP:/share/apps/Index/adapters/adapt.list.BGI.fa:2:30:10 \
        LEADING:2 TRAILING:2 \
        SLIDINGWINDOW:4:20 \
        MINLEN:50 2> {log} 2>&1"

rule cat:
    input:
        "trimmomatic/{rep}.R1P_paired.fastq.gz",
        "trimmomatic/{rep}.R1P_unpaired.fastq.gz",
        "trimmomatic/{rep}.R2P_paired.fastq.gz",
        "trimmomatic/{rep}.R2P_unpaired.fastq.gz",
    output:
        "trimmomatic/{rep}_all_R1.fq.gz",
        "trimmomatic/{rep}_all_R2.fq.gz",
    shell:
        """
        cat {input[0]} {input[1]} > {output[0]}
        cat {input[2]} {input[3]} > {output[1]}
        """

rule fastqc_analysis:
    input:
        "trimmomatic/{rep}_all_R1.fq.gz",
        "trimmomatic/{rep}_all_R2.fq.gz"
    params:
        output_path = "result/QC"
    output:
        "result/QC/{rep}_all_R1_fastqc.html",
        "result/QC/{rep}_all_R1_fastqc.zip",
        "result/QC/{rep}_all_R2_fastqc.html",
        "result/QC/{rep}_all_R2_fastqc.zip"
    shell:
        "fastqc {input[0]} {input[1]} -o {params.output_path}"

rule kraken2:  
    message:
        """
        =======================================================
        Running kraken2...
        kraken2 --db /mnt/d/kraken2_db/viral/ --threads 10 -gzip-compressed --use-names --paired 22R05962_1.fastq.gz 22R05962_2.fastq.gz --report kraken/1.kreport --output kraken/1.kraken --report-minimizer-data --confidence 0.5 --use-names
        =======================================================
        """
    input:
        "trimmomatic/{rep}.R1P_paired.fastq.gz",
        "trimmomatic/{rep}.R2P_paired.fastq.gz",
    output:
        "result/kraken2/{rep}.kreport",
        "result/kraken2/{rep}.kraken",
    threads: 72
    shell:
        """
        kraken2 --db {Kraken_standard} --threads {threads} -gzip-compressed \
        --paired {input[0]} {input[1]} --use-names --report {output[0]} --output {output[1]} --report-minimizer-data \
        --confidence 0.5 \
        --use-names
        """

rule bracken:  
    message:
        """
        =======================================================
        Running bracken...  t不是线程
        Usage: bracken -d MY_DB -i INPUT -o OUTPUT -w OUTREPORT -r READ_LEN -l LEVEL -t THRESHOLD
        MY_DB          location of Kraken database
        INPUT          Kraken REPORT file to use for abundance estimation
        OUTPUT         file name for Bracken default output
        OUTREPORT      New Kraken REPORT output file with Bracken read estimates
        READ_LEN       read length to get all classifications for (default: 100)
        LEVEL          level to estimate abundance at [options: D,P,C,O,F,G,S,S1,etc] (default: S)
        THRESHOLD      number of reads required PRIOR to abundance estimation to perform reestimation (default: 0)
        =======================================================
        """
    input:
        "result/kraken2/{rep}.kreport", 
    output:
        "result/kraken2/{rep}.bracken",
        "result/kraken2/{rep}.tsv",
    shell:
        "bracken -d {Kraken_standard} -i {input[0]} -o {output[0]} -w {output[1]}"

rule visual:  
    input:
        "result/kraken2/{rep}.tsv", 
    output:
        "{rep}.html",
    shell:
        "Rscript /share/home/rna/daima/yankuo1.R {input}"

rule kreport2krona:  
    message:
        """
        =======================================================
        kreport2krona.py 
        特别注意，这里输入的文件是seqs.hostfree.tsv，不是seqs.hostfree.mpa.tsv。
        python ~/biosoft/KrakenTools/kreport2krona.py
        usage: kreport2krona.py [-h] -r R_FILE -o O_FILE [--intermediate-ranks] [--no-intermediate-ranks]
        kreport2krona.py: error: the following arguments are required: -r/--report-file/--report, -o/--output
        $ python ~/biosoft/KrakenTools/kreport2krona.py -r seqs.hostfree.tsv -o seqs.hostfree.kro
        =======================================================
        """
    input:
        "result/kraken2/{rep}.kreport", 
    output:
        "result/kraken2/krona/{rep}.krona",
    shell:
        "python /share/apps/KrakenTools/kreport2krona.py -r {input} -o {output}"

rule html:
    message:
        """
        =======================================================
        ktImportText 
        #python ~/biosoft/Bracken/analysis_scripts/combine_bracken_outputs.py
        usage: combine_bracken_outputs.py [-h] --files FILES [FILES ...] [--names NAMES] -o OUTPUT
        combine_bracken_outputs.py: error: the following arguments are required: --files, -o/--output        
        combine_kreports.py: combines multiple Kraken reports into a single combined report file
        combine_kreports.py -r *.bracken -o bracken_phylum_all.report
        =======================================================
        """
    input:
        "result/kraken2/krona/{rep}.krona", 
    output:
        "result/kraken2/krona/{rep}.krona.html",
    shell:
        "ktImportText {input} -o {output}"

rule megahit:
    message:
        """
        =======================================================
        Running megahit...  megahit -t 40 -1 S1.clean.R1.fq.gz -2 S2.clean.R1.fq.gz -o out --k-min 35 --k-max 95 --k-step 20 --min-contig-len 500 -m 0.1 
        -k-min #设置最小的 kmer size，应小于 255，必须为奇数 --k-max #设置最大的 kmer size，应小于 255，必须为奇数  --k-step #间隔大小，应小于等于 28，必须为偶数
	=======================================================
        """
    input: 
        "trimmomatic/{rep}.R1P_paired.fastq.gz",
        "trimmomatic/{rep}.R2P_paired.fastq.gz",
        "trimmomatic/{rep}.R1P_unpaired.fastq.gz",
        "trimmomatic/{rep}.R2P_unpaired.fastq.gz",
    output:
        "result/megahit_out/{rep}/{rep}.final.contigs.fasta"  
    shell:
        """
        idvar=$(echo $(basename $(dirname {output})))
        mkdir -p $(dirname {output})/${{idvar}}
        cd $(dirname {output})/${{idvar}}
        cp ../../../../{input[0]} .
        cp ../../../../{input[1]} .
        cp ../../../../{input[2]} .
        cp ../../../../{input[3]} .
        megahit -1 $(basename {input[0]}) -2 $(basename {input[1]}) -r $(basename {input[2]}),$(basename {input[3]}) -o tmp --min-contig-len 500
        mv tmp/final.contigs.fa ../../../../{output}
        """

rule mv_rm:
    input:
        "result/megahit_out/{rep}/{rep}.final.contigs.fasta" 
    output:
        "result/megahit_out/{rep}.final.contigs.fasta"
    shell:
        """
        id=$(echo $(basename $(dirname {input})))
        mv {input} {output}
        rm -rf $(dirname {output})/${{id}}
        """

rule quast:
    input:
        "result/megahit_out/{rep}.final.contigs.fasta"
    params:
        output_path = "result/quast/{rep}_quast"
    output: 
        "result/quast/{rep}_quast/report.html"
    shell:
        "quast.py {input} -o {params.output_path}"

rule diamond:
    message:
        """
        =======================================================
        Running diamond...diamond help conda update diamond更新
        diamond makedb --in nr.fasta --db nr --taxonmap prot.accession2taxid --taxonnodes nodes.dmp
        diamond makedb --in nr.fasta --db nr --taxonmap prot. accession2taxid.gz --taxonnodes nodes.dmp
        diamond makedb --in ~/vfdb/VFDB_setB_pro.fas --db ~/vfdb/vfdb_pro$ diamond makedb --in ~/vfdb/VFDB_setB_nt.fas --db ~/vfdb/vfdb_nt
        ./ktImportBLAST /test_path/test.blast.out -o /test_path/test.blast.html
        =======================================================
        """
    input:
        "result/megahit_out/{rep}.final.contigs.fasta"
    output:
        "result/classification/diamond/{rep}.diamond.csv"
    params:
        o="6 qseqid sseqid pident qlen length evalue"
    threads: 72
    shell:
        "diamond blastx -p {threads} --db {diamond_evrdnr} -q {input} --query-cover 0.5 --outfmt {params.o} -e 1e-5 > {output}"


rule generate_virusunique_csv:
    input:
        "result/classification/diamond/{rep}.diamond.csv"
    output:
        "result/classification/processing/unique_{rep}.virus1.csv",
    shell:
        """
        awk -F'\t' '$3 >= 70 && $5 >= 200 && ($3 > max[$1] || max[$1] == "" || $6 < min[$1] || min[$1] == "") {{max[$1] = $3; min[$1] = $6; row[$1] = $0}} END {{for (i in row) print row[i]}}'  {input} > {output}
        """

rule contig_virus:
    message:
        """
        =======================================================
        提取病毒序列conda install seqkit
        =======================================================
        """
    input:
       "result/classification/processing/unique_{rep}.virus1.csv",
    output:
        "result/classification/processing/{rep}.txt"
    shell:
        "cut -f 1 {input} | uniq > {output}"

rule select_virus:
    message:
        """
        =======================================================
        提取病毒序列conda install seqkit
        =======================================================
        """
    input:
        "result/classification/processing/{rep}.txt",
        "result/megahit_out/{rep}.final.contigs.fasta",
    output:
        "result/classification/processing/{rep}.virus.fasta"
    shell:
        "python /share/apps/database1/bin/extract.py {input[0]} {input[1]} {output}"


rule replace_virussequence_names:
    input:
        "result/classification/processing/unique_{rep}.virus1.csv",
    output:
        "result/classification/uniquenr_{rep}.virus.csv",
    shell:
        "sed 's/\// /g' {input} > {output}"

rule process_virusfasta:
    input:
        fasta="result/classification/processing/{rep}.virus.fasta",
        unique_csv="result/classification/uniquenr_{rep}.virus.csv",
    output:
        "result/classification/finaldiamond_{rep}.virus.fasta",
    shell:
        "python /share/apps/database1/bin/syk_csv_fasta.py  {input.unique_csv} {input.fasta} {output}"

rule extractdiamond_virus:
    input:
        "result/classification/uniquenr_{rep}.virus.csv",
    output:
        "result/classification/{rep}_virus_diamond.txt"
    shell:
        "python /share/apps/database1/bin/evrd_list.py {input} {output}"

rule blastn:
    message:
        """
        =======================================================
        Running blastn...
        =======================================================
        """
    input:
        "result/megahit_out/{rep}.final.contigs.fasta"
    output:
        "result/classification/blastn/{rep}.blastn.csv"
    params:
        format="6 qseqid sseqid pident qlen length qcovs evalue bitscore"
    threads: 72
    shell:
        "blastn -db {blast_evrdnt} -num_threads {threads} -perc_identity 60 -max_hsps 5 -query {input} -max_target_seqs 5 -evalue 0.000001 -outfmt '{params.format}' > {output}" 


rule generate_blastnvirusunique_csv:
    input:
        "result/classification/blastn/{rep}.blastn.csv"
    output:
        "result/classification/blastn/unique_{rep}.virus1.csv",
    shell:
        """
        awk -F'\t' '$6 >= 80 && ($3 > max[$1] || max[$1] == "" || $7 < min[$1] || min[$1] == "") {{max[$1] = $3; min[$1] = $7; row[$1] = $0}} END {{for (i in row) print row[i]}}' {input} > {output}
        """


rule contig_virus_blastn:
    message:
        """
        =======================================================
        提取病毒序列conda install seqkit
        =======================================================
        """
    input:
        "result/classification/blastn/unique_{rep}.virus1.csv",
    output:
        "result/classification/blastn/{rep}.txt"
    shell:
        "cut -f 1 {input} | uniq > {output}"

rule select_virus_blastn:
    message:
        """
        =======================================================
        提取病毒序列conda install seqkit
        =======================================================
        """
    input:
        "result/classification/blastn/{rep}.txt",
        "result/megahit_out/{rep}.final.contigs.fasta",
    output:
        "result/classification/blastn/{rep}.virus_blastn.fasta"
    shell:
        "python /share/apps/database1/bin/extract.py {input[0]} {input[1]} {output}"


rule replace_blastvirussequence_names:
    input:
        "result/classification/blastn/unique_{rep}.virus1.csv",
    output:
        "result/classification/uniqueblastn_{rep}.virus.csv",
    shell:
        "sed 's/\// /g' {input} > {output}"

rule process_virusfastablastn:
    input:
        fasta="result/classification/blastn/{rep}.virus_blastn.fasta",
        unique_csv="result/classification/uniqueblastn_{rep}.virus.csv",
    output:   
        "result/classification/finalblastn_{rep}.virus.fasta"
    shell:
        "python /share/apps/database1/bin/syk_csv_fasta.py {input.unique_csv} {input.fasta} {output}"

rule cat_all:
    input:
        "result/classification/finaldiamond_{rep}.virus.fasta",
        "result/classification/finalblastn_{rep}.virus.fasta",
    output:
        "result/classification/zong/zong_{rep}.contigs.fa"
    shell:
        "cat {input[0]} {input[1]} | seqkit rmdup --by-seq --ignore-case > {output}"

rule cd_hit:
    input:
        "result/classification/zong/zong_{rep}.contigs.fa"
    output:
        "result/classification/zong/95zong_{rep}.contigs.fa",
        "result/classification/zong/95zong_{rep}.contigs.fa.clstr",
    threads: 72
    shell:
        "cd-hit -i {input} -o {output[0]} -c 0.95 -T {threads} -M 111111111"

rule bowtie_index:
    input:
        "result/classification/zong/95zong_{rep}.contigs.fa"
    output:
        "result/classification/zong/95zong_{rep}.contigs.1.bt2",
        "result/classification/zong/95zong_{rep}.contigs.2.bt2",
        "result/classification/zong/95zong_{rep}.contigs.3.bt2",
        "result/classification/zong/95zong_{rep}.contigs.4.bt2",
        "result/classification/zong/95zong_{rep}.contigs.rev.1.bt2",
        "result/classification/zong/95zong_{rep}.contigs.rev.2.bt2"
    params:
        index="result/classification/zong/95zong_{rep}.contigs"
    shell:
        "bowtie2-build {input} {params.index}"

rule bowtie:
    message:
        """
        =======================================================
        bowtie2-build --threads 64 contigs.fasta contig
        =======================================================
        """
    input:
        "trimmomatic/{rep}.R1P_paired.fastq.gz",
        "trimmomatic/{rep}.R1P_unpaired.fastq.gz",
        "trimmomatic/{rep}.R2P_paired.fastq.gz",
        "trimmomatic/{rep}.R2P_unpaired.fastq.gz",
        "result/classification/zong/95zong_{rep}.contigs.1.bt2",
        "result/classification/zong/95zong_{rep}.contigs.2.bt2",
        "result/classification/zong/95zong_{rep}.contigs.3.bt2",
        "result/classification/zong/95zong_{rep}.contigs.4.bt2",
        "result/classification/zong/95zong_{rep}.contigs.rev.1.bt2",
        "result/classification/zong/95zong_{rep}.contigs.rev.2.bt2",
    output: 
        "bam/{rep}_contigs.sam"
    params:
        index="result/classification/zong/95zong_{rep}.contigs"
    threads: 72
    shell:
        "bowtie2 -p {threads} -x {params.index} -1 {input[0]} -2 {input[2]} -U {input[1]} -U {input[3]} -S {output} --fast"

rule pileup:
    message:
        """
        =======================================================
        install -y bbmap
        bowtie2-build --threads 64 contigs.fasta contig
        =======================================================
        """
    input:
        "result/classification/zong/95zong_{rep}.contigs.fa",
        "bam/{rep}_contigs.sam",
    output:
        cov = "result/abandance/coverage/{rep}.cov.txt",
        rpkm = "result/abandance/rpkm/{rep}.rpkm.txt",
        hist = "result/abandance/histograms/{rep}.hist.txt",
    shell:
        "pileup.sh in={input[1]} ref={input[0]} out={output.cov} rpkm={output.rpkm} hist={output.hist}"

