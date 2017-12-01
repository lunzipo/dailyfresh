from django.conf.urls import url
from df_cart import views

urlpatterns = [
    url(r'^add/$', views.cart_add, name='add'),  # 往购物车添加商品
    url(r'^$', views.cart_show, name='show'),  # 购物车页面
    url(r'^count/$', views.cart_count, name='count'),  # 购物车商品数目
    url(r'update/$', views.update, name='update'),  # 更新redis数据库
    url(r'delete/$', views.delete, name='delete'),  # 删除商品

]