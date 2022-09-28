#3d图像渲染 v3.0 9/23/2022-9/28/2022

#函数区
import math
def repeating_words():   #输入部分 一段出现了3词的 这样大概可以短一点
    print('\n输入w更改画面宽度   输入h更改画面高度   输入f更改视野   输入q退出',end='   ')
    print('输入p更改体对角线上两点坐标',end='   ')
    print('输入huge 宽高自动设为 938x311')
    print('输入回车以继续')

#下面这仨函数纯粹是因为我懒 不过也可以让下面短一点吧
def sin(theta):    return math.sin(theta*math.pi/180)
def cos(theta):    return math.cos(theta*math.pi/180)
def integer(val):    return int(round(val,0))

def trans(P):   #直线PC与平面的交点Q 并转换为2维坐标
    '''用于把一个三维坐标的转换为二维坐标
    通过
    1 计算 摄像机camera 和 转换对象P 的连线 与距离摄像机距离为f 法向量为(cosα·cosβ,sinβ,sinα·cosβ)的平面p的交点Q1
    2 将平面p平移至过原点O得到平面p' 保持Q1与平面p恒过的点F相对位置不变 得到Q2
    3 通过两个方向向量a b 得到Q2在方向向量a b上的数量投影 即平面p'旋转为法向量为(0,0,1)的过原点O的平面p''下
        Q2转换为Q3的横纵坐标值
    4 将得到的Q3平移 使之适配draw()'''
    #求交点
    cP = (P[0]-camera[0],P[1]-camera[1],P[2]-camera[2])   #直线方向向量 含大小
    n = [round(cos(alpha)*cos(beta),8), round(sin(beta),8), round(sin(alpha)*cos(beta),8)]   #平面法向量
    ncPD = cP[0]*n[0]+cP[1]*n[1]+cP[2]*n[2]   #向量内积

    if ncPD == 0:   #无交点 直线平行于平面
        Q1 = (P[0]+n[0]*f, P[1]+n[1]*f, P[2]+n[2]*f)

    elif ncPD > 0 or ncPD < 0:   #有焦点
        #手动解方程解出来的 不知道几何意义上分母为什么会和向量内积有关
        Q1 = (f*cP[0]/ncPD+camera[0], f*cP[1]/ncPD+camera[1], f*cP[2]/ncPD+camera[2])
    
    #转化为2维坐标
    F = (camera[0]+n[0]*f, camera[1]+n[1]*f, camera[2]+n[2]*f)   #平面必过F点
    Q2 = [Q1[0]-F[0],Q1[1]-F[1],Q1[2]-F[2]]   #平移平面到过原点

    #a b向量是平面上的两个方向单位向量 a b垂直 通过数量投影把三维坐标化为二维坐标
    #a原式: cos(α+90°)·cosβ, 0, sin(α+90°)·cosβ
    a = (sin(alpha)*cos(beta), 0, -cos(alpha)*cos(beta))   #注意 a[1] == 1
    a_len = (a[0]**2+a[2]**2)**0.5   #向量a的长度不恒为1 所以算一下
    #b原式: cosα·cos(β-90°), sin(β-90°), sinα·cos(β-90°)   不知道为什么是减而不是加90
    b = (-cos(alpha)*sin(beta), cos(beta), -sin(alpha)*sin(beta))   #b长度恒为1 就不单独写了

    if beta != 90 and beta != -90:   #分母不等于0
        Q3 = ((a[0]*Q2[0]+a[1]*Q2[1]+a[2]*Q2[2])/a_len, b[0]*Q2[0]+b[1]*Q2[1]+b[2]*Q2[2])   #数量投影
        if ncPD <= 0:   return ()   #在视野后方直接abandon            
    elif beta == 90:   Q3 = (Q2[0],-Q2[2])      
    elif beta == -90:   Q3 = (Q2[0],Q2[2])
    
    Q4 = (integer(Q3[0]+width/2),integer(Q3[1]+height/2))
    return Q4

