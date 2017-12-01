from django.conf.urls import url
from df_order import views

urlpatterns = [
    url(r'^$', views.order_show, name='order_place'),  # 订单显示页面
    url(r'^commit/$', views.order_commit, name='commit'),  # 订单提交

]