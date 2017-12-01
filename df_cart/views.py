from django.shortcuts import render
from django.http import JsonResponse
from df_goods.models import Goods
from django_redis import get_redis_connection
from utils.decorators import login_required
# Create your views here.


# 前端post提交发过来的数据： 商品的id 商品的数目 goods_id goods_count
# 涉及到数据的修改用post方式
def cart_add(request):
    '''向购物车添加数据'''
    # 判断用户是否登录
    if not request.session.has_key('islogin'):
        return JsonResponse({'res': 0, 'errmsg': '请先登录'})
    # 接收数据
    goods_id = request.POST.get('goods_id')
    goods_count = request.POST.get('goods_count')
    # 进行数据校验
    if not all([goods_id, goods_count]):
        return JsonResponse({'rers': 1, 'errmsg': '数据不完整'})
    goods = Goods.objects.get_goods_by_id(goods_id=goods_id)
    if goods is None:
        return JsonResponse({'res': 2, 'errmsg': '商品不存在'})
    # 将商品数目转换成整型
    try:
        count = int(goods_count)
    except Exception as e:
        # 商品数目不合法
        return JsonResponse({'res': 3, 'errmsg': '商品数量必须是整数'})
    # 添加商品到购物车
    # 每个用户的购物车记录用一条hash数据保存，格式为：cart_用户id:商品id 商品数量
    conn = get_redis_connection('default')
    cart_key = 'cart_%d' % request.session.get('passport_id')
    # 获取goods_count,购物车本来有的商品数目
    res = conn.hget(cart_key, goods_id)
    if res is None:
        # 用户购物车没有添加过该商品
        res = count
    else:
        # 用户购物车中已经添加过该商品
        res = int(res)+count
    # 判断商品的库存
    if res > goods.stock:
        # 库存不足
        return JsonResponse({'res': 4, 'errmsg': '商品库存不足'})
    else:
        conn.hset(cart_key, goods_id, res)
    # 返回结果
    return JsonResponse({'res': 5})


def cart_count(request):
    '''获取用户购物车中商品的数目'''
    # 判断用户是否登录
    if not request.session.has_key('islogin'):
        return JsonResponse({'res': 0})
    # 计算用户购物车商品的件数
    conn = get_redis_connection('default')
    cart_key = 'cart_%d' % request.session.get('passport_id')
    # res = conn.hlen(cart_key)
    res = 0
    res_list = conn.hvals(cart_key)

    for i in res_list:
        res += int(i)

    # 返回结果
    return JsonResponse({'res': res})


# http://127.0.0.1:8000/cart/
@login_required
def cart_show(request):
    '''显示用户购物车页面'''
    passport_id = request.session.get('passport_id')
    # 获取用户购物车的记录
    conn = get_redis_connection('default')
    cart_key = 'cart_%d' % passport_id
    res_dict = conn.hgetall(cart_key)
    goods_li = []
    # 保存购物车商品总件数
    goods_type_count = conn.hlen(cart_key)
    # 保存购物车商品总数目
    total_count = 0
    # 保存所有商品的价格
    total_price = 0

    # 遍历res_dict获取商品的数据
    for id, count in res_dict.items():
        # 根据id获取商品的信息
        goods = Goods.objects.get_goods_by_id(goods_id=id)
        # 保存商品的数目（动态增加）
        goods.count = count
        # 保存商品的小计（动态增加）
        goods.amount = int(count)*goods.price
        goods_li.append(goods)
        total_count += int(count)
        total_price += int(count)*goods.price
    # 定义模板上下文
    context = {'goods_li': goods_li, 'total_count': total_count,
               'total_price': total_price, 'goods_type_count': goods_type_count}
    return render(request, 'df_cart/cart.html', context)


def update(request):
    '''更改redis数据库中商品的数目'''
    # 判断是否登录
    if not request.session.has_key('islogin'):
        return JsonResponse({'res': 0, 'errmsg': '用户未登录'})
    # 接收数据
    goods_id = request.POST.get('goods_id')
    goods_count = request.POST.get('goods_count')
    # 校验数据
    if not all([goods_id, goods_count]):
        return JsonResponse({'res': 1, 'errmsg': '数据不完整'})
    goods = Goods.objects.get_goods_by_id(goods_id=goods_id)
    if goods is None:
        return JsonResponse({'res': 2, 'errmsg': '商品不存在'})
    try:
        goods_count = int(goods_count)
    except Exception as e:
        return JsonResponse({'res': 3, 'errmsg': '商品数目必须为数字'})
    if goods_count > goods.stock:
        return JsonResponse({'res': 4, 'errmsg': '商品库存不足'})
    # 更新操作
    conn = get_redis_connection('default')
    cart_key = 'cart_%d'%request.session.get('passport_id')
    conn.hset(cart_key, goods_id, goods_count)
    # 返回数据
    return JsonResponse({'res': 5})


def delete(request):
    '''删除购物车商品'''
    if not request.session.has_key('passport_id'):
        return JsonResponse({'res': 0, "errmsg": '商品不存在'})
    # 获取数据
    goods_id = request.POST.get('goods_id')
    # 校验数据
    if not all([goods_id]):
        return JsonResponse({'res': 1, 'errmsg': '数据不能为空'})
    goods = Goods.objects.get_goods_by_id(goods_id=goods_id)
    if goods is None:
        return JsonResponse({'res': 2, 'errmsg': '商品不存在'})
    # 删除购物车商品信息
    conn = get_redis_connection('default')
    cart_key = 'cart_%d'%request.session.get('passport_id')
    conn.hdel(cart_key, goods_id)
    goods_type_count = conn.hlen(cart_key)
    # 返回信息
    return JsonResponse({'res': 3, 'goods_type_count': goods_type_count})










