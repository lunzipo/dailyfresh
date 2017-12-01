$(function(){
    $('#btnLogin').click(function(){
        //获取数据
        username = $('#username').val()
        password = $('#pwd').val()
        csrf = $('input[name="csrfmiddlewaretoken"]').val()
        remember = $('input[name="remember"]').prop('checked')
        // 发起ajax请求
        params = {'username':username, 'password':password, 'csrfmiddlewaretoken':csrf, 'remember':remember}
        $.post('/user/login_check/', params, function(data){
            // 用户名密码错误{'res':0}
            // 登录成功{'res':1}
            if (data.res == 0)
            {
                $('#username').next().html('用户名或密码错误').show()
            }
            else
            {
                // 跳转页面
                location.href = data.next_url  // /user/
            }
        });
    });

})