def lines(P,Q):   #重写了 缩短+连线
    '''用于计算平面上两点P Q定义的线段PQ经过的所有坐标
    先分类讨论斜率k是否存在
    若存在 以1为步长迭代x 计算出x和y
        因为1为步长 所以 k>1 或 k<-1 时可能出现一个x对应2个y 从而导致仅按上述方法线条会断断续续
        所以当 k>1 或 k<-1时把它手动连上
    若不存在 就直接range()'''
    line = {}
    if P == () or Q == ():   #在视野后方直接abandon 这个防止报错
        return {}
    #按照斜率存在与否分类讨论
    elif P[0] != Q[0]:   #斜率存在
        for x in range(min(P[0],Q[0]),max(P[0],Q[0])+1):   #遍历x值 会max()和min()就能缩短了
            y = set()
            y.add(int(round((P[1]-Q[1])/(P[0]-Q[0])*(x-P[0])+P[1],0)))
            line[x] = y
        #上面的算法x步长为1 对于斜率 k>1 的情况可能线会断断续续 通过这个连上
        if (P[1]-Q[1])/(P[0]-Q[0]) > 1:   #k > 1
            for x in range(min(P[0],Q[0]),max(P[0],Q[0])):
                line[x] = line[x] | set(range(max(line[x]),min(line[x+1])))
        elif (P[1]-Q[1])/(P[0]-Q[0]) < -1:   #k < 1
            for x in range(min(P[0],Q[0]),max(P[0],Q[0])):
                line[x] = line[x] | set(range(max(line[x+1]),min(line[x])))        
    elif P[0] == Q[0]:   #斜率不存在
            line[P[0]] = set(range(min(P[1],Q[1]),max(P[1],Q[1])+1))
    return line

def draw(coordinate):   #大幅缩短了
    '''用于限定画面范围的图像绘制 coordinate应是字典 key为x 且x为integer value为x对应的y的集合'''
    for y in range(height+1,-1,-1):
        print('')
        former_x = 0
        for x in tuple(range(0,width+2)):
            if y in coordinate[x]:
                print('  '*(x-former_x),end='')
                print('██',end='')
                former_x = x+1


#介绍
print('3d v3.0')
print('1 可以旋转摄像机了')
print('2 精简了输入部分的代码')
print('3 精简了移动部分代码')
print('4 把函数区的return从函数变为关键字')
print('5 重写了计算平面线的函数lines() 缩短+优化 现在不会有断断续续的线了 大概')
print('6 大幅精简了draw()的代码')

print('已知"特性"')
print('1 进入长方体内部画面有问题 只能看到部分棱')


#默认值
width,height,degrees = 63,55,math.pi / 180
alpha,beta,fov = 90,0,72
A,G = [-20,-10,40],[20,10,90]
camera = [0,0,0]
print('默认数值：')
print('画面宽度 %d   画面高度 %d   视野大小%.3f°'   % (width,height,fov))
print('长方体体对角线上两点 A和G 坐标分别为 %s和%s' % (A,G))


