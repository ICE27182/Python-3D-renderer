#2.1 9/19/2022
#介绍
print('3d v2.1')
print('1 修复了摄像头z大于长方体后仍能看到的bug(因为原来是直线和平面的交点)')
print('2 修复了摄像头在长方体里面看到图像错误(原因和上面差不多)')
print('3 会显示摄像机当前坐标了')
print('4 对于摄像机的操控更加方便了')
print('5 可以通过输入自定义视野 缩放 长方体坐标了 允许画线和面 点的话因为看不到就没允许')
print('6 让没用的变量及时下班')

#函数区
import math
def str_int(list):   #把列表里的元素都变为int
    index = 0
    for n in list:
        list[index] = int(n)
        index+=1
    del index,n
    return(list)

def trans(camera,f,P):   #精髓 坐标变换 这版更高级(难 XD)
    if camera[2]-P[2] >= 0:   #v2.1修的主要bug在这里 从=0变成≥0 至于为什么 自己品 懒得讲
        Q = [-int(frame/2+f*(camera[0]-P[0])-1),
    -int(frame/2+f*(camera[1]-P[1])-1)]   #Q的两个坐标加了负号 至于为什么 自己品 懒得讲

    else:   #把空间直线和平面的交点转化为2个平面中2直线的交点问题
        Q = [int(frame/2+f*(camera[0]-P[0])/(camera[2]-P[2])-1),
    int(frame/2+f*(camera[1]-P[1])/(camera[2]-P[2])-1)]
    return(Q)

def lines(P,Q):   #基本就是v1.0的函数
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

def draw(coordinate):   #可以导入 但是没必要 v2.1精简了一下
    x_axis = []
    for x in coordinate:
        x_axis.append(x)
    x_axis.sort()
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
    del x,former_x,y_axis

#输入
print('''
       y
      ↑    z
      │  ↗
      │ ╱
      │╱         x
――――――┼――――――→
     ╱│
    ╱ │
   ╱  │    
输入自定义的参数
自定义视野输入w按回车后输入(0,180)的实数   默认60度
自定义缩放输入s按回车后输入大于0的实数   默认1
自定义长方体坐标输入p后按回车输入一个点坐标 后按回车输入另一个点坐标
点坐标按照'x y z'输入 空格连接 如果不是整数则会去尾变为整数
默认A(-10 -20 40) G(20 10 90)
按回车确认''')

#默认数据
camera = [0,0,0]
width,scale = 60,1
A,G = [-20,-20,40],[20,10,90]

#自定义输入
option = input()
while True:
    if option == 'w':
        while True:
            width = input('输入视野大小 范围为(0,180)的实数 按回车则默认60')
            try:
                if width == '':
                    width = 60
                width = int(float(width))
                if width <=0 or width >= 180:
                    width = int('')
                break
            except:
                print('请检查输入内容')
        option = input()
    if option == 's':
        while True:
            scale = input('输入缩放大小 范围为大于0的实数 按回车则默认1(画面为61x61)')
            try:
                if scale == '':
                    scale = 1
                scale = float(scale)
                if scale <= 0:
                    scale = int('')
                break
            except:
                print('请检查输入内容')
        option = input()
    if option == 'p':
        while True:
            A = input()
            try:
                if len(A.split()) != 3:
                    A = int('')
                A = str_int(A.split())
                break
            except:
                print('请检查输入内容')
            
        while True:
            G = input()
            try:
                if len(G.split()) != 3:
                    G = int('')
                G = str_int(G.split())
                if G == A:
                    print('G和A不应重合')
                    G = int('')
                break
            except:
                print('请检查输入内容')
        option = input()
    if option == '':
        break
del option

#一些别的量
frame = int(63*scale)
step = int(scale*0.5)+1
f = ((frame-2)/2)/math.tan(width/360*math.pi)   #摄像机到等效平面的距离
#计算其余6个点坐标
B,C,D = [G[0],A[1],A[2]],[G[0],G[1],A[2]],[A[0],G[1],A[2]]
E,F,H = [A[0],A[1],G[2]],[G[0],A[1],G[2]],[A[0],G[1],G[2]]


