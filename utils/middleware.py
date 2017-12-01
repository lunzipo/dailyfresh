class UrlPathRecordMiddleware(object):
    '''记录用户访问的url地址'''
    EXCLUDE_URLS = ['/user/register/', '/user/login/', '/user/logout/']  # 排除的列表

    # 中间件
    def process_view(self, request, view_func, *view_args, **view_kwargs):
        # 当用户请求的地址不在排除的列表中，同时不是ajax请求，请求方式为get
        # 该中间件为访问视图views前访问
        if request.path not in UrlPathRecordMiddleware.EXCLUDE_URLS and not\
                request.is_aiax() and request.method == "GET":
            request.session['url_path'] = request.path


