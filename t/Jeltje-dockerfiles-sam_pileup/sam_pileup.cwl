#!/usr/bin/env cwl-runner
#
# Author: Jeltje van Baren jeltje.van.baren@gmail.com

cwlVersion: v1.0
class: CommandLineTool
baseCommand: []

doc: "samtools_pileup runs samtools on invididual chromosomes"

hints:
  DockerRequirement:
    dockerPull: quay.io/jeltje/samtools_pileup

requirements:
  - class: InlineJavascriptRequirement
  - class: ResourceRequirement
    coresMin: 8
    ramMin: 60000

inputs:
  bamfile:
    type: File
    doc: |
      Input bam file
    inputBinding:
      position: 2
      prefix: --input1
    secondaryFiles:
      - .bai

  out_pileup:
    type: string
    doc: |
      Output pileup file
    inputBinding:
      position: 2
      prefix: --output1

  genome:
    type: File
    doc: |
      Samtools indexed genome reference fasta file
    inputBinding:
      position: 2
      prefix: --genome
    secondaryFiles:
      - .fai

  outputdir:
    type: string?
    default: ./
    doc: |
      Output pileup directory (./)
    inputBinding:
      position: 2
      prefix: --outputdir

  lastCol:
    type: boolean?
    doc: |
      Print the mapping quality as the last column (False)
    inputBinding:
      position: 2
      prefix: --lastCol

  indels:
    type: boolean?
    doc: |
      Only output lines containing indels (False)
    inputBinding:
      position: 2
      prefix: --indels

  mapqMin:
    type: int?
    doc: |
      Filter reads by this min MAPQ 
    inputBinding:
      position: 2
      prefix: --mapqMin

  nobaq:
    type: boolean?
    doc: |
      disable BAQ computation (False)
    inputBinding:
      position: 2
      prefix: --nobaq

  consensus:
    type: boolean?
    doc: |
      Call the consensus sequence using MAQ consensus model (False). If set to True, also supply theta, hapNum, fraction and phredProb.
    inputBinding:
      position: 2
      prefix: --consensus

  theta:
    type: string?
    doc: |
      Theta parameter (error dependency coefficient)
    inputBinding:
      position: 2
      prefix: --theta

  hapNum:
    type: string?
    doc: |
      Number of haplotypes in sample
    inputBinding:
      position: 2
      prefix: --hapNum

  fraction:
    type: string?
    doc: |
      Expected fraction of differences between a pair of haplotypes
    inputBinding:
      position: 2
      prefix: --fraction

  phredProb:
    type: string?
    doc: |
      Phred probability of an indel in sequencing/prep
    inputBinding:
      position: 2
      prefix: --phredProb

  cpus:
    type: int?
    default: 8
    doc: |
      Number of CPUs to use (default 8)
    inputBinding:
      position: 2
      prefix: --cpus

  workdir:
    type: string?
    default: ./
    doc: |
      Working directory (default ./)
    inputBinding:
      position: 2
      prefix: --workdir


outputs:

  mpileup:
    type: File
    outputBinding:
      glob: $(inputs.out_pileup)

