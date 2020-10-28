import math
import struct


def k_fun(i):
    return [
        i,
        (5 * i + 1) % 16,
        (3 * i + 5) % 16,
        (7 * i) % 16
    ]


# round functions
def function_f(B, C, D):
    return (B & C) | (~B & D)


def function_g(B, C, D):
    return (B & D) | (C & ~D)


def function_h(B, C, D):
    return B ^ C ^ D


def function_i(B, C, D):
    return C ^ (B | ~D)


def tabl_t(i):
    return math.floor(abs(math.sin(i + 1)) * 2 ** 32)


def step_1_2(msg):
    # first step
    msg_in_bits = 8 * len(msg)

    msg_in_bytes = bytearray(msg, encoding='utf-8')

    # 128 = 1000 0000 bit
    msg_in_bytes.append(128)

    # 448 % 512
    while len(msg_in_bytes) % 64 != 56:
        msg_in_bytes.append(0)

    # second step
    msg_in_bytes += msg_in_bits.to_bytes(8, byteorder='little')

    return msg_in_bytes


def rotate_left(x, positions):
    return (x << positions) | (x >> (32 - positions)) % pow(2, 32)


# abcd k s i
# a = b + (( a + F(bcd) + x[k] + T[i])) << s

def step_3_4(input):
    # third step
    buffer = [0x67452301, 0xefcdab89, 0x98badcfe, 0x10325476]

    for piece in struct.iter_unpack("<16I", step_1_2(input)):
        (a, b, c, d) = buffer

        for i in range(64):
            k_numbers = k_fun(i)
            if i < 16:
                bits = function_f(b, c, d)
                k = k_numbers[0]
                # зсув раунд1
                zsuv = (7, 12, 17, 22)[i % 4]
            elif i < 32:
                bits = function_g(b, c, d)
                k = k_numbers[1]
                # зсув раунд2
                zsuv = (5, 9, 14, 20)[i % 4]
            elif i < 48:
                bits = function_h(b, c, d)
                k = k_numbers[2]
                # зсув раунд3
                zsuv = (4, 11, 16, 23)[i % 4]
            else:
                bits = function_i(b, c, d)
                k = k_numbers[3]
                # зсув раунд4
                zsuv = (6, 10, 15, 21)[i % 4]

            # a = b + (( a + F(bcd) + x[k] + T[i])) << s
            a = rotate_left((tabl_t(i) + a + bits + piece[k]) % pow(2, 32), zsuv) + b

            # a => d  b => a  c => b  d => c
            (a, b, c, d) = (d, a, b, c)
        buffer = [(first + second) % pow(2, 32) for (first, second) in zip(buffer, (a, b, c, d))]

    return buffer


def md5(msg):
    buffer = step_3_4(msg)
    # побайтовий вивід в hex
    final = ''
    for i in range(4):
        final += buffer[i].to_bytes(4, 'little').hex()
    return final


if __name__ == '__main__':

    while True:
        command = input('type "string" to encode string\n'
                        'type "file" to encode file\n'
                        'type "check file" to check file with stored hash\n'
                        'type "string file" to compare string with info in file \n')
        if command == 'file':
            filename = input('Name of file ')
            with open(filename, 'r', ) as f:
                file_obj = f.read()
                md5_obj = md5(file_obj)
            filename = input('Save hash to file ')

            with open(filename, 'w') as f:
                f.write(md5_obj)
                exit()

        elif command == 'string':
            inputing = input('Type any string you want ')
            md5_obj = md5(inputing)
            print('MD5 of string ' + inputing + ' is ' + md5_obj)

            filename = input('Save hash to file ')
            try:
                with open(filename, 'w') as f:
                    f.write(md5_obj)
                    f.close()
            except:
                print()
                continue
        elif command == 'check file':
            filename = input('Type file where hash is stored ')

            file = open(filename, 'r')
            hash_of_file = file.read()

            filename = input('Type file to check')
            file = open(filename, 'r', encoding='utf-8')
            file_obj = file.read()
            md5_obj = md5(file_obj)

            if md5_obj != hash_of_file:
                print('File are not same!')
                print(md5_obj + 'is not' + hash_of_file)
            else:
                print('File are same!')
                print(md5_obj + ' = ' + hash_of_file)
            exit()
        elif command == 'string file':
            filename = input('Type file where hash is stored ')

            file = open(filename, 'r')
            hash_of_file = file.read()

            inputing = input('Type any string you want ')
            md5_obj = md5(inputing)

            if md5_obj != hash_of_file:
                print('not same!')
                print(md5_obj + ' is not ' + hash_of_file)
            else:
                print('same!')
                print(md5_obj + ' = ' + hash_of_file)
            exit()
        else:
            print('Unknown command!')
            continue
        break
