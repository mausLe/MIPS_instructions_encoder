from string import Template


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
        return ''.join(('{'+ block[1:] + form[2:]
                            if block[0] == '%' 
                            else form.format(int(block)))
                                for form, block in zip(lengths, blocks))
    def encode_hex(self, arguments):
        return hex(int((self.template).format(*arguments),2))


"""def get_prg_from_file(file):
    with open(file, 'r') as f:
        prog = enumerate(map(str.strip, f.readlines))
    return prog"""

instr = Instruction('add:reg,reg,reg:R:0/%0/%1/%2/0/32')
print(instr.template)
instr = Instruction('add:reg,reg,reg:R:0/0/%1/%2/%0/32')
print(instr.template)
print(instr.encode_hex([1, 0, 0])) #TODO ujemne?