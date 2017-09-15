params.BAMStats_mem_gb = 4
process BAMStats {
container 'quay.io/collaboratory/dockstore-tool-bamstats:1.25-6_1.0'
input:
file bam_input from inp_BAMStats_bam_input
output:
file 'bamstats_report.zip' into out_BAMStats_bamstats_report
script:
"""
bash /usr/local/bin/bamstats ${params.BAMStats_mem_gb} ${bam_input}
"""
}
