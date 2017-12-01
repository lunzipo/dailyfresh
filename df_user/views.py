from django.shortcuts import render, redirect
from django.http import HttpResponse, JsonResponse
from df_user.models import Passport, Address
from django.conf import settings
from celery_tasks.tasks import send_active_email
# import re  # 导入正则匹配
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from itsdangerous import SignatureExpired
from django.core.urlresolvers import reverse
from utils.decorators import login_required
from django.views.decorators.http import require_GET, require_POST, require_http_methods
from django_redis import get_redis_connection
from df_goods.models import Goods
from df_order.models import OrderInfo, OrderGoods
# Create your views here.


# /user/register/
def register(request):
    '''显示注册页面'''
    return render(request, 'df_user/register.html')


def register_handles(request):
    '''进行用户注册数据处理'''
    # 接收数据
    username = request.POST.get('user_name')
    password = request.POST.get('pwd')
    # cpassword = request.POST.get('cpwd')
    email = request.POST.get('email')
    # # 判断是否为空
    # if not all([username, password, cpassword, email]):
    #     return render(request, 'df_user/register.html', {'errodata': '参数不能为空'})
    # # 判断邮箱是否合理
    # if not re.match(r'/^[a-z0-9][\w\.\-]*@[a-z0-9\-]+(\.[a-z]{2,5}){1,2}$/')

    # 数据库保存注册用户（方法1：用save保存）
    # p = Passport()
    # p.username = username
    # p.password = password
    # p.email = email
    # p.save()
    # 数据库保存注册用户（方法2：）
    # passport = Passport(username=username, password=password, email=email)
    # passport.save()
    # Passport.objects.create(username=username, password=password, email=email)
    # 数据库保存注册用户（方法3：函数封装）
    passport = Passport.objects.add_one_passport(username=username, password=password, email=email)

    # 生成激活的token
    serializer = Serializer(settings.SECRET_KEY, 3600)  # 设置链接失效时间为3600秒
    token = serializer.dumps({'confirm': passport.id})  # dumps将id加密，返回的是byte类型
    token = token.decode()

    # 给用户的邮箱发送激活邮件
    # send_mail('天天生鲜用户激活', '', settings.EMAIL_FROM, [email], html_message='<a href="www.baidu.com">百度</a>')
    # send_mail('天天生鲜用户激活', '激活请点击', settings.EMAIL_FROM, [email], )

    send_active_email.delay(token, username, email)  # delay延时，是设置异步执行，邮箱发送和页面跳转同时进行
    return redirect('/user/login/')


@require_GET
def check_user_exist(request):
    '''检验用户名是否存在'''
    # 1.接收数据
    username = request.GET.get('username')
    # 2.根据用户名在数据库查找
    try:
        Passport.objects.get(username=username)
        return JsonResponse({'res': 0})
    except Passport.DoesNotExist:
        # 用户名可用
        return JsonResponse({'res': 1})


def register_active(request, token):
    '''邮箱激活账户'''
    serializer = Serializer(settings.SECRET_KEY, 3600)  # 设置过期时间为3600秒，期间链接有效
    try:
        info = serializer.loads(token)  # load将加密的用户id解密
        passport_id = info['confirm']
        #  进行用户激活
        passport = Passport.objects.get(id=passport_id)
        passport.is_active = True
        passport.save()
        # 页面跳转
        return HttpResponse('激活成功！')
    except SignatureExpired:
        # 链接过期
        return HttpResponse('激活链接已经过期！')


# /user/login/
def login(request):
    '''显示登录页面'''
    # 判断cookies中是否有username
    if 'username' in request.COOKIES:
        username = request.COOKIES['username']
        checked = 'checked'
    else:
        username = ''
        checked = ''
    return render(request, 'df_user/login.html', {'username': username, 'checked': checked})
    # return render(request, 'df_user/login.html')


