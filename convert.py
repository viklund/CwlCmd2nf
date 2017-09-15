#!/usr/bin/env python3

import argparse
import yaml
import os.path

class CWL(object):
    def __init__(self, yaml, name=None, prefix=None):
        self.yaml = yaml
        self.name = name
        self.prefix = prefix
        self.build()

    def full_name(self):
        if not self.name:
            raise NameError("No name for me")
        if not self.prefix:
            return self.name
        else:
            return "{}_{}".format(self.prefix, self.name)

class Container(CWL):
    def build(self):
        for req in self.yaml:
            if 'dockerPull' in req:
                self.container = req['dockerPull']

    def repr(self):
        return "container '{}'".format(self.container)

class Process(CWL):
    def build(self):
        if 'id' in self.yaml:
            self.id = self.yaml['id']
        else:
            self.id = '_'.join( os.path.basename(self.name).split('.') )

        self.build_inputs()
        self.build_outputs()
        self.build_command()
        self.build_container()

    def build_container(self):
        self.container = Container(self.yaml['requirements'])

    def build_inputs(self):
        self.inputs = []
        for n, v in self.yaml['inputs'].items():
            self.inputs.append( Input(v, name=n, prefix=self.id) )

    def build_outputs(self):
        self.outputs = []
        for n, v in self.yaml['outputs'].items():
            self.outputs.append( Output(v, name=n, prefix=self.id) )

    def build_command(self):
        self.command = Command(self.yaml['baseCommand'])

    def repr(self):
        repr = []
        for input in self.inputs:
            repr.append(input.setup_repr())
        repr.append("process {} {{".format(self.id))

        repr.append(self.container.repr())

        repr.append('input:')
        for input in self.inputs:
            repr.append( input.channel_repr() )

        repr.append('output:')
        for output in self.outputs:
            repr.append( output.channel_repr() )

        repr.append('script:')
        repr.append('"""')
        repr.append( self.command_repr() )
        repr.append('"""')
        repr.append('}')
        return "\n".join([r for r in repr if r])

    def command_repr(self):
        repr = self.command.repr()
        for argument in sorted(self.inputs, key=lambda x: x.position):
            repr += " " + argument.command_repr()
        return repr



class Input(CWL):
    def build(self):
        self.type = self.yaml['type']
        if 'default' in self.yaml:
            self.default = self.yaml['default']

        if 'inputBinding' in self.yaml:
            self.position = self.yaml['inputBinding']['position']
            self.arg_name = self.yaml['inputBinding'].get('prefix', '')
        else:
            self.position = 0

    def full_name(self):
        name = super().full_name()
        if self.type == 'File':
            name = "{}_{}".format('inp', name)
        else:
            name = "params.{}".format(name)
        return name

    def setup_repr(self):
        if self.type == 'File':
            return
        repr = self.full_name()
        if hasattr(self, 'default'):
            repr += " = {}".format(self.default)
        return repr

    def command_repr(self):
        arg_name = ''
        if self.arg_name:
            arg_name = self.arg_name + ' '
        if self.type == 'File':
            return "{}${{{}}}".format(arg_name, self.name)
        return "{}${{{}}}".format(arg_name, self.full_name())

    def channel_repr(self):
        if self.type != 'File':
            return
        return "file {} from {}".format(self.name, self.full_name())


class Output(CWL):
    def build(self):
        self.type = self.yaml['type']
        self.output = self.yaml['outputBinding']['glob']

    def full_name(self):
        name = super().full_name()
        if self.type == 'File':
            name = "{}_{}".format('out', name)
        return name

    def channel_repr(self):
        if self.type != 'File':
            return
        return "file '{}' into {}".format(self.output, self.full_name())

class Command(CWL):
    def build(self):
        self.command = self.yaml

    def repr(self):
        return " ".join(self.command)

class Converter(object):
    def convert(self, file):
        with open(file) as fh:
            contents = "".join(fh.readlines())
            data = yaml.load(contents)

        p = Process(data)
        print(p.repr())


def main():
    parser = argparse.ArgumentParser(description='Convert a CWL Command descriptor into a nextflow process')
    parser.add_argument('--file', required=True, help='CWL file')

    args = parser.parse_args()
    Converter().convert(args.file)

if __name__ == '__main__':
    main()

