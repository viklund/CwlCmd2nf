#!/usr/bin/env python3

import argparse


def main():
    parser = argparse.ArgumentParser(description='Convert a CWL Command descriptor into a nextflow process')
    parser.add_argument('--file', required=True, help='CWL file')

    args = parser.parse_args()

if __name__ == '__main__':
    main()

