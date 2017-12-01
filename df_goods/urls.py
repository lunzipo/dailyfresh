from django.conf.urls import url
from df_goods import views

urlpatterns = [
    url(r'^index/$', views.index, name='index'),  # 网站主页面
    url(r'^detail(?P<goods_id>\d+)/$', views.goods_detail, name='detail'),  # 商品详情
    url(r'^list/(?P<type_id>\d+)/(?P<page>\d+)/$', views.goods_list, name='list'),  # 商品列表
]
