import math
import os
import time

# MD5 алгоритм для шифрування парольної фрази з 2 лаби.
T = [int((2 ** 32) * abs(math.sin(i + 1))) for i in range(64)]
md5buffer = [0x67452301, 0xefcdab89, 0x98badcfe, 0x10325476]
cyclic_shift = [7, 12, 17, 22, 7, 12, 17, 22, 7, 12, 17, 22, 7, 12, 17, 22,
                5, 9, 14, 20, 5, 9, 14, 20, 5, 9, 14, 20, 5, 9, 14, 20,
                4, 11, 16, 23, 4, 11, 16, 23, 4, 11, 16, 23, 4, 11, 16, 23,
                6, 10, 15, 21, 6, 10, 15, 21, 6, 10, 15, 21, 6, 10, 15, 21]
elementary_functions = 16 * [lambda B, C, D: (B & C) | (~B & D)] + \
                       16 * [lambda B, C, D: (D & B) | (~D & C)] + \
                       16 * [lambda B, C, D: B ^ C ^ D] + \
                       16 * [lambda B, C, D: C ^ (B | ~D)]
сyclical_permutations = 16 * [lambda i: i] + \
                        16 * [lambda i: (5 * i + 1) % 16] + \
                        16 * [lambda i: (3 * i + 5) % 16] + \
                        16 * [lambda i: (7 * i) % 16]


def cyclic_shift_left(arg, num):
    arg &= 0xFFFFFFFF
    return ((arg << num) | (arg >> (32 - num))) & 0xFFFFFFFF


def md5(element, isString=False):
    if isString:
        with open("temp.txt", "w") as temp:
            temp.write(element)
        element = "temp.txt"
    lengthInBits = os.path.getsize(element) * 8
    lengthToAppend = lengthInBits & 0xffffffffffffffff
    fullAmount = lengthInBits // 512
    filetoWork = open(element, "rb")
    buffer = md5buffer[:]
    for k in range(fullAmount + 1):
        partialData = filetoWork.read(64)
        partialData = bytearray(partialData)
        if k == fullAmount:
            partialData.append(0x80)
            while len(partialData) % 64 != 56:
                partialData.append(0)
            partialData += lengthToAppend.to_bytes(8, byteorder='little')
        for every64byte in range(0, len(partialData), 64):
            A, B, C, D = buffer
            block512bit = partialData[every64byte:every64byte + 64]
            for i in range(64):
                current_function = elementary_functions[i](B, C, D)
                current_permutation = сyclical_permutations[i](i)
                before_shift = A + current_function + T[i] + int.from_bytes(
                    block512bit[4 * current_permutation:4 * current_permutation + 4], byteorder='little')
                B_new = (B + cyclic_shift_left(before_shift, cyclic_shift[i])) & 0xFFFFFFFF
                A, B, C, D = D, B_new, B, C
            for i, x in enumerate([A, B, C, D]):
                buffer[i] += x
                buffer[i] &= 0xFFFFFFFF
    variable = sum(x << (32 * i) for i, x in enumerate(buffer))
    another_variable = variable.to_bytes(16, byteorder='little')
    filetoWork.close()
    return '{:032x}'.format(int.from_bytes(another_variable, byteorder='big'))


# рс5

# Зсуви
# Циклічний зсув вліво.
def left_shift(value, amount, mod):
    mask = 2 ** mod - 1
    v1 = (value << amount % mod) & mask
    v2 = (value & mask) >> (mod - (amount % mod))
    return v1 | v2


# Циклічний зсув вправо.
def right_shift(value, amount, mod):
    mask = 2 ** mod - 1
    v1 = (value & mask) >> amount % mod
    v2 = value << (mod - (amount % mod)) & mask
    return v1 | v2


# Вектор ініціалізації
def vector_init(key, wordsize, rounds, IV=None):

    # Функція генерування масиву L.
    def make_L(key, value):
        L = []
        for i in range(0, len(key), value):
            L.append(int.from_bytes(key[i: i + value], byteorder="little"))
        return L

    # Функція генерування випадкових чисел з 1 лаби.
    def generate_random(amount):
        m = pow(2, 13) - 1
        a = pow(5, 5)
        c = 3
        x0 = int(round(time.time() * 1000)) % m
        result = []
        for i in range(amount):
            x0 = (a * x0 + c) % m
            result.append(x0)
        return result

    # Функція генерування масиву S.
    def make_S(rounds):
        # довжина вектора ініціалізації
        amount = 2 * (rounds + 1)
        return generate_random(amount)

    # Змішування ініціалізованого масиву S з масивом ключів L.
    def shuffle(L, S, rounds, w, c):
        T = 2 * (rounds + 1)
        m = max(c, T)
        i = j = A = B = 0
        for k in range(3 * m):
            A = S[i] = left_shift(S[i] + A + B, 3, w)
            B = L[j] = left_shift(L[j] + A + B, A + B, w)
            i = (i + 1) % T
            j = (j + 1) % c
        return S

    L = make_L(key, wordsize // 8)
    if IV == None:
        S = make_S(rounds)
        IV = S[:]
        # шифрування
        return IV, shuffle(L, S, rounds, wordsize, len(L))
    else:
        # дешифрування
        return shuffle(L, IV, rounds, wordsize, len(L))




# Клас шифрування/дешифрування файлу.
class RC5():
    def __init__(self, key, b, r):
        self.key = key
        self.blocksize = b
        self.rounds = r

    # Функція шифрування файлу по блоках.
    def encrypt_file(self, input_file, output_file):
        blocksize = self.blocksize
        rounds = self.rounds
        key = self.key
        w = blocksize // 2
        b = blocksize // 8
        IV, S = vector_init(key, w, rounds)
        cbc = 0
        with open(input_file, 'rb') as inp, open(output_file, 'wb') as out:
            for i in IV:
                temp = i.to_bytes(b, byteorder="little")
                out.write(self.encrypt_block(temp, [0] * (2 * (rounds + 1)), blocksize, rounds))
            isNext = True
            while isNext:
                block = inp.read(b)
                if not block:
                    break
                if len(block) != b:
                    block = block.ljust(b, b'\x00')
                    isNext = False
                block = int.from_bytes(block, byteorder='little')
                block = block ^ cbc
                block = block.to_bytes(b, byteorder='little')
                block = self.encrypt_block(block, S, blocksize, rounds)
                out.write(block)
                cbc = int.from_bytes(block, byteorder='little')

    # Функція дешифрування файлу по блоках.
    def decrypt_file(self, input_file, output_file):
        blocksize = self.blocksize
        rounds = self.rounds
        key = self.key
        w = blocksize // 2
        b = blocksize // 8
        cbc = 0
        with open(input_file, 'rb') as inp, open(output_file, 'wb') as out:
            IV = []
            for i in range(2 * (rounds + 1)):
                temp = inp.read(b)
                temp = self.decrypt_block(temp, [0] * (2 * (rounds + 1)), blocksize, rounds)
                IV.append(int.from_bytes(temp, byteorder="little"))
            S = vector_init(key, w, rounds, IV=IV)
            isNext = True
            while isNext:
                block = inp.read(b)
                temp = int.from_bytes(block, byteorder="little")
                if not block:
                    break
                if len(block) != b:
                    isNext = False
                decrypted = self.decrypt_block(block, S, blocksize, rounds)
                if not isNext:
                    decrypted = decrypted.rstrip(b'\x00')
                decrypted = int.from_bytes(decrypted, byteorder="little") ^ cbc
                decrypted = decrypted.to_bytes(b, byteorder="little")
                out.write(decrypted)
                cbc = temp

    def encrypt_block(self, block, S, blocksize, rounds):
        w = blocksize // 2
        b = blocksize // 8
        mod = 2 ** w
        A = int.from_bytes(block[:b // 2], byteorder='little')
        B = int.from_bytes(block[b // 2:], byteorder='little')
        A = (A + S[0]) % mod
        B = (B + S[1]) % mod
        for i in range(1, rounds + 1):
            A = (left_shift((A ^ B), B, w) + S[2 * i]) % mod
            B = (left_shift((A ^ B), A, w) + S[2 * i + 1]) % mod
        return A.to_bytes(b // 2, byteorder='little') + B.to_bytes(b // 2, byteorder='little')

    # Функція дешифрування одного блоку.
    def decrypt_block(self, block, S, blocksize, rounds):
        w = blocksize // 2
        b = blocksize // 8
        mod = 2 ** w
        A = int.from_bytes(block[:b // 2], byteorder='little')
        B = int.from_bytes(block[b // 2:], byteorder='little')
        for i in range(rounds, 0, -1):
            B = right_shift(B - S[2 * i + 1], A, w) ^ A
            A = right_shift(A - S[2 * i], B, w) ^ B
        B = (B - S[1]) % mod
        A = (A - S[0]) % mod
        return (A.to_bytes(b // 2, byteorder='little') + B.to_bytes(b // 2, byteorder='little'))

# отримання хешу з паролю
def get_key_by_password(password, b):
    key = md5(password, isString=True)

    if b == 8:
        key = key[0:16]
    elif b == 32:
        key = md5(key, isString=True) + key

    return bytes.fromhex(key)


print("Input w(length of word) R(rounds) b(length of key)")
vvesty = list(map(int, input().split()))

w = vvesty[0]
R = vvesty[1]
b = vvesty[2]

while (True):
    choose = input("To Encrypt file press 1 or Decrypt file press 2: ")
    if choose == 1:
        fR = input("File to encrypt: ")
        fW = input("Filename to write results into: ")
        password = input("Password: ")
        key = get_key_by_password(password, b)
        cod = RC5(key, w, R)
        cod.encrypt_file(fR, fW)
        print("Done")
    elif choose == 2:
        fR = input("File to decrypt: ")
        fW = input("Filename to write results into: ")
        password = input("Password: ")
        key = get_key_by_password(password, b)
        cod = RC5(key, w, R)
        cod.decrypt_file(fR, fW)
        print("Done")
    else:
        break
