from django.shortcuts import render, redirect
from django.core.urlresolvers import reverse
from utils.decorators import login_required
from df_user.models import Address
from df_goods.models import Goods
from django_redis import get_redis_connection
from df_order.models import OrderGoods, OrderInfo
from django.http import JsonResponse, HttpResponse
from datetime import datetime
from django.db import transaction
# Create your views here.


# 用户收货地址（addr），用户选中的商品（goods_li），
# 订单信息（总价total_price，总数目total_count，运费，transit，实付费total_pay，）
# goods_ids（字符串）
@login_required
def order_show(request):
    '''显示提交订单页面'''
    # 接收数据,post表单提交的goods_ids是个列表，用getlist方法可以获取列表
    goods_ids = request.POST.getlist('goods_ids')
    # # 校验数据
    if not all(goods_ids):
        # 跳转回购物车页面
        return redirect(reverse('cart:show'))
    # 获取用户收获地址
    passport_id = request.session.get('passport_id')
    addr = Address.objects.get_default_address(passport_id=passport_id)
    # 用户要购买的商品的信息
    goods_li = []
    # 商品的数目和总金额,从redis数据库获取
    total_count = 0
    total_price = 0

    conn = get_redis_connection('default')
    cart_key = 'cart_%d' % passport_id

    for goods_id in goods_ids:
        # 根据id获取商品的信息
        goods = Goods.objects.get_goods_by_id(goods_id=goods_id)
        # 从redis数据库获得用户要购买的商品的数目
        count = conn.hget(cart_key, goods_id)
        goods.count = count  # 给goods添加静态属性商品数目count
        # 计算商品的小计
        amount = int(count)*goods.price
        goods.amount = amount  # 给goods添加静态属性商品总价amount
        goods_li.append(goods)
        # 累计计算商品的总数目和总金额
        total_count += int(count)
        total_price += amount
    # 商品运费和实付款
    transit_price = 10
    total_pay = total_price + transit_price

    # 将列表goods_ids转换成字符串
    goods_ids = ','.join(goods_ids)
    # 组织模板上下文
    context = {'addr': addr, 'goods_li': goods_li,
               'total_count': total_count, 'total_price': total_price,
               'transit_price': transit_price, 'total_pay': total_pay,
               'goods_ids': goods_ids}
    # 使用模板
    return render(request, 'df_order/place_order.html', context)


@transaction.atomic  # 事务
def order_commit(request):
    '''生成订单'''
    # 验证用户是否登录
    if not request.session.has_key('islogin'):
        return JsonResponse({'res': 0, 'errmsg': '用户没有登录'})

    # 接收数据
    addr_id = request.POST.get('addr_id')
    pay_method = request.POST.get('pay_method')
    goods_ids = request.POST.get('goods_ids')

    # 校验数据
    if not all([addr_id, pay_method, goods_ids]):
        return JsonResponse({'res': 1, 'errmsg': '数据不完整'})
    try:
        addr = Address.objects.get(id=addr_id)
    except Exception as e:
        # 地址信息出错
        return JsonResponse({'res': 2, 'errmsg': '地址信息出错'})
    if int(pay_method) not in OrderInfo.PAY_METHODS_ENUM.values():
        return JsonResponse({'res': 3, 'errmsg': '不支持的支付方式'})

    # 订单创建
    # 组织订单信息
    passport_id = request.session.get('passport_id')
    # 订单编号
    order_id = datetime.now().strftime('%Y%m%d%H%M%S')+str(passport_id)
    # 运费
    transit_price = 10
    # 订单商品总数和总金额
    total_count = 0
    total_price = 0
    goods_ids = goods_ids.split(',')
    conn = get_redis_connection('default')
    cart_key = 'cart_%d' % passport_id
    # 创建一个保存点
    sid = transaction.savepoint()
    # 遍历获取用户购买的商品信息
    # 订单商品表，主键为id
    try:
        # 创建一条订单信息表记录,主键为order_id
        order = OrderInfo.objects.create(order_id=order_id,
                                 passport_id=passport_id,
                                 addr_id=addr_id,
                                 total_count=total_count,
                                 total_price=total_price,
                                 transit_price=transit_price,
                                 pay_method=pay_method)
        for id in goods_ids:
            goods = Goods.objects.get_goods_by_id(goods_id=id)
            if goods is None:
                return JsonResponse({'res': 4, 'errmsg': '商品信息出错'})
            # 获取用户购买的商品数目
            count = conn.hget(cart_key, id)
            # 判断商品的库存
            if int(count) > goods.stock:
                return JsonResponse({'res': 5, 'errmsg': '商品库存不足'})
            # 创建一条订单商品记录
            OrderGoods.objects.create(order_id=order_id,
                                      goods_id=id,
                                      count=count,
                                      price=goods.price)
            # 增加商品的销量，减少商品的库存
            goods.sales += int(count)
            goods.stock -= int(count)
            goods.save()
            # 累计计算商品的总数目和总金额
            total_count += int(count)
            total_price += int(count)*goods.price
            # 更新订单的商品数目和总金额
            order.total_price = total_price
            order.total_count = total_count
            order.save()

    except Exception as e:
        transaction.savepoint_rollback(sid)
        return JsonResponse({'res': 6, 'errmsg': '服务器错误'})
    # 清除购物车对应的记录
    conn.hdel(cart_key, *goods_ids)
    # 返回应答
    return JsonResponse({'res': 7})



