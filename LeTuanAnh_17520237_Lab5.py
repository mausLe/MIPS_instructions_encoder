# from constants import INSTRUCTIONS, REGISTERS, BLOCKS_FORMATS

"""
This code was implemented from the original repo of @MariuszBielecki288728.
Thanks for providing this helpful repo!
https://github.com/MariuszBielecki288728/MIPS_instructions_encoder
"""

import re
import sys, os

INSTRUCTIONS = [
    "add:reg,reg,reg:R:000000/%1/%2/%0/00000/100000",
    "addi:reg,reg,sint16:I:001000/%1/%0/%2",
    "lui:reg,sint16:I:001111/00000/%0/%1",
    "addiu:reg,reg,sint16:I:001001/%1/%0/%2",
    "slti:reg,reg,sint16:I:001010/%1/%0/%2",
    "sltiu:reg,reg,sint16:I:001011/%1/%0/%2",
    "andi:reg,reg,sint16:I:001100/%1/%0/%2",
    "ori:reg,reg,sint16:I:001101/%1/%0/%2",
    "xori:reg,reg,sint16:I:001110/%1/%0/%2",
    "sll:reg,reg,shamt:R:000000/00000/%1/%0/%2/000000",
    "srl:reg,reg,shamt:R:000000/00000/%1/%0/%2/000010",
    "sra:reg,reg,shamt:R:000000/00000/%1/%0/%2/000011",
    "sllv:reg,reg,reg:R:000000/%2/%1/%0/00000/000100",
    "srlv:reg,reg,reg:R:000000/%2/%1/%0/00000/000110",
    "srav:reg,reg,reg:R:000000/%2/%1/%0/00000/000111",
    "mfhi:reg:R:000000/00000/00000/%0/00000/010000",
    "mthi:reg:R:000000/%0/00000/00000/00000/010001",
    "mflo:reg:R:000000/00000/00000/%0/00000/010010",
    "mtlo:reg:R:000000/%0/00000/00000/00000/010011",
    "mult:reg,reg:R:000000/%0/%1/00000/00000/011000",
    "multu:reg,reg:R:000000/%0/%1/00000/00000/011001",
    "div:reg,reg:R:000000/%0/%1/00000/00000/011010",
    "divu:reg,reg:R:000000/%0/%1/00000/00000/011011",
    "addu:reg,reg,reg:R:000000/%1/%2/%0/00000/100001",
    "sub:reg,reg,reg:R:000000/%1/%2/%0/00000/100010",
    "subu:reg,reg,reg:R:000000/%1/%2/%0/00000/100011",
    "and:reg,reg,reg:R:000000/%1/%2/%0/00000/100100",
    "or:reg,reg,reg:R:000000/%1/%2/%0/00000/100101",
    "xor:reg,reg,reg:R:000000/%1/%2/%0/00000/100110",
    "nor:reg,reg,reg:R:000000/%1/%2/%0/00000/100111",
    "slt:reg,reg,reg:R:000000/%1/%2/%0/00000/101010",
    "sltu:reg,reg,reg:R:000000/%1/%2/%0/00000/101011"
]
BLOCKS_FORMATS = {
    'R': ['{0:06b}', '{0:05b}',
          '{0:05b}', '{0:05b}',
          '{0:05b}', '{0:06b}'],

    'I': ['{0:06b}', '{0:05b}',
          '{0:05b}', '{0:016b}'],

    'J': ['{0:06b}', '{0:026b}']
}
REGISTERS = {'$zero': 0, '$0': 0, '$at': 1, '$1': 1, '$v0': 2, '$2': 2, '$v1': 3, '$3': 3, '$a0': 4, '$4': 4, '$a1': 5, '$5': 5, '$a2': 6, '$6': 6, '$a3': 7, '$7': 7, '$t0': 8, '$8': 8, '$t1': 9, '$9': 9, '$t2': 10, '$10': 10, '$t3': 11, '$11': 11, '$t4': 12, '$12': 12, '$t5': 13, '$13': 13, '$t6': 14, '$14': 14, '$t7': 15, '$15': 15, '$s0': 16,
             '$16': 16, '$s1': 17, '$17': 17, '$s2': 18, '$18': 18, '$s3': 19, '$19': 19, '$s4': 20, '$20': 20, '$s5': 21, '$21': 21, '$s6': 22, '$22': 22, '$s7': 23, '$23': 23, '$t8': 24, '$24': 24, '$t9': 25, '$25': 25, '$k0': 26, '$26': 26, '$k1': 27, '$27': 27, '$gp': 28, '$28': 28, '$sp': 29, '$29': 29, '$fp': 30, '$30': 30, '$ra': 31, '$31': 31, }

