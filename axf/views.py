import hashlib
import os
import uuid

from django.contrib.auth import logout
from django.http import HttpResponse
from django.shortcuts import render, redirect

# Create your views here.
from Python1809 import settings
from axf.models import Wheel, Nav, Mustbuy, Shop, MainShow, Foodtypes, Goods, User, Cart


def home(request):
    # 轮播图数据
    wheels = Wheel.objects.all()

    # 导航栏数据
    nav = Nav.objects.all()
    # 每日必购数据
    mustbuys = Mustbuy.objects.all()

    # 商品数据
    shoplist = Shop.objects.all()
    shophead = shoplist[0]
    shoptab = shoplist[1:3]
    shopclass = shoplist[3:7]
    shopcommend = shoplist[7:11]

    # 商品主体部分
    mainshows = MainShow.objects.all()

    data = {
        'title': '我的',
        'wheels': wheels,
        'nav': nav,
        'mustbuys': mustbuys,
        'shophead': shophead,
        'shoptab': shoptab,
        'shopclass':shopclass,
        'shopcommend': shopcommend,
        'mainshows': mainshows,
    }
    return render(request,'home/home.html',context=data)


def market(request,categoryid, childid, sortid):
    # 分类数据
    foodtypes = Foodtypes.objects.all()
    typeIndex = int(request.COOKIES.get('typeIndex', 0))
    print(foodtypes[typeIndex])
    categoryid = foodtypes[typeIndex].typeid
    # 子类
    childtypenames = foodtypes.get(typeid=categoryid).childtypenames # 对应分类下 子类字符串
    childlist = []
    for item in childtypenames.split('#'):
        arr = item.split(':')
        obj = {'childname':arr[0], 'childid':arr[1]}
        childlist.append(obj)

    # 商品数据
    # goodslist = Goods.objects.all()[1:10]

    # 根据商品分类 数据过滤
    if childid == '0':  # 全部分类
        goodslist = Goods.objects.filter(categoryid=categoryid)
    else:   # 对应分类
        goodslist = Goods.objects.filter(categoryid=categoryid, childcid=childid)

    # 排序处理
    if sortid == '1':   # 销量排序
        goodslist= goodslist.order_by('productnum')
    elif sortid == '2': # 价格最低
        goodslist= goodslist.order_by('price')
    elif sortid == '3': # 价格最高
        goodslist= goodslist.order_by('-price')


    # 购物车数量问题
    token = request.session.get('token')
    carts = []
    if token:
        user = User.objects.get(token=token)
        carts = Cart.objects.filter(user=user).exclude(number=0)

    data = {
        'title': '闪购超市',
        'foodtypes':foodtypes,
        'goodslist':goodslist,
        'childlist':childlist,
        'categoryid':categoryid,
        'childid':childid,
        'carts': carts
    }


    return render(request,'market/market.html',context=data)


def cart(request):

    return render(request,'cart/cart.html')


def mine(request):

    return render(request,'mine/mine.html')


def login(request):
    return render(request,'mine/login.html')

def register(request):
    if request.method == 'POST':
        user = User()
        # 用户账号
        user.account = request.POST.get('account')
        # 用户密码加密
        user.password = generate_password(request.POST.get('password'))
        # 用户名
        user.name = request.POST.get('name')
        # 电话
        user.tel = request.POST.get('tel')
        # 地址
        user.address = request.POST.get('address')
        # 头像
        imgName = user.account + '.png'
        imgPath = os.path.join(settings.MEDIA_ROOT, imgName)
        print(imgPath)
        file = request.FILES.get('file')
        print(file)
        with open(imgPath, 'wb') as fp:
            for data in file.chunks():
                fp.write(data)
        user.img = imgName

        # token
        user.token = str(uuid.uuid5(uuid.uuid4(), 'register'))
        # 用户保存
        user.save()
        # 状态保持
        request.session['token'] = user.token
        # 注册成功之后的重定向
        return redirect('axf:mine')

    elif request.method == 'GET':
        return render(request,'mine/register.html')

# 密码
def generate_password(password):
    sha = hashlib.sha512()
    sha.update(password.encode('utf-8'))
    return sha.hexdigest()
# 退出登录
def quit(request):
    logout(request)
    return redirect('axf:mine')