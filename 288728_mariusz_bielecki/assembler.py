from constants import INSTRUCTIONS, REGISTERS, BLOCKS_FORMATS
import re
import sys


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
        # print(self.template, u2_repr)
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
        print('.text')
        for line, instr in self.program:
            splitted_instr = re.split('\s+|\s*,\s*', instr)
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
            print("  " +
                  encoded_instr_num+"  ",
                  encoded_instr+"  ",
                  instr
                  )


if __name__ == '__main__':
    prog_path = sys.argv[1]
    asm_instance = Assembler(prog_path, INSTRUCTIONS)
    asm_instance.assemble()