class Instruction:

    def __init__(self, metadata):
        data = metadata.split(':')
        self.operands = data[1].split(',')
        self.instr_type = data[2]
        self.template = self.generate_bin_template(data[3])

    def generate_bin_template(self, meta_template):
        blocks = meta_template.split('/')
        lengths = BLOCKS_FORMATS[self.instr_type]
        return ''.join(('{' + block[1:] + form[2:]
                        if block[0] == '%'
                        else block)
                       for form, block in zip(lengths, blocks))

    def encode_to_int(self, arguments):
        u2_repr = map(lambda x: x if x >= 0 else x % (1 << 16), arguments)
        return int((self.template).format(*u2_repr), 2)


class Assembler:

    def __init__(self, prog_path, instr_set):
        self.instruction_dict = self.__generate_instructions_dict(instr_set)
        self.program = self.__get_prg_from_file(prog_path)

    def __generate_instructions_dict(self, instr_set):
        instr_dict = {}
        for instruction_meta in INSTRUCTIONS:
            splitted_instr = instruction_meta.split(":")
            instr_dict[splitted_instr[0]] = Instruction(instruction_meta)
        return instr_dict

    def __get_prg_from_file(self, file):
        with open(file, 'r') as f:
            lines = list(map(str.strip, map(str.casefold, f.readlines())))
            lines_with_instr = [line
                                for line in lines
                                if self.__is_instruction_canditate(line)]
            prog = list(enumerate(lines_with_instr))
        return prog

    def __is_instruction_canditate(self, instr):
        stripped = instr.strip()
        if stripped == '' or stripped[0] == '#':
            return False
        else:
            return True

    def assemble(self):
        for line, instr in self.program:
            splitted_instr = re.split('\s+|\s*,\s*', instr) # split multple dilimiter of every lines of the input file

            try:
                instruction_instance = self.instruction_dict[splitted_instr[0]]
            except KeyError:
                raise Exception("unrecognised instruction: " +
                                str(instr))

            def get_int_arg(arg):
                if arg[0] == '$':
                    try:
                        return REGISTERS[arg]
                    except KeyError:
                        raise Exception(
                            "Invalid register in instr:" + str(instr))
                else:
                    try:
                        return (int(arg, 16)
                                if arg[:2] == "0x" or arg[1:3] == "0x"
                                else int(arg))
                    except ValueError:
                        raise Exception(
                            "Invalid immediate value in instr: " + str(instr))

            num_of_args = len(instruction_instance.operands)
            args = splitted_instr[1:num_of_args + 1]
            if num_of_args != len(args):
                raise Exception("too few arguments in instr: " + str(instr))
            encoded_args = map(get_int_arg, args)
            encoded_instr = '{0:08X}'.format(
                instruction_instance.encode_to_int(encoded_args))
            encoded_instr_num = '{0:08X}'.format(4*line)
            print(encoded_instr)

            with open("output.txt", "a") as outf:
                outf.write(encoded_instr + "\n")

                outf.close()


if __name__ == '__main__':

    prog_path = "test.txt" # input path
    asm_instance = Assembler(prog_path, INSTRUCTIONS)
    asm_instance.assemble()