# @require_POST
def login_check(request):
    '''登录验证'''
    # 1.获取数据
    username = request.POST.get('username')
    password = request.POST.get('password')
    remember = request.POST.get('remember')
    # 2.数据校验
    if not all([username, password, remember]):
        # 数据为空
        return JsonResponse({'res': 0})
    # 3.进行处理：根据用户名和密码查找账户信息
    passport = Passport.objects.get_one_passport(username=username, password=password)
    if passport:
        # 返回之前登录的页面
        next_url = request.session.get('url_path', reverse('goods:index'))  # url_path有值返回，没有的话取index
        jres = JsonResponse({'res': 1, 'next_url': next_url})

        # 判断是否需要记住用户名
        if remember == "true":
            # 记住用户名
            jres.set_cookie('username', username, max_age=7*24*3600)  # 时间一周
        else:
            # 不要记住用户名
            jres.delete_cookie('username')
        # 记住用户的登录状态
        request.session['islogin'] = True
        request.session['username'] = username
        request.session['passport_id'] = passport.id
        return jres
    else:
        # 用户名或密码错误
        return JsonResponse({'res': 0})


# /user/logout
def logout(request):
    '''用户退出登录'''
    # 清空用户的session信息
    request.session.flush()
    # 跳转到首页
    return redirect(reverse('goods:index'))


@login_required
def user(request):
    '''用户中心-信息页'''
    passport_id = request.session.get('passport_id')
    # 获取用户的基本信息
    addr = Address.objects.get_default_address(passport_id=passport_id)
    # 获取用户的最近浏览记录
    conn = get_redis_connection('default')
    key = 'history_%d'%passport_id
    # 取出最近用户浏览的5个商品的id
    history_li = conn.lrange(key, 0, 4)

    goods_li = []
    for id in history_li:
        goods = Goods.objects.get_goods_by_id(goods_id=id)
        goods_li.append(goods)

    return render(request, 'df_user/user_center_info.html', {'addr': addr,
                                                             'page': 'user',
                                                             'goods_li': goods_li})

@login_required
def order(request):
    '''用户中心-订单页'''
    passport_id = request.session.get('passport_id')
    # 查询用户的订单信息,passport_id是外键，一个用户可以有多个订单
    order_info_li = OrderInfo.objects.filter(passport_id=passport_id).order_by('-create_time')
    # 遍历获取的订单的商品信息
    for order_info in order_info_li:
        order_id = order_info.order_id  # 订单编号
        # 根据订单编号查询商品，一个订单可能包含多个商品
        order_goods_li = OrderGoods.objects.filter(order_id=order_id)
        # 计算商品的小计
        for goods in order_goods_li:
            count = goods.count
            price = goods.price
            amount = count*price
            # 保存订单中每一个商品的小计
            goods.amount = amount
        # 给order对象动态增加一个属性order_goods_li,保存所有商品(OrderGoods)
        order_info.order_goods_li = order_goods_li
    return render(request, 'df_user/user_center_order.html', {'order_info_li': order_info_li,})


@require_http_methods(['GET', 'POST'])
@login_required
def address(request):
    '''用户中心-地址页'''
    # 获取登录用户的id
    passport_id = request.session.get('passport_id')
    if request.method == 'GET':
        addr = Address.objects.get_default_address(passport_id=passport_id)
        return render(request, 'df_user/user_center_site.html', {'addr': addr})
    else:
        # 添加收货地址
        # 1.获取数据
        recipient_name = request.POST.get('username')
        recipient_addr = request.POST.get('addr')
        zip_code = request.POST.get('zip_code')
        recipient_phone = request.POST.get('phone')
        # 2.进行校验
        if not all([recipient_name, recipient_addr, zip_code, recipient_phone]):
            return render(request, 'df_user/user_center_site.html', {'erromsg': '参数不能为空'})
        # 3.添加收货地址
        Address.objects.add_one_address(passport_id=passport_id,
                                        recipient_name=recipient_name,
                                        recipient_addr=recipient_addr,
                                        zip_code=zip_code,
                                        recipient_phone=recipient_phone,
                                        )
        addr = Address.objects.get_default_address(passport_id=passport_id)
        # 4.返回应答
        # return redirect(reverse('user: address', {'addr': addr}))
        return render(request, 'df_user/user_center_site.html', {'addr': addr})








