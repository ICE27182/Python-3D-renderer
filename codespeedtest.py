from timeit import timeit

# print(
#     timeit("from shutil import get_terminal_size\nget_terminal_size()", number=10**6),
#     timeit("import shutil\nshutil.get_terminal_size()", number=10**6)
#     )
# print(
#     timeit("10**10",number=10**8),
#     timeit("10**10\n10**10",number=10**8)
# )
a = timeit("from os import system\nsystem('cls')", number=10**3)
print(0000)

b = timeit("import os\nos.system('cls')", number=10**3)
    
print(a,b)