$(function(){
    update_total_price();
    // 计算总价
    function update_total_price(){
        // 获取商品的价格和数量
        goods_price = $('.show_pirze').children('em').text();
        goods_count = $('.num_show').val();
        // 计算商品的价格
        goods_price = parseFloat(goods_price);
        goods_count = parseInt(goods_count);
        total_price = goods_price * goods_count;
        // 设置商品的价格
        $('.total').children('em').text(total_price.toFixed(2)+'元');
    };
    // 商品增加
    $('.add').click(function () {
        // 获取商品的数量
        goods_count = $('.num_show').val();
        // 加1
        goods_count = parseInt(goods_count)+1;
        // 重新设置值
        $('.num_show').val(goods_count);
        // 计算总价
        update_total_price();
    });
    // 商品减少
    $('.minus').click(function () {
        // 获取商品的数量
        goods_count = $('.num_show').val();
        // 加1
        goods_count = parseInt(goods_count)-1;
        if (goods_count==0)
        {
            goods_count = 1
        }
        // 重新设置值
        $('.num_show').val(goods_count);
        // 计算总价
        update_total_price();
    });
    // 手动输入
    $('.num_show').blur(function () {
        // 获取商品的数量
        goods_count = $(this).val();
        // 数据检验
        if (isNaN(goods_count) || goods_count.trim().length == 0 || parseInt(goods_count) <= 0 )
        {
            goods_count = 1
        }
        // 重新设置值
        $('.num_show').val(parseInt(goods_count));
        // 计算总价
        update_total_price();
    })
    var $add_x = $('#add_cart').offset().top;
    var $add_y = $('#add_cart').offset().left;

    var $to_x = $('#show_count').offset().top;
    var $to_y = $('#show_count').offset().left;
    $('#add_cart').click(function(){
        goods_id = $(this).attr('goods_id')
        goods_count = $('.num_show').val()
        csrf = $('input[name="csrfmiddlewaretoken"]').val()
        params = {'goods_id':goods_id, 'goods_count':goods_count,
                        'csrfmiddlewaretoken':csrf}
        $.post('/cart/add/', params, function (data) {
            if (data.res == 5){
                // 添加成功
                $(".add_jump").css({'left':$add_y+80,'top':$add_x+10,'display':'block'})
                $(".add_jump").stop().animate({
                    'left': $to_y+7,
                        'top': $to_x+7},
                    "fast", function() {
                        $(".add_jump").fadeOut('fast',function(){
                            // 获取原有show_count的值
                            count = $('#show_count').html()
                            count = parseInt(count)+parseInt(goods_count)
                            $('#show_count').html(count);
                        });
                    });
            }
            else {
                    // 添加失败
                    alert(data.errmsg)
                }
        } )
    })

})
