#立方体

#8个顶点的坐标
A,B,C,D,E,F,G,H = [-7,-3,0],[7,-3,0],[7,3,0],[-7,3,0],[-7,-3,20],[7,-3,20],[7,3,20],[-7,3,20]

#缩放
temp = (A,B,C,D,E,F,G,H)
temp_size = float(input())
for temp_s in temp:
    for temp_co in temp_s:
        temp_s[temp_s.index(temp_co)] = temp_co*temp_size
del temp_s,temp,temp_co,temp_size

#3维坐标转为2维 透视用的是占视野的比例 视野120°
#摄像机(0, 0, 10x3½) 约等于(0, 0, -17.321)
def trans(spot):
    spot[0] = int( spot[0] * 30 / ((3**0.5)* spot[2] +30) )
    spot[1] = int( spot[1] * 30 / ((3**0.5)* spot[2] +30) )
    spot.pop()
    return(spot)

A,B,C,D,E,F,G,H = trans(A),trans(B),trans(C),trans(D),trans(E),trans(F),trans(G),trans(H)

#计算12条棱分别经过的点坐标 (点斜式表示的直线方程 外加斜率不存在讨论)
def lines(P,Q):
    c_temp = {}
    if P[0] < Q[0]:
        for x in range(P[0],Q[0]+1):
            l_temp = []
            l_temp.append(int(round((P[1]-Q[1])/(P[0]-Q[0])*(x-P[0])+P[1],0)))
            c_temp[x] = l_temp
    elif P[0] > Q[0]:
        for x in range(P[0],Q[0]+1,-1):
            l_temp = []
            l_temp.append(int(round((P[1]-Q[1])/(P[0]-Q[0])*(x-P[0])+P[1],0)))
            c_temp[x] = l_temp
    elif P[0] == Q[0]:
        if P[1] < Q[1]:
            c_temp[P[0]] = list(range(P[1],Q[1]))
        if P[1] > Q[1]:
            c_temp[P[0]] = list(range(P[1],Q[1],-1))
    return(c_temp)

ab,bc,cd,ad = lines(A,B),lines(B,C),lines(C,D),lines(A,D)
ae,bf,cg,dh = lines(A,E),lines(B,F),lines(C,G),lines(D,H)
ef,fg,gh,eh = lines(E,F),lines(F,G),lines(G,H),lines(E,H)
all_lines = (ab,bc,cd,ad,ae,bf,cg,dh,ef,fg,gh,eh)

#所有 x 的值
coordinate,x_all_lines = {},[]
for line in all_lines:
    for x in line:
        x_all_lines.append(x)
        coordinate[x] = []
x_all_lines = list(set(x_all_lines))
x_all_lines.sort
x_all_lines = tuple(x_all_lines)
del x,line

#合并12条棱的坐标 (感觉这可能才是难点? 虽然代码挺短)
for x in x_all_lines:
    for line in all_lines:
        temp = coordinate[x]
        if x in line.keys():
            temp.extend(line[x])
        coordinate[x] = temp
print(coordinate)

#画画 代码参考另一个程序 本来可以导入的 但是原来那个就不是为了当模块/函数用的
#所以...
#Ctrl+C Ctrl+V 稍微删点没用的东西
def draw(coordinate):
    x_axis = []
    for x in coordinate:
        x_axis.append(x)
    x_axis.sort()
    if len(x_axis) < len(range(x_axis[0],x_axis[-1]+1)):
        for x in range(x_axis[0],x_axis[-1]+1):
            try:
                coordinate[x] = coordinate[x]
            except:
                coordinate[x] = []
    x_axis = tuple(range(x_axis[0],x_axis[-1]+1))
    del x
    y_axis = []
    for coordinate_y in coordinate:
        y_axis.extend(coordinate[coordinate_y])
    del coordinate_y
    y_axis = list(set(y_axis))
    y_axis.sort(reverse=True)
    y_axis = tuple(y_axis)
    for y in range(y_axis[0],y_axis[len(y_axis)-1]-1,-1):
        print('')
        former_x = 0
        for x in x_axis:
            if y in coordinate[x]:
                print('  '*(x-former_x),end='')
                print('██',end='')
                former_x = x+1
    del x,former_x
    print('')
    for x in coordinate:
        for y in coordinate[x]:
            print('(%d,%d)' % (x+1,y),end=' ')

draw (coordinate)