from string import Template
from constants import INSTRUCTIONS, REGISTERS
import re
import sys


class Instruction:

    blocks_formats = {
        'R': ['{0:06b}', '{0:05b}',
              '{0:05b}', '{0:05b}',
              '{0:05b}', '{0:06b}'],

        'I': ['{0:06b}', '{0:05b}',
              '{0:05b}', '{0:016b}'],

        'J': ['{0:06b}', '{0:026b}']
    }

    def __init__(self, metadata):
        data = metadata.split(':')
        self.operands = data[1].split(',')
        self.instr_type = data[2]
        self.template = self.generate_bin_template(data[3])

    def generate_bin_template(self, meta_template):
        blocks = meta_template.split('/')
        lengths = Instruction.blocks_formats[self.instr_type]
        return ''.join(('{' + block[1:] + form[2:]
                        if block[0] == '%'
                        else block)
                       for form, block in zip(lengths, blocks))

    def encode_hex(self, arguments):
        u2_repr = map(lambda x: x if x >= 0 else x % (1 << 16), arguments)
        #print(self.template, u2_repr)
        return hex(int((self.template).format(*u2_repr), 2))


def get_prg_from_file(file):

    def is_instruction_canditate(instr):
        stripped = instr.strip()
        if stripped == '' or stripped[0] == '#':
            return False
        else:
            return True

    with open(file, 'r') as f:
        lines = list(map(str.strip, map(str.casefold, f.readlines())))
        lines_with_instr = [line
                            for line in lines
                            if is_instruction_canditate(line)]
        prog = list(enumerate(lines_with_instr))
    return prog


def assembler(prog, instructions_dict):
    print('.text')
    for line, instr in prog:
        splitted_instr = re.split('\s+|\s*,\s*', instr)
        try:
            instruction_instance = instr_dict[splitted_instr[0]]
        except KeyError:
            raise Exception("unrecognised instruction no." + str(line))
        num_of_args = len(instruction_instance.operands)
        args = splitted_instr[1:num_of_args + 1]
        #print(args)

        def encode_arg(arg):
            if arg[0] == '$':
                try:
                    return REGISTERS[arg]
                except KeyError:
                    raise Exception("Invalid register in instr no." + str(line))
            else:
                try:
                    return int(arg)
                except ValueError:
                    raise Exception("Invalid immediate value in instr no." + str(line))
        encoded_args = map(encode_arg, args)
        encoded_instr = '{0:08X}'.format(
            int(instruction_instance.encode_hex(encoded_args), 16))
        encoded_instr_num = '{0:08X}'.format(4*line)
        print("  "+
            encoded_instr_num+"  ",
            encoded_instr+"  ",
            instr
        )


if __name__ == '__main__':

    instr_dict = {}
    for instruction_meta in INSTRUCTIONS:
        splitted_instr = instruction_meta.split(":")
        instr_dict[splitted_instr[0]] = Instruction(instruction_meta)

    prog = get_prg_from_file(sys.argv[1])
    assembler(prog, instr_dict)
