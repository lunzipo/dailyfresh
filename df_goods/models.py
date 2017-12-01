from django.db import models
from db.base_model import BaseModel
from df_goods.enums import *
from tinymce.models import HTMLField
# Create your models here.


class GoodsManage(models.Manager):
    '''商品模型管理器类'''
    def get_goods_by_type(self, type_id, limit=None, sort='default'):  # default为默认参数
        # 通过商品种类查询商品
        if sort == 'new':
            order_by = ('-create_time',)
        elif sort == 'hot':
            order_by = ('-sales',)
        elif sort == 'price':
            order_by = ('price',)
        else:
            order_by = ('-pk',)
        goods_li = self.filter(type_id=type_id).order_by(*order_by)
        # 查询结果集的限制
        if limit:
            goods_li = goods_li[:limit]  # 将列表切片
        return goods_li

    def get_goods_by_id(self, goods_id):
        '''根据商品的id获取商品的信息'''
        try:
            goods = self.get(id=goods_id)
        except self.model.DoesNotExist:
            # 不存在商品信息
            goods = None
        return goods


class Goods(BaseModel):
    '''商品模型类'''
    goods_type_choices = ((k, v) for k, v in GOODS_TYPES.items())
    status_choices = ((k, v) for k, v in STATUS_CHOICE.items())
    type_id = models.SmallIntegerField(default=FRUIT, choices=goods_type_choices, verbose_name='商品种类')
    name = models.CharField(max_length=20, verbose_name='商品名称')
    desc = models.CharField(max_length=256, verbose_name='商品简介')
    price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='商品单价')
    unite = models.CharField(max_length=20, verbose_name='商品单位')
    stock = models.IntegerField(default=1, verbose_name='商品库存')
    sales = models.IntegerField(default=0, verbose_name='商品销量')
    detail = HTMLField(verbose_name='商品详情')
    image = models.ImageField(upload_to='goods', verbose_name='商品图片')
    status = models.SmallIntegerField(default=ONLINE, choices=status_choices, verbose_name='商品状态')

    objects = GoodsManage()

    class Meta:
        db_table = 's_goods'


class ImageManage(models.Manager):
    '''商品图片模型管理器类'''
    pass


class GoodsImage(BaseModel):
    '''图片模型类'''
    goods = models.ForeignKey('goods', verbose_name='所属商品')
    image = models.ImageField(upload_to='goods', verbose_name='商品图片')

    objects = ImageManage()

    class Meta:
        db_table = 's_goods_image'


