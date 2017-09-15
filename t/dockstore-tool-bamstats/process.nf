params.mem_gb=4
params.bam_input='rna.SRR94877*.bam'
mem=params.mem_gb
bam=Channel.fromPath(params.bam_input)
bam.map { it -> [mem, it] }
.view()
.set {input_ch}

process dockstore_tool_bamstats {
    container 'quay.io/collaboratory/dockstore-tool-bamstats:1.25-6_1.0' 

    input:
    set val(mem_gb), file(bam_input) from input_ch

    output:
    file ('bamstats_report.zip') into bamstats_report

    script:
    """
    bash /usr/local/bin/bamstats ${mem_gb} ${bam_input}
    “””
}