#输入        width height fov A G
repeating_words()
val = input()
while True:
    if val == '':
        break
    elif val == 'q':
        exit()
    elif val == 'huge':
        width,height = 938,311
        break

    elif val == 'w':
        width = input('画面宽度为')
        while not width.isdecimal() or float(width) <= 0:
            width = input('\n宽度应为正整数\n')
        width = int(width)
    
    elif val == 'h':
        height = input('画面高度为')
        while not height.isdecimal() or float(height) <= 0:
            height = input('\n高度应为正整数\n')
        height = int(height)
    
    elif val == 'f':
        while True:
            fov = input('摄像机视野为')
            try:
                fov = float(fov)
                if fov >= 180 or fov <= 0:
                    fov = int('')
                break
            except:
                print('\n视野大小应在0°-180°之间且不等于0°或180° 请输入属于(0,180)的数字')
    
    elif val == 'p':
        while True:
            A = input('输入A点坐标   x y z 用空格连接\n').split()
            try:
                if len(A) != 3:
                    A = int('')
                for temp in range(0,3):
                    A[temp] = float(A[temp])
                break
            except:
                print('\n坐标形式应为如 1,-2,6.4')
                
        while True:
            G = input('输入G点坐标   x y z 用空格连接\n').split()
            try:
                if len(G) != 3:
                    G = int('')
                for temp in range(0,3):
                    G[temp] = float(G[temp])
                if G == A:
                    G = int('')
                break
            except:
                print('\n坐标形式应为如 1,-2,6.4 且A与G不应重合')

    else:
        print('输入了无效字符')
        repeating_words()
        val = input()
        continue
    
    print('')
    print('画面宽度 %d   画面高度 %d   视野大小%.3f°'   % (width,height,fov))
    print('长方体体对角线上两点 A和G 坐标分别为 %s和%s' % (A,G))
    
    val = input('\n输入回车确认 输入q退出 输入d恢复默认 输入w/h/f/p继续或重新输入')
    if val == '':
        break
    elif val == 'q':
        exit()
    elif val == 'd':
        if input('\n是否确定全部恢复默认值 若确定则输入C 输入任意取消') == 'C':
            width,height,A,G = 63,63,[-10,-5,0],[10,5,20]
            print('画面宽度 %d   画面高度 %d   视野大小%.3f°'   % (width,height,fov))
            print('长方体体对角线上两点 A和G 坐标分别为 %s和%s' % (A,G))
del val


#由自定义的量控制的量
f = (width/2)/math.tan(fov*degrees/2)   #摄像机到等效平面的距离
A,G = tuple(A),tuple(G)
B,C,D = (G[0],A[1],A[2]),(G[0],G[1],A[2]),(A[0],G[1],A[2])
E,F,H = (A[0],A[1],G[2]),(G[0],A[1],G[2]),(A[0],G[1],G[2])


