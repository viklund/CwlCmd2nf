#!/usr/bin/env python3

import argparse
import yaml


class Converter:
    def convert(self, file):
        with open(file) as fh:
            contents = "".join(fh.readlines())
            data = yaml.load(contents)

        self.prefix = data['id']

        self.setup_params(data['inputs'])
        self.setup_input_channels(data['inputs'])

        self.setup_process(data)

    def setup_input_channels(self, inputs):
        for name, structure in inputs.items():
            if structure['type'] != 'File':
                continue
            name = self._create_name(name)
            ch_name = "inp_{}".format(name)
            structure['nxf_name'] = name
            structure['nxf_ch_name'] = ch_name

            print("Channel.from(file(params.{})).set {{ {} }}".format(name, ch_name))

    def setup_params(self, inputs):
        for name, structure in inputs.items():
            if structure['type'] == 'File':
                continue
            pname = "params.{}".format( self._create_name(name) )
            structure['nxf_name'] = pname
            if 'default' in structure:
                print("{} = {}".format(pname, structure['default']))
            else:
                print("{}".format(pname))

    def setup_process(self, data):
        print("process {} {{".format(data['id']))
        self.process_container(data)
        self.process_inputs(data)
        self.process_outputs(data)
        self.process_script(data)
        print("}")

    def process_outputs(self, data):
        print("    output:")
        for name, structure in data['outputs'].items():
            if structure['type'] != 'File':
                continue
            glob_pattern = structure['outputBinding']['glob']
            ch_name = "out_{}".format(self._create_name(name))
            print("        file('{}') into {}".format(glob_pattern, ch_name))


    def process_inputs(self, data):
        print("    input:")
        for inp, structure in data['inputs'].items():
            if structure['type'] != 'File':
                continue
            print("        file({}) from {}".format(structure['nxf_name'], structure['nxf_ch_name']))

    def process_script(self, data):
        print('    """')
        print('    {}'.format( self._build_command_line(data)))
        print('    """')
        return

    def _build_command_line(self, data):
        command = ' '.join(data['baseCommand'])

        sorted_inputs = sorted( data['inputs'].items(), key=lambda x: x[1]['inputBinding']['position'])
        for name, structure in sorted_inputs:
            command += ' ' + self._build_param(structure)
        return command

    def _build_param(self, structure):
        return '"${{{}}}"'.format(structure['nxf_name'])

    def process_container(self, data):
        for req in data['requirements']:
            if 'dockerPull' in req:
                print("    container '{}'".format( req['dockerPull'] ))
                return


    def _create_name(self, name):
        return "{}_{}".format(self.prefix, name)




def main():
    parser = argparse.ArgumentParser(description='Convert a CWL Command descriptor into a nextflow process')
    parser.add_argument('--file', required=True, help='CWL file')

    args = parser.parse_args()
    Converter().convert(args.file)

if __name__ == '__main__':
    main()

