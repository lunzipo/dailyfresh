from django.conf.urls import url
from df_user import views

urlpatterns = [
    url(r'^register/$', views.register, name='register'),  # 显示注册页面
    url(r'^register_handles/$', views.register_handles, name='register_handles'),  # 用户注册
    url(r'^login/$', views.login, name='login'),  # 显示注册页面
    url(r'^check_user_exist/$', views.check_user_exist, name='check_user_exist'),  # 判断用户是否存在
    url(r'^active/(?P<token>.*)/$', views.register_active, name='active'),  # 邮箱激活账户
    url(r'^login_check/$', views.login_check, name='login_check'),  # 用户登录
    url(r'^logout/$', views.logout, name='logout'),  # 退出用户登录
    url(r'^$', views.user, name='user'),  # 用户中心-信息页
    url(r'^order/$', views.order, name='order'),  # 用户中心-订单页
    url(r'^address/$', views.address, name='address'),  # 用户中心-地址页
]