while True:
    #画面边缘的框
    coordinate = {}
    for x in range(0,width+2):   #框上下两条
        coordinate[x] = {0,height+1}
    del x
    coordinate[0],coordinate[width+1] = set(range(0,height+2)),set(range(0,height+2))   #框左右两条
    
    #计算对应的二维坐标
    A2,B2 = trans(A),trans(B)
    C2,D2 = trans(C),trans(D)
    E2,F2 = trans(E),trans(F)
    G2,H2 = trans(G),trans(H)

    #计算连线线的所有的点
    ab,bc,cd,ad = lines(A2,B2),lines(B2,C2),lines(C2,D2),lines(A2,D2)
    ae,bf,cg,dh = lines(A2,E2),lines(B2,F2),lines(C2,G2),lines(D2,H2)
    ef,fg,gh,eh = lines(E2,F2),lines(F2,G2),lines(G2,H2),lines(E2,H2)
    all_lines = (ab,bc,cd,ad,ae,bf,cg,dh,ef,fg,gh,eh)

    #把坐标丢进coordinate里
    for x in range(1,width+2):
        for line in all_lines:
            if x in line.keys():
                coordinate[x].update(line[x])
    del all_lines,line,ab,bc,cd,ad,ae,bf,cg,dh,ef,fg,gh,eh
    
    #丢掉超出画面范围的y 抄的老版本的
    coordinate_temp = coordinate
    for x in coordinate_temp:
        temp = set()
        for y in coordinate_temp[x]:
            if y > height+1 or y < 0:
                temp.add(y)
        for y in temp:
            coordinate[x].remove(y)
    del coordinate_temp,x,y,temp


    #绘图
    draw(coordinate)
    print('\n当前摄像机坐标为',camera)
    print('当前摄像机朝向为%d°   %d°' % (alpha,beta))
    
    #移动摄像机
    print('直接输入WASD EF控制镜头按默认距离移动')
    print('输入W/A/S/D/E/F+数字 控制镜头按自定义距离移动')
    print('直接输入如1 2 3控制镜头到自定义坐标 空格连接')
    print('输入c使摄像头回到原点 输入q退出')
    camera_move = input()
    
    step = integer((width**2+height**2)**0.5/200)+1   #默认步长
    try:   step = int(camera_move[1:])   #按自定义步长移动
    except:   pass
    ws, ad = (cos(alpha)*step, sin(alpha)*step), (-sin(alpha)*step, cos(alpha)*step)   #按默认步长移动
    
    #单个字符控制
    #移动
    if camera_move == 'w':
        camera = [camera[0]+ws[0],camera[1],camera[2]+ws[1]]
    elif camera_move == 's':
        camera = [camera[0]-ws[0],camera[1],camera[2]-ws[1]]
    elif camera_move == 'a':
        camera = [camera[0]+ad[0],camera[1],camera[2]+ad[1]]
    elif camera_move == 'd':
        camera = [camera[0]-ad[0],camera[1],camera[2]-ad[1]]
    elif camera_move == 'e':
        camera = [camera[0],camera[1]+step,camera[2]]
    elif camera_move == 'f':
        camera = [camera[0],camera[1]-step,camera[2]]
    #旋转
    elif camera_move == '4':
        alpha += 1
        if alpha > 180:
            alpha = alpha-360
    elif camera_move == '6':
        alpha -= 1
        if alpha < -180:
            alpha = alpha+360
    elif camera_move == '8':
        beta += 1
        if beta > 90:
            beta = 90
    elif camera_move == '2':
        beta -= 1
        if beta < -90:
            beta = -90
    #控制
    elif camera_move == 'c':   #回到原点
        camera = [0,0,0]
    elif camera_move == '5':
        alpha,beta = 90,0
    elif camera_move == 'q':   #退出
        exit()
    elif camera_move == '':   #防止点快了没输入就按回车导致的bug
        print('\n'*height*2)
        continue

    #多个字符
    #移动
    elif camera_move[0] == 'w':
        camera = [camera[0]+ws[0],camera[1],camera[2]+ws[1]]
    elif camera_move[0] == 's':
        camera = [camera[0]-ws[0],camera[1],camera[2]-ws[1]]
    elif camera_move[0] == 'a':
        camera = [camera[0]+ad[0],camera[1],camera[2]+ad[1]]
    elif camera_move[0] == 'd':
       camera = [camera[0]-ad[0],camera[1],camera[2]-ad[1]]
    elif camera_move[0] == 'e':
        camera = [camera[0],camera[1]+step,camera[2]]
    elif camera_move[0] == 'f':
        camera = [camera[0],camera[1]-step,camera[2]]
    #旋转
    elif camera_move[0] == '4':
        try:   alpha += int(camera_move[1:])
        except:   pass
    elif camera_move[0] == '6':
        try:   alpha -= int(camera_move[1:])
        except:   pass
    elif camera_move[0] == '8':
        try:   beta += int(camera_move[1:])
        except:   pass
    elif camera_move[0] == '2':
        try:   beta -= int(camera_move[1:])
        except:   pass


    #按照坐标直接移动摄像机
    elif len(camera_move.split()) == 3:
        try:
            count = 0
            for temp in camera_move.split():
                camera[count] = int(temp)
                count+=1
            del temp,count
        except:   pass
    elif len(camera_move.split()) == 2:
        try:
            alpha,beta = int(camera_move.split()[0]),int(camera_move.split()[1])
            while alpha > 180:
                alpha -= 360
            while alpha < -180:
                alpha += 360
            while beta > 90:
                beta = 90
                print('β最大90°')
            while beta < -90:
                beta = -90
                print('β最小-90°')
        except: pass

    #换16行 "隐藏"上一张画面 16是随便输的 太大影响速度 太小有一点点小问题 其实也无所谓
    print('\n'*16)