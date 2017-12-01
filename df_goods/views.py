from django.shortcuts import render, redirect
from django.core.urlresolvers import reverse
from df_goods.models import Goods, GoodsImage
from df_goods.enums import *
from django_redis import get_redis_connection
from django.core.paginator import Paginator

# Create your views here.


# /index/
def index(request):
    '''显示主页面'''
    # 查询每个商品种类3条新品信息和4条销量最高的商品
    fruit_new = Goods.objects.get_goods_by_type(FRUIT, 3, sort='new')
    fruit_hot = Goods.objects.get_goods_by_type(FRUIT, 4, sort='hot')
    seafood_new = Goods.objects.get_goods_by_type(SEAFOOD, 3, sort='new')
    seafood_hot = Goods.objects.get_goods_by_type(SEAFOOD, 4, sort='hot')
    meat_new = Goods.objects.get_goods_by_type(MEAT, 3, sort='new')
    meat_hot = Goods.objects.get_goods_by_type(MEAT, 4, sort='hot')
    eggs_new = Goods.objects.get_goods_by_type(EGGS, 3, sort='new')
    eggs_hot = Goods.objects.get_goods_by_type(EGGS, 4, sort='hot')
    vegetables_new = Goods.objects.get_goods_by_type(VEGETABLES, 3, sort='new')
    vegetables_hot = Goods.objects.get_goods_by_type(VEGETABLES, 4, sort='hot')
    frozen_new = Goods.objects.get_goods_by_type(FROZEN, 3, sort='new')
    frozen_hot = Goods.objects.get_goods_by_type(FROZEN, 4, sort='hot')
    # 定义模板上下文
    context = {'fruit_new': fruit_new, 'fruit_hot': fruit_hot,
               'seafood_new': seafood_new, 'seafood_hot': seafood_hot,
               'meat_new': meat_new, 'meat_hot': meat_hot,
               'eggs_new': eggs_new, 'eggs_hot': eggs_hot,
               'vegetables_new': vegetables_new, 'vegetables_hot': vegetables_hot,
               'frozen_new': frozen_new, 'frozen_hot': frozen_hot}
    return render(request, 'df_goods/index.html', context)


# /list/
def list(request, goods_id):
    '''显示商品列表页面'''
    # 获取商品的详细信息(位置参数)
    goods = Goods.objects.get_goods_by_type(goods_id=goods_id)
    if goods is None:
        # 如果商品不存在，返回首页
        return redirect(reversed('goods:index'))
    # 获取商品的详情图片
    images = GoodsImage.objects.filter(goods_id=goods_id)
    if images.exists():
        # 有图片
        image = images[0]
    else:
        # 没有图片
        image = ''
    return render(request, 'df_goods/list.html')


# /detail/
def goods_detail(request, goods_id):
    '''显示商品详细信息'''
    # 获取商品的详细信息
    goods = Goods.objects.get_goods_by_id(goods_id=goods_id)
    if goods is None:
        # 商品不存在，跳转到首页
        return redirect(reverse('goods:index'))
    # 获取商品的详情图片
    images = GoodsImage.objects.filter(goods_id=goods_id)
    if images.exists():
        # 有图片
        images = images[0]
    else:
        # 没有图片
        images = ''
    # 新品推荐
    goods_li = Goods.objects.get_goods_by_type(type_id=goods.type_id, limit=2, sort='new')
    # 用户登录后，才记录浏览记录
    if request.session.has_key('islogin'):
        # 用户已经登录，记录浏览记录
        con = get_redis_connection('default')
        key = 'history_%d' % request.session.get('passport_id')
        # 先从redis列表中移除goods_id
        con.lrem(key, 0, goods_id)
        # 将商品浏览记录添加到列表中
        con.lpush(key, goods_id)
        # 保存用户最近浏览的5个商品
        con.ltrim(key, 0, 4)
    # 定义上下文
    context = {'goods': goods, 'goods_li': goods_li, 'images': images}
    return render(request, 'df_goods/detail.html', context)


# 商品种类 页码 排序方式
# /list/(种类id)/(页码)/?sort=排序方式
def goods_list(request, type_id, page):
    '''显示商品列表'''
    # 获取排序方式
    sort = request.GET.get('sort', 'default')
    # 判断type_id是否合法
    if int(type_id) not in GOODS_TYPES.keys():
        return redirect(reverse('goods:index'))
    # 根据商品种类id和排序方式查询数据
    goods_li = Goods.objects.get_goods_by_type(type_id=type_id, sort=sort)
    # 分页
    paginator = Paginator(goods_li, 1)
    # 获取分页之后的总页数
    num_pages = paginator.num_pages
    # 获取第page页的数据
    if page == '' or int(page) > num_pages:
        page = 1
    else:
        page = int(page)
    # 返回值是一个page类的实例对象
    goods_li = paginator.page(page)
    # 页码控制
    if num_pages < 5:
        pages = range(1, num_pages+1)
    elif page <= 3:
        pages = range(1, 6)
    elif num_pages - page <= 2:
        pages = range(num_pages-4, num_pages+1)
    else:
        pages = range(page-2, page+3)
    # 新品推荐
    goods_new = Goods.objects.get_goods_by_type(type_id=type_id, limit=2, sort='new')
    # 定义上下文
    type_title = GOODS_TYPES[int(type_id)]
    context = {'goods_li': goods_li, 'goods_new': goods_new,
               'type_id': type_id, 'sort': sort,
               'type_title': type_title, 'pages': pages}
    # 使用模板
    return render(request, 'df_goods/list.html', context)