while True:
    coordinate = {}
    for temp in range(0,frame):
        coordinate[temp] = {frame-1,0}   #0-62
    del temp
    coordinate[0] = set(range(0,frame))
    coordinate[frame-1] = set(range(0,frame))

    #计算对应的二维坐标
    A2,B2,C2,D2 = trans(camera,f,A),trans(camera,f,B),trans(camera,f,C),trans(camera,f,D)
    E2,F2,G2,H2 = trans(camera,f,E),trans(camera,f,F),trans(camera,f,G),trans(camera,f,H) 

    #计算连线线的所有的点
    ab,bc,cd,ad = lines(A2,B2),lines(B2,C2),lines(C2,D2),lines(A2,D2)
    ae,bf,cg,dh = lines(A2,E2),lines(B2,F2),lines(C2,G2),lines(D2,H2)
    ef,fg,gh,eh = lines(E2,F2),lines(F2,G2),lines(G2,H2),lines(E2,H2)
    all_lines = (ab,bc,cd,ad,ae,bf,cg,dh,ef,fg,gh,eh)
    del A2,B2,C2,D2,E2,F2,G2,H2
    #把坐标丢进coordinate里
    for x in range(1,frame):
        for line in all_lines:
            if x in line.keys():
                coordinate[x].update(line[x])
    del all_lines,ab,bc,cd,ad,ae,bf,cg,dh,ef,fg,gh,eh
    #把y超过范围的删掉
    coordinate_temp = coordinate
    for x in coordinate_temp:
        temp = set()
        for y in coordinate_temp[x]:
            if y > frame-1 or y < 0:
                temp.add(y)
        for y in temp:
            coordinate[x].remove(y)
    del coordinate_temp,x,y,temp

    #画图
    draw(coordinate)
    print('\n当前摄像机坐标为',camera)
    
    #移动摄像机
    print('直接输入WASD EF控制镜头按默认距离移动')
    print('输入W/A/S/D/E/F+数字 控制镜头按自定义距离移动')
    print('直接输入如1 2 3控制镜头到自定义坐标 空格连接')
    print('输入c使摄像头回到原点 输入q退出')
    camera_move = input()
    #按默认步长移动
    if camera_move == 'w':
        camera = [camera[0],camera[1],camera[2]+step]
    elif camera_move == 'a':
        camera = [camera[0]-step,camera[1],camera[2]]
    elif camera_move == 's':
        camera = [camera[0],camera[1],camera[2]-step]
    elif camera_move == 'd':
        camera = [camera[0]+step,camera[1],camera[2]]
    elif camera_move == 'e':
        camera = [camera[0],camera[1]+step,camera[2]]
    elif camera_move == 'f':
        camera = [camera[0],camera[1]-step,camera[2]]
    
    elif camera_move == 'c':   #回到原点
        camera = [0,0,0]
    elif camera_move == 'q':   #退出
        exit()
    elif camera_move == '':   #防止点快了没输入就按回车导致的bug
        print('\n'*frame*2)
        continue
    #按自定义步长移动摄像机
    elif camera_move[0] == 'w':
        try:
            camera = [camera[0],camera[1],camera[2]+int(camera_move[1:])]
        except:
            print('输入字母+整数表示移动的方向和距离')
    elif camera_move[0] == 'a':
        try:
            camera = [camera[0]-int(camera_move[1:]),camera[1],camera[2]]
        except:
            print('输入字母+整数表示移动的方向和距离')
    elif camera_move[0] == 's':
        try:
            camera = [camera[0],camera[1],camera[2]-int(camera_move[1:])]
        except:
            print('输入字母+整数表示移动的方向和距离')
    elif camera_move[0] == 'd':
        try:
            camera = [camera[0]+int(camera_move[1:]),camera[1],camera[2]]
        except:
            print('输入字母+整数表示移动的方向和距离')
    elif camera_move[0] == 'e':
        try:
            camera = [camera[0],camera[1]+int(camera_move[1:]),camera[2]]
        except:
            print('输入字母+整数表示移动的方向和距离')
    elif camera_move[0] == 'f':
        try:
            camera = [camera[0],camera[1]-int(camera_move[1:]),camera[2]]
        except:
            print('输入字母+整数表示移动的方向和距离')
    #按照坐标直接移动摄像机
    elif len(camera_move.split()) == 3:
        try:
            count = 0
            for temp in camera_move.split():
                camera[count] = int(temp)
                count+=1
            del temp,count
        except:
            print('按诸如 \'1 2 -3\' 输入整数')
    #换很多行 "隐藏"上一张画面
    print('\n'*frame*2)