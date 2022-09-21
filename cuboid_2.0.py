#2.0 9/11/2022
#介绍
print('3d v2.0')
print('1 确定了画面分辨率 标了界限')
print('2 可以平移摄像机(巨大飞跃)')
print('3 很多数值都可以方便的调了 比如视野角度')
print('4 代码相对更整洁了 吧')

#函数区
import math
def str_int(list):   #把列表里的元素都变为int
    index = 0
    for n in list:
        list[index] = int(n)
        index+=1
    return(list)

def trans(camera,f,P):   #精髓 坐标变换 这版更高级(难 XD)
    if camera[2]-P[2] == 0:
        Q = [int(frame/2+f*(camera[0]-P[0])-1),
    int(frame/2+f*(camera[1]-P[1])-1)]
    else:   #把空间直线和平面的交点转化为2个平面中2直线的交点问题
        Q = [int(frame/2+f*(camera[0]-P[0])/(camera[2]-P[2])-1),
    int(frame/2+f*(camera[1]-P[1])/(camera[2]-P[2])-1)]
    return(Q)

def lines(P,Q):   #基本就是上一个版的函数
    c_temp = {}
    if P[0] < Q[0]:   #还是和上次一样 这个条件和下一个其实只是步长不一样 函数解析式是一样的
        for x in range(P[0],Q[0]+1):
            l_temp = set()
            l_temp.add(int(round((P[1]-Q[1])/(P[0]-Q[0])*(x-P[0])+P[1],0)))
            c_temp[x] = l_temp
    elif P[0] > Q[0]:
        for x in range(P[0],Q[0]+1,-1):
            l_temp = set()
            l_temp.add(int(round((P[1]-Q[1])/(P[0]-Q[0])*(x-P[0])+P[1],0)))
            c_temp[x] = l_temp
    elif P[0] == Q[0]:
        if P[1] < Q[1]:
            c_temp[P[0]] = set(range(P[1],Q[1]))
        if P[1] > Q[1]:
            c_temp[P[0]] = set(range(P[1],Q[1],-1))
    return(c_temp)

def draw(coordinate,val=''):   #可以导入 但是没必要
    #不需要的功能 说不需要也需要 可以缩 但没要 反正能用 没这段还跑不起来 因为定义了变量
    #确保x连续 如果缺失了x值则自动填补
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

    #得到y从小到大的序列
    y_axis = []
    for coordinate_y in coordinate:
        y_axis.extend(coordinate[coordinate_y])
    del coordinate_y
    y_axis = list(set(y_axis))
    y_axis.sort(reverse=True)
    y_axis = tuple(y_axis)

    #绘图
    for y in range(y_axis[0],y_axis[len(y_axis)-1]-1,-1):   # y
        print('')
        print(y,'\t',end='')   #显示y轴坐标
        
        former_x = 0   # x
        for x in x_axis:
            if y in coordinate[x]:
                print('  '*(x-former_x),end='')
                print('██',end='')
                former_x = x+1
    del x,former_x

    #显示所有点的坐标(其实没啥用 在这里 但是 何必删呢)
    if val == 1:
        print('')
        for x in coordinate:
            for y in coordinate[x]:
                print('(%d,%d)' % (x+1,y),end=' ')

#啊啊啊啊啊
print('''
       y
      ↑    z
      │  ↗
      │ ╱
      │╱         x
――――――┼――――――→
     ╱│
    ╱ │
   ╱  │    ''')

camera = [0,0,0]
width = 60
scale = float(input('输入1 则 63x63\n'))   #边框缩放大小
frame = int(63*scale)
step = int(scale*1)
f = ((frame-2)/2)/math.tan(width/360*math.pi)   #摄像机到等效平面的距离

while True:
    coordinate = {}
    for temp in range(0,frame):
        coordinate[temp] = {frame-1,0}   #0-62
    del temp
    coordinate[0] = set(range(0,frame))
    coordinate[frame-1] = set(range(0,frame))

    #输入两点坐标
    #A = input()
    A = '-20 -20 52'
    if len(A.split()) != 3:
        print('3个数')
        exit()

    #G = input()
    G = '20 20 84'
    if len(G.split()) != 3:
        print('3个数')
        exit()
    if A == G:
        print('= x')
        exit()


    A,G = str_int(A.split()),str_int(G.split())
    #计算其余6个点坐标
    B,C,D = [G[0],A[1],A[2]],[G[0],G[1],A[2]],[A[0],G[1],A[2]]
    E,F,H = [A[0],A[1],G[2]],[G[0],A[1],G[2]],[A[0],G[1],G[2]]

    #计算对应的二维坐标
    A,B,C,D = trans(camera,f,A),trans(camera,f,B),trans(camera,f,C),trans(camera,f,D)
    E,F,G,H = trans(camera,f,E),trans(camera,f,F),trans(camera,f,G),trans(camera,f,H) 

    #计算连线线的所有的点
    ab,bc,cd,ad = lines(A,B),lines(B,C),lines(C,D),lines(A,D)
    ae,bf,cg,dh = lines(A,E),lines(B,F),lines(C,G),lines(D,H)
    ef,fg,gh,eh = lines(E,F),lines(F,G),lines(G,H),lines(E,H)
    all_lines = (ab,bc,cd,ad,ae,bf,cg,dh,ef,fg,gh,eh)

    #删掉画面外的点 根据 x 的值  !!!!!!这段没用 可以直接删!!!!!!
    for line in all_lines:
        key = list(line.keys())
        for x in key:
            if x > frame-1 or x < 1:
                del line[x]



    #把坐标丢进coordinate里
    for x in range(1,frame):
        for line in all_lines:
            if x in line.keys():
                coordinate[x].update(line[x])
    
    #把y超过范围的删掉
    coordinate_temp = coordinate
    for x in coordinate_temp:
        temp = set()
        for y in coordinate_temp[x]:
            if y > frame-1 or y < 0:
                temp.add(y)
        for y in temp:
            coordinate[x].remove(y)
    del coordinate_temp

    #画图
    draw(coordinate)
    print('')
    
    #移动摄像机
    camera_move = input()
    if len(camera_move) == 1:
        if camera_move == 'w':
            camera = [camera[0],camera[1],camera[2]+step]
        if camera_move == 'a':
            camera = [camera[0]-step,camera[1],camera[2]]
        if camera_move == 's':
            camera = [camera[0],camera[1],camera[2]-step]
        if camera_move == 'd':
            camera = [camera[0]+step,camera[1],camera[2]]
        if camera_move == 'u':
            camera = [camera[0],camera[1]+step,camera[2]]
        if camera_move == 'h':
            camera = [camera[0],camera[1]-step,camera[2]]
        if camera_move == 'c':
            camera = [0,0,0]
    print('\n'*frame*2)