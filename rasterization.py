# Use the rasterize3!!!


def rasterize0(A, B, C):
    pos = (min(A[1], B[1], C[1]), max(A[1], B[1], C[1]) + 1, min(A[0], B[0], C[0]), max(A[0], B[0], C[0]) + 1)
    out = [[0] * (pos[3] - pos[2]) for _ in range(pos[1] - pos[0])]
    for y in range(pos[0], pos[1]):
        for x in range(pos[2], pos[3]):
            if (x, y) in (A, B, C):
                out[y - pos[0]][x - pos[2]] = 2
                continue
            AP = (x - A[0], y - A[1])
            BP = (x - B[0], y - B[1])
            CP = (x - C[0], y - C[1])
            APxBP = AP[0] * BP[1] - AP[1] * BP[0]
            BPxCP = BP[0] * CP[1] - BP[1] * CP[0]
            CPxAP = CP[0] * AP[1] - CP[1] * AP[0]
            if APxBP >= 0 and BPxCP >= 0 and CPxAP >= 0:
                out[y - pos[0]][x - pos[2]] = 1
            else:
                out[y - pos[0]][x - pos[2]] = 0
    return out

def rasterize1(A, B, C):
    pos = (min(A[1], B[1], C[1]), max(A[1], B[1], C[1]) + 1, min(A[0], B[0], C[0]), max(A[0], B[0], C[0]) + 1)
    out = [[0] * (pos[3] - pos[2]) for _ in range(pos[1] - pos[0])]
    def add_line(P, Q):
        # No need to change to if P[1] > Q[1]: ... elif P[1] < Q[1]: ... else: ...
        if P[1] != Q[1]:
            # No need to change to t = (P[0] - Q[0]) / (P[1] - Q[1])
            f = lambda y: (P[0] - Q[0]) / (P[1] - Q[1]) * y + P[0] - P[1] * (P[0] - Q[0]) / (P[1] - Q[1])
            for y in range(min(P[1], Q[1]), max(P[1], Q[1])):
                out[y - pos[0]][int(f(y) - pos[2])] = 1
        else:
            out[P[1] - pos[0]] = [1] * (pos[3] - pos[2])
    add_line(A, B)
    add_line(B, C)
    add_line(C, A)
    for row in out:
        if row.count(1) == 2:
            in_tri = False
            for x, p in enumerate(row):
                if p == 1:
                    in_tri = not in_tri
                if in_tri:
                    row[x] = 1
    return out

def rasterize2(A, B, C):
    pos = (min(A[1], B[1], C[1]), max(A[1], B[1], C[1]) + 1, min(A[0], B[0], C[0]), max(A[0], B[0], C[0]) + 1)
    out = [[0] * (pos[3] - pos[2]) for _ in range(pos[1] - pos[0])]
    for y in range(pos[0], pos[1]):
        for x in range(pos[2], pos[3]):
            if (x, y) in (A, B, C):
                out[y - pos[0]][x - pos[2]] = 2
                continue
            AP = (x - A[0], y - A[1])
            BP = (x - B[0], y - B[1])
            CP = (x - C[0], y - C[1])
            CPxAP = CP[0] * AP[1] - CP[1] * AP[0]
            if (AP[0] * BP[1] - AP[1] * BP[0]) * CPxAP >= 0 and (BP[0] * CP[1] - BP[1] * CP[0]) * CPxAP >= 0:
                out[y - pos[0]][x - pos[2]] = 1
            else:
                out[y - pos[0]][x - pos[2]] = 0
    return out

def rasterize3(A, B, C):
    pos = (min(A[1], B[1], C[1]), max(A[1], B[1], C[1]) + 1, min(A[0], B[0], C[0]), max(A[0], B[0], C[0]) + 1)
    out = [[0] * (pos[3] - pos[2]) for _ in range(pos[1] - pos[0])]
    if A[1] != B[1]:
        f = lambda y: (A[0] - B[0]) / (A[1] - B[1]) * y + A[0] - A[1] * (A[0] - B[0]) / (A[1] - B[1])
        for y in range(min(A[1], B[1]), max(A[1], B[1])):
            out[y - pos[0]][int(f(y) - pos[2])] = 1
    else:
        out[A[1] - pos[0]] = [1] * (pos[3] - pos[2])
    if B[1] != C[1]:
        f = lambda y: (B[0] - C[0]) / (B[1] - C[1]) * y + B[0] - B[1] * (B[0] - C[0]) / (B[1] - C[1])
        for y in range(min(B[1], C[1]), max(B[1], C[1])):
            out[y - pos[0]][int(f(y) - pos[2])] = 1
    else:
        out[B[1] - pos[0]] = [1] * (pos[3] - pos[2])
    if C[1] != A[1]:
        f = lambda y: (C[0] - A[0]) / (C[1] - A[1]) * y + C[0] - C[1] * (C[0] - A[0]) / (C[1] - A[1])
        for y in range(min(C[1], A[1]), max(C[1], A[1])):
            out[y - pos[0]][int(f(y) - pos[2])] = 1
    else:
        out[C[1] - pos[0]] = [1] * (pos[3] - pos[2])
    for row in out:
        if row.count(1) == 2:
            in_tri = False
            for x, p in enumerate(row):
                if p == 1:
                    in_tri = not in_tri
                if in_tri:
                    row[x] = 1
    return out

def rasterize4(A, B, C):
    if A[1] > B[1]:
        A, B = B, A
    if B[1] > C[1]:
        B, C = C, B
    if A[1] > B[1]:
        A, B = B, A
    minx = min(A[0], B[0], C[0])
    out = [[0] * (max(A[0], B[0], C[0]) - minx + 1) for _ in range(C[1] - A[1] + 1)]
    g = lambda y: int((A[0] - C[0]) / (A[1] - C[1]) * y + A[0] - A[1] * (A[0] - C[0]) / (A[1] - C[1]))
    if A[1] == B[1]:
        out[0] = [1] * (abs(A[0] - B[0]) + 1)
    else:
        f = lambda y: int((A[0] - B[0]) / (A[1] - B[1]) * y + A[0] - A[1] * (A[0] - B[0]) / (A[1] - B[1]))
        for y in range(A[1], B[1]):
            x1 = f(y) - minx
            x2 = g(y) - minx
            for x in range(min(x1, x2), max(x1, x2) + 1):
                out[y - A[1]][x] = 1
    if B[1] == C[1]:
        out[-1] = [1] * (abs(B[0] - C[0]) + 1)
    else:
        f = lambda y: int((B[0] - C[0]) / (B[1] - C[1]) * y + B[0] - B[1] * (B[0] - C[0]) / (B[1] - C[1]))
        for y in range(B[1], C[1]):
            x1 = f(y) - minx
            x2 = g(y) - minx
            for x in range(min(x1, x2), max(x1, x2) + 1):
                out[y - A[1]][x] = 1
    return out




def display(tri):
    palette = ("\033[31;1m██", "\033[36;1m██", "\033[32;1m██",)
    for row in tri:
        for p in row:
            print(palette[p], end="")
        print("\033[0m")

from timeit import timeit
from time import sleep

A = (15, 5)
B = (45, 20)
C = (30, 45)
# A = (0, 0)
# B = (45, 20)
# C = (0, 20)

display(rasterize4((15, 5), (45, 20), (30, 45)))
display(rasterize4((0, 0), (45, 20), (0, 20)))
display(rasterize4((8, 8), (128, 64), (64, 96)))
display(rasterize4((0, 20), (50, 20), (30, 0)))
display(rasterize4((16, 64), (0, 4), (8, 96)))



# exit()
print("3", timeit(
"""
rasterize3((15, 5), (45, 20), (30, 45))
rasterize3((0, 0), (45, 20), (0, 20))
rasterize3((8, 8), (128, 64), (64, 96))
rasterize3((0, 20), (50, 20), (30, 0))
rasterize3((16, 64), (0, 4), (8, 96))
""",
"""
def rasterize3(A, B, C):
    pos = (min(A[1], B[1], C[1]), max(A[1], B[1], C[1]) + 1, min(A[0], B[0], C[0]), max(A[0], B[0], C[0]) + 1)
    out = [[0] * (pos[3] - pos[2]) for _ in range(pos[1] - pos[0])]
    if A[1] != B[1]:
            f = lambda y: (A[0] - B[0]) / (A[1] - B[1]) * y + A[0] - A[1] * (A[0] - B[0]) / (A[1] - B[1])
            for y in range(min(A[1], B[1]), max(A[1], B[1])):
                out[y - pos[0]][int(f(y) - pos[2])] = 1
    else:
        out[A[1] - pos[0]] = [1] * (pos[3] - pos[2])
    if B[1] != C[1]:
            f = lambda y: (B[0] - C[0]) / (B[1] - C[1]) * y + B[0] - B[1] * (B[0] - C[0]) / (B[1] - C[1])
            for y in range(min(B[1], C[1]), max(B[1], C[1])):
                out[y - pos[0]][int(f(y) - pos[2])] = 1
    else:
        out[B[1] - pos[0]] = [1] * (pos[3] - pos[2])
    if C[1] != B[1]:
            f = lambda y: (C[0] - B[0]) / (C[1] - B[1]) * y + C[0] - C[1] * (C[0] - B[0]) / (C[1] - B[1])
            for y in range(min(C[1], B[1]), max(C[1], B[1])):
                out[y - pos[0]][int(f(y) - pos[2])] = 1
    else:
        out[C[1] - pos[0]] = [1] * (pos[3] - pos[2])
    for row in out:
        if row.count(1) == 2:
            in_tri = False
            for x, p in enumerate(row):
                if p == 1:
                    in_tri = not in_tri
                if in_tri:
                    row[x] = 1
    return out
""",
number=10**4
))
sleep(1)
print("4", timeit(
"""
rasterize4((15, 5), (45, 20), (30, 45))
rasterize4((0, 0), (45, 20), (0, 20))
rasterize4((8, 8), (128, 64), (64, 96))
rasterize4((0, 20), (50, 20), (30, 0))
rasterize4((16, 64), (0, 4), (8, 96))
""",
"""
def rasterize4(A, B, C):
    if A[1] > B[1]:
        A, B = B, A
    if B[1] > C[1]:
        B, C = C, B
    if A[1] > B[1]:
        A, B = B, A
    minx = min(A[0], B[0], C[0])
    out = [[0] * (max(A[0], B[0], C[0]) - minx + 1) for _ in range(C[1] - A[1] + 1)]
    g = lambda y: int((A[0] - C[0]) / (A[1] - C[1]) * y + A[0] - A[1] * (A[0] - C[0]) / (A[1] - C[1]))
    if A[1] == B[1]:
        out[0] = [1] * (abs(A[0] - B[0]) + 1)
    else:
        f = lambda y: int((A[0] - B[0]) / (A[1] - B[1]) * y + A[0] - A[1] * (A[0] - B[0]) / (A[1] - B[1]))
        for y in range(A[1], B[1]):
            x1 = f(y) - minx
            x2 = g(y) - minx
            for x in range(min(x1, x2), max(x1, x2) + 1):
                out[y - A[1]][x] = 1
    if B[1] == C[1]:
        out[-1] = [1] * (abs(B[0] - C[0]) + 1)
    else:
        f = lambda y: int((B[0] - C[0]) / (B[1] - C[1]) * y + B[0] - B[1] * (B[0] - C[0]) / (B[1] - C[1]))
        for y in range(B[1], C[1]):
            x1 = f(y) - minx
            x2 = g(y) - minx
            for x in range(min(x1, x2), max(x1, x2) + 1):
                out[y - A[1]][x] = 1
    return out
""",
number=10**4
))