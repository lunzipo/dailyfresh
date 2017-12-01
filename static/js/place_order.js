$(function () {
    $('#order_btn').click(function() {
        // 获取收获地址的id，支付方式，用户购买的商品的id
        addr_id = $('input[name="addr_id"]').val()
        pay_method = $('input[name="pay_style"]').val()
        goods_ids = $(this).attr('goods_ids')
		csrf = $('input[name="csrfmiddlewaretoken"]').val()
        // alert(addr_id+':'+pay_method+':'+goods_ids)
        // 发起post请求，访问/order/commit/
        params={'addr_id': addr_id, 'pay_method': pay_method, 'goods_ids': goods_ids, 'csrfmiddlewaretoken': csrf}
        // alert(params.csrfmiddlewaretoken)
        $.post('/order/commit/', params, function (data) {
            // alert('表单已经提交！')
            // alert(data.res)
            if (data.res==7){
                localStorage.setItem('order_finish',2);
                $('.popup_con').fadeIn('fast', function() {
                    setTimeout(function(){
                        $('.popup_con').fadeOut('fast',function(){
                            window.location.href = '/user/order/';
                        });
                    },3000)
                });
            }
            else{
                alert(data.errmsg)
            }
        })
    });
})

