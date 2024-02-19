from timeit import timeit
def tmit(stmt, setup="", number=10**6):
    print(timeit(stmt=stmt, setup=setup, number=number))
def infi_loop():
    while True:
        print(0)
        pass

# Data type performance
'''
# tuple
# List 
# dict
# class
# array.array & collections.deque

print("Slots",
# Creat New
timeit(
stmt = """
A = Coor2d(1, 2)
""",
setup = """
class Coor2d:
    __slots__ = ("x", "y")
    def __init__(self, x=0, y=0) -> None:
        self.x = x
        self.y = y
""",
number = 10**8),
# Access created instance
timeit(
stmt = """
A.x == A.y
A.x + A.y
A.x * A.y
""",
setup = """
class Coor2d:
    __slots__ = ("x", "y")
    def __init__(self, x=0, y=0) -> None:
        self.x = x
        self.y = y
A = Coor2d(1, 2)
""",
number = 10**8)
)

print("Without slots",
# Creat New
timeit(
stmt = """
B = Coornd(1, 2)
""",
setup = """
class Coornd:
    def __init__(self, x=0, y=0) -> None:
        self.x = x
        self.y = y
""",
number = 10**8),
# Access created instance
timeit(
stmt = """
B.x == B.y
B.x + B.y
B.x * B.y
""",
setup = """
class Coornd:
    def __init__(self, x=0, y=0) -> None:
        self.x = x
        self.y = y
B = Coornd(1, 2)
""",
number = 10**8)
)

print("List",
# Creat New
timeit(
stmt = """
C = [1.0, 2.0]
""",
setup = """
""",
number = 10**8),
# Access created instance
timeit(
stmt = """
C[0] == C[1]
C[0] + C[1]
C[0] * C[1]
""",
setup = """
C = [1.0, 2.0]
""",
number = 10**8)
)

print("Array",
# Creat New
timeit(
stmt = """
D = array("f", (1.0, 2.0))
""",
setup = """
from array import array
""",
number = 10**8),
# Access created instance
timeit(
stmt = """
D[0] == D[1]
D[0] + D[1]
D[0] * D[1]
""",
setup = """
from array import array
D = array("f", (1.0, 2.0))
""",
number = 10**8)
)

print("Deque",
# Creat New
timeit(
stmt = """
E = deque([1.0, 2.0], 2)
""",
setup = """
from collections import deque
""",
number = 10**8),
# Access created instance
timeit(
stmt = """
E[0] == E[1]
E[0] + E[1]
E[0] * E[1]
""",
setup = """
from collections import deque
E = deque([1.0, 2.0], 2)
""",
number = 10**8)
)

print("Dictionary",
# Creat New
timeit(
stmt = """
F = {0:1.0, 1:2.0}
""",
setup = """
""",
number = 10**8),
# Access created instance
timeit(
stmt = """
F[0] == F[1]
F[0] + F[1]
F[0] * F[1]
""",
setup = """
F = {0:1.0, 1:2.0}
""",
number = 10**8)
)

print("Tuple",
# Creat New
timeit(
stmt = """
G = (1.0, 2.0)
""",
setup = """
""",
number = 10**8),
# Access created instance
timeit(
stmt = """
D[0] == D[1]
D[0] + D[1]
D[0] * D[1]
""",
setup = """
D = (1.0, 2.0)
""",
number = 10**8)
)


# if A[1] == C[1]:
#     g = lambda y: A[1]
# else:
#     g = lambda y: int((A[0] - C[0]) / (A[1] - C[1]) * y + A[0] - A[1] * (A[0] - C[0]) / (A[1] - C[1]))


# if A[1] == C[1]:
#     g = lambda y: A[1]
# else:
#     t = (A[0] - C[0]) / (A[1] - C[1])
#     g = lambda y: int(t * y + A[0] - A[1] * t)

# exit()

faces = [[0, 1, 2, 3, 4] for _ in range(1000)]
facesMap = list(map(lambda face: face[0] + 10, faces))
for face in faces:
    face[0] += 10
print(facesMap == faces)
print(timeit(
"""
faces = list(map(lambda face: face[0] + 10, faces))
""",
"""
faces = [[0, 1, 2, 3, 4] for _ in range(1000)]
""",
number = 10**3) 
)
print(timeit(
"""
for face in faces:
    face[0] += 10
""",
"""
faces = [[0, 1, 2, 3, 4] for _ in range(1000)]
""",
number = 10**3)
)

l = [([0, 1, 2], 91, 81), ([3, 4, 5,], 92, 82), ([6, 7, 8], 93, 83), ([9, 10, 11], 94, 85)]
print(tuple(map(lambda item: item[0], l)))
print(tuple(zip(*tuple(zip(*l))[0])))
# exit()
# 1.2452824999927543
print(timeit(
"""
tuple(map(lambda item: item[0], l))
""",
"""
l = [([0, 1, 2], 91, 81), ([3, 4, 5,], 92, 82), ([6, 7, 8], 93, 83), ([9, 10, 11], 94, 85)]
""",
number=10**6
))

# 1.1478829000261612
print(timeit(
"""
tuple(zip(*l))[0]
""",
"""
l = [([0, 1, 2], 91, 81), ([3, 4, 5,], 92, 82), ([6, 7, 8], 93, 83), ([9, 10, 11], 94, 85)]
""",
number=10**6
))

# 2.3158868000027724
print(timeit(
"""
tuple(zip(*tuple(zip(*l))[0]))
""",
"""
l = [([0, 1, 2], 91, 81), ([3, 4, 5,], 92, 82), ([6, 7, 8], 93, 83), ([9, 10, 11], 94, 85)]
""",
number=10**6
))
import Readability.png as png
from copy import deepcopy
texture0 = png.Png("texture", "", from_pickle=False, to_pickle=False).pixels
print(png.Png("texture", "").pixels == deepcopy(texture0))

# 0.9501629999722354
print(timeit(
"""
texture = png.Png("texture", "", from_pickle=False, to_pickle=False).pixels
""",
"""
import Readability.png as png
texture0 = png.Png("texture", "", from_pickle=False, to_pickle=False).pixels
""",
number = 10
))

# 3.509561200044118
print(timeit(
"""
texture = deepcopy(texture0)
""",
"""
import Readability.png as png
from copy import deepcopy
texture0 = png.Png("texture", "", from_pickle=False, to_pickle=False).pixels
""",
number = 10
))


left = [1] * 10
right = [2] * 10

if left[8] < 0:
    x_start = 0
else:
    x_start = left[8]

if right[8] > 1:
    x_end = 1
else:
    x_end = right[8]
x_start
x_end

max(left[8], 0)
min(right[8], 1)

# 3.817218399999547
print(timeit(
"""
if left[8] < 0:
    x_start = 0
else:
    x_start = left[8]

if right[8] > 1:
    x_end = 1
else:
    x_end = right[8]
x_start
x_end
""",
"""
left = [1] * 10
right = [2] * 10
""",
number=10**8
))

# 9.962122400000226
print(timeit(
"""
max(left[8], 0)
min(right[8], 1)
""",
"""
left = [1] * 10
right = [2] * 10
""",
number=10**8
))


p1 = 0.618271828
p2 = 1 - p1
left = [0.271828] * 10
right = [0.618] * 10

1 / (p2 * left[2] + p1 * right[2])
1 / (p2 * left[2] + p1 * right[2])

dominator = 1 / (p2 * left[2] + p1 * right[2])
dominator
dominator

# 7.121450300001015
print(timeit(
"""
1 / (p2 * left[2] + p1 * right[2])
1 / (p2 * left[2] + p1 * right[2])
""",
"""
p1 = 0.618271828
p2 = 1 - p1
left = [0.271828] * 10
right = [0.618] * 10
""",
number=10**8))

# 4.194964299998901
print(timeit(
"""
dominator = 1 / (p2 * left[2] + p1 * right[2])
dominator
dominator
""",
"""
p1 = 0.618271828
p2 = 1 - p1
left = [0.271828] * 10
right = [0.618] * 10
""",
number=10**8))



mode = 4
hasnormal_map = True
hastexture = True
p1 = 0.618271828
p2 = 1 - p1
left = [0.271828] * 10
right = [0.618] * 10

if mode == 0 and (hastexture or hasnormal_map) or mode == 4 and hasnormal_map:
    p2 * left[2] + p1 * right[2]
p2 * left[2] + p1 * right[2]

# 0.04200260000015987
tmit(
"""
if mode == 0 and (hastexture or hasnormal_map) or mode == 4 and hasnormal_map:
    p2 * left[2] + p1 * right[2]
""",
"""
mode = 4
hasnormal_map = True
hastexture = True
p1 = 0.618271828
p2 = 1 - p1
left = [0.271828] * 10
right = [0.618] * 10
"""
)

# 0.029005400000187365
tmit(
"""
p2 * left[2] + p1 * right[2]
""",
"""
mode = 4
hasnormal_map = True
hastexture = True
p1 = 0.618271828
p2 = 1 - p1
left = [0.271828] * 10
right = [0.618] * 10
"""
)

mode = 0
if mode <= 1:
    pass
mode = 1
if mode <= 1:
    pass

mode = 0
if mode in (0, 1):
    pass
mode = 1
if mode in (0, 1):
    pass

# 0.021053699999811215
tmit(
"""
mode = 0
if mode <= 1:
    pass
mode = 1
if mode <= 1:
    pass
""",
)

# 0.02796470000021145
tmit(
"""
mode = 0
if mode in (0, 1):
    pass
mode = 1
if mode in (0, 1):
    pass
""",
)

# 0.018178800000896445
tmit(
"""
if a < 0 and b < 0 and c < 0:
    pass
""",
"""
a, b, c = -2, -3, -4
"""
)

# 0.058843099999648985
tmit(
"""
if max(a, b, c) < 0:
    pass
""",
"""
a, b, c = -2, -3, -4
"""
)


# 0.8136665000001813
tmit(
"""
if b:
    pass
""",
"""
b = False
"""
)

# 0.8479103999998188
tmit(
"""
if b:
    pass
""",
"""
b = 0
"""
)

# 0.7846098999998503
tmit(
"""
if b:
    pass
""",
"""
b = None
"""
)


from math import sqrt, pi
a = pi
b = sqrt(a)
print(sqrt(a)**3, b * b * b, a**1.5)

# 0.08469250000052853
tmit(
"""
sqrt(a)**3
""",
"""
from math import sqrt, pi
a = pi
"""
)

# 0.04258259999915026
tmit(
"""
b = sqrt(a)
b * b * b
""",
"""
from math import sqrt, pi
a = pi
"""
)

# 0.05368100000123377
tmit(
"""
a**1.5
""",
"""
from math import sqrt, pi
a = pi
"""
)


# 0.01405450003221631
tmit(
"""
A, B = B, A
""",
"""
from random import random, seed
seed(27182)
A = [random() for _ in range(20)]
B = [random() for _ in range(20)]
print(A)
print(B)
"""
)

# 0.02277799998410046
tmit(
"""
A_copy = A
A = B
B = A_copy
""",
"""
from random import random, seed
seed(27182)
A = [random() for _ in range(20)]
B = [random() for _ in range(20)]
print(A)
print(B)
"""
)



tmit(
"""
sum(A)
""",
"""
from random import random, seed
seed(27182)
A = [random() for _ in range(20)]
"""
)

tmit(
"""
sum(A[:])
""",
"""
from random import random, seed
seed(27182)
A = [random() for _ in range(20)]
"""
)



A, B, C, D = [(0,) * 9 + (i,) for i in range(4, 0, -1)]
print(A, B, C, D, "\n")
A, B, C, D = sorted((A, B, C, D), key=lambda l: l[9])
print(A, B, C, D)

A, B, C, D = [(0,) * 9 + (i,) for i in range(4, 0, -1)]
if A[9] > B[9]:
    A, B = B, A
if B[9] > C[9]:
    B, C = C, B
    if A[9] > B[9]:
        A, B = B, A
if C[9] > D[9]:
    C, D = D, C
    if B[9] > C[9]:
        B, C = C, B
        if A[9] > B[9]:
            A, B = B, A
print(A, B, C, D)

tmit(
"""
A, B, C, D = sorted((A, B, C, D), key=lambda l: l[9])
""",
"""
A, B, C, D = [(0,) * 9 + (i,) for i in range(4, 0, -1)]
"""
)


tmit(
"""
if A[9] > B[9]:
    A, B = B, A
if B[9] > C[9]:
    B, C = C, B
    if A[9] > B[9]:
        A, B = B, A
if C[9] > D[9]:
    C, D = D, C
    if B[9] > C[9]:
        B, C = C, B
        if A[9] > B[9]:
            A, B = B, A
""",
"""
A, B, C, D = [(0,) * 9 + (i,) for i in range(4, 0, -1)]
"""
)
s = set(range(10**6))
print(
    0 in s,
10**5 in s,
10**7 in s,
)

# 0.029898100066930056
tmit(
"""
0 in s
10**5 in s
10**7 in s
""",
"""
s = set(range(10**6))
"""
)

# inf
tmit(
"""
0 in s
10**5 in s
10**7 in s
""",
"""
s = list(range(10**6))
"""
)

# 0.07441400003153831
tmit(
"""
s.add(None)
s.add(8)
s.add(-16.67258)
s.add(())
""",
"""
s = set()
"""
)

# 0.14125549991149455
tmit(
"""
s |= {None}
s |= {8}
s |= {-16.67258}
s |= {()}
""",
"""
s = set()
"""
)

# 3.56883589993231
tmit(
"""
(a - b) ** 2
""",
"""
a = 512
b = 368
""",
number = 10 ** 8
)

# 3.3769518001936376
tmit(
"""
(a - b) * (a - b)
""",
"""
a = 512
b = 368
""",
number = 10 ** 8
)

# 3.3812057999894023
tmit(
"""
c = a - b
c * c
""",
"""
a = 512
b = 368
""",
number = 10 ** 8
)

# 3.2881512998137623
tmit(
"""
(c:=a-b) * c
""",
"""
a = 512
b = 368
""",
number = 10 ** 8
)
'''



