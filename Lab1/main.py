print('How many number you would like to get?')
n = int(input('n= '))


def fun_rand(x_0):
    return (a * x_0 + c) % m


def period(x_0):
    test_arr = [x_0]
    for i in range(300):
        x = fun_rand(x_0)
        test_arr.append(str(x))
        x_0 = x
    return len(set(test_arr)) - 1


def listToString(s):
    str1 = " "
    return str1.join(s)


m = 2 ** 13 - 1
a = 5 ** 5
c = 3
x_init = 16
arr = [str(x_init)]
x_0 = x_init

for i in range(n - 1):
    x = fun_rand(x_0)
    arr.append(str(x))
    x_0 = x

print(arr)
my_set = set(arr)

print("Період = " + str(period(x_init)))
try:
    print("Число " + str(len(my_set) + 1) + ' = ' + arr[len(my_set)])
except:
    pass
f = open("text.txt", "w")
f.write(listToString(arr))
f.close()
input()
