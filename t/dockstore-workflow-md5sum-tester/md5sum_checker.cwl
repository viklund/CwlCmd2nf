#!/usr/bin/env cwl-runner

class: CommandLineTool
id: Md5sumWorkflowChecker
label: A tool that checks the md5sum workflow
cwlVersion: v1.0

doc: |
  [![Docker Repository on Quay.io](https://quay.io/repository/briandoconnor/dockstore-tool-md5sum/status "Docker Repository on Quay.io")](https://quay.io/repository/briandoconnor/dockstore-tool-md5sum)
  [![Build Status](https://travis-ci.org/briandoconnor/dockstore-tool-md5sum.svg)](https://travis-ci.org/briandoconnor/dockstore-tool-md5sum)
  A very, very simple Docker container that checks the output of the https://github.com/briandoconnor/dockstore-workflow-md5sum workflow. This was used in the GA4GH/DREAM Infrastructure Challenge Phase 2.  See the [README](https://github.com/briandoconnor/dockstore-workflow-md5sum-tester/blob/master/README.md) for more information.


requirements:
- class: DockerRequirement
  dockerPull: quay.io/briandoconnor/dockstore-workflow-md5sum-tester:1.0.0
- class: InlineJavascriptRequirement

hints:
- class: ResourceRequirement
  # The command really requires very little resources.
  coresMin: 1
  ramMin: 1024
  outdirMin: 512000

inputs:
  input_file:
    type: File
    inputBinding:
      position: 1
      prefix: --input-file
    doc: The file that contains an md5sum.


outputs:
  results_file:
    type: File
    outputBinding:
      glob: results.json
    doc: A json file that contains the result of the test.

  log_file:
    type: File
    outputBinding:
      glob: log.txt
    doc: A text log file that contains more details.

baseCommand: [/bin/check_md5sum]
