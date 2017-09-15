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
        for req in self.yaml['requirements']:
            if 'dockerPull' in req:
                self.container = req['dockerPull']
                return
        for hint, req in self.yaml['hints'].items():
            if hint != 'DockerRequirement':
                continue
            if 'dockerPull' in req:
                self.container = req['dockerPull']
                return


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
        self.container = Container(self.yaml)

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
        repr = Representation()
        for input in self.inputs:
            if input.type == 'File':
                continue
            if input.required:
                if hasattr(input, 'default'):
                    repr.append(input.setup_repr())
                else:
                    repr.append("""
if (!{}) {{
    log.info("Missing parameter {}")
    exit 1
}}
""".format(input.param_name(), input.full_name()))
            else:
                repr.append(input.setup_repr())
        repr.append("process {} {{".format(self.id))
        repr.inc_indent()

        repr.append(self.container.repr())

        repr.append('input:')
        repr.inc_indent()
        for input in self.inputs:
            repr.append( input.channel_repr() )
        repr.dec_indent()

        repr.append('output:')
        repr.inc_indent()
        for output in self.outputs:
            repr.append( output.channel_repr() )
        repr.dec_indent()

        repr.append('script:')
        repr.inc_indent()
        repr.append( self.build_script_string() )

        repr.dec_indent()
        repr.dec_indent()
        repr.append('}')
        return repr.repr()

    def build_script_string(self):
        script = []

        command = self.command.repr()
        if command:
            script.append(command)
        for argument in sorted(self.inputs, key=lambda x: x.position):
            if not argument.required:
                script.append("( {} ? '{}' : '')".format(argument.param_name(), argument.command_repr()))
            else:
                script.append( " '{}'".format( argument.command_repr()) )
        return " + ".join(script)


class Representation(object):
    def __init__(self):
        self.indent = 0
        self._repr = []

    def append(self, str):
        if str:
            self._repr.append( "{}{}".format(' ' * self.indent, str))

    def inc_indent(self):
        self.indent += 4

    def dec_indent(self):
        self.indent -= 4
        if self.indent < 0:
            self.indent = 0

    def repr(self):
        return "\n".join([r for r in self._repr if r])



class Input(CWL):
    def build(self):
        self.required = True
        self.type = self.yaml['type']
        if self.type[-1] == '?':
            self.required = False
            self.type = self.type[:-1]

        if 'default' in self.yaml:
            self.default = self.yaml['default']
            self.required = True

        if 'inputBinding' in self.yaml:
            self.position = self.yaml['inputBinding']['position']
            self.arg_name = self.yaml['inputBinding'].get('prefix', '')
        else:
            self.position = 0

        if 'secondaryFiles' in self.yaml:
            self.secondary_files = self.yaml['secondaryFiles']

    def channel_name(self):
        return "{}_{}".format('inp', self.full_name())

    def param_name(self):
        return "param.{}".format(self.full_name())

    def setup_repr(self):
        if self.type == 'File':
            return
        repr = self.param_name()
        if hasattr(self, 'default'):
            if self.type == 'string':
                repr += " = '{}'".format(self.default)
            elif self.type == 'int':
                repr += " = {}".format(self.default)
        else:
            repr += " = ''"
        return repr

    def command_repr(self):
        arg_name = ''
        if self.arg_name:
            arg_name = self.arg_name + ' '
        if self.type == 'File':
            return "{}${{{}}}".format(arg_name, self.name)
        if self.type == 'boolean':
            return arg_name
        return "{}${{{}}}".format(arg_name, self.param_name())

    def channel_repr(self):
        if self.type != 'File':
            return
        if hasattr(self, 'secondary_files'):
            files = [self.name]
            for sf in self.secondary_files:
                if sf[0] == '.':
                    sf = '_' + sf[1:]
                files.append( self.name + sf )

            file_repr = ', '.join(["file({})".format(f) for f in files])

            return "set {} from {}".format(file_repr, self.channel_name())
        return "file {} from {}".format(self.name, self.channel_name())


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

        p = Process(data, name=file)
        print(p.repr())


def main():
    parser = argparse.ArgumentParser(description='Convert a CWL Command descriptor into a nextflow process')
    parser.add_argument('--file', required=True, help='CWL file')

    args = parser.parse_args()
    Converter().convert(args.file)

if __name__ == '__main__':
    main()

