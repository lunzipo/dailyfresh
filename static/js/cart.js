$(function(){
    // 计算所有被选中的商品的总价，总数量和商品的小计
    function update_total_price(){
        total_count = 0
        total_price = 0
        // 获取所有被选中的商品的ul元素
        $('.cart_list_td').find(':checked').parents('ul').each(function(){
            // 获取每一个商品的价格和数量
            goods_price = $(this).children('.col05').text()
            goods_count = $(this).find('.num_show').val()
            // 计算商品的小计
            goods_price = parseFloat(goods_price)
            goods_count = parseInt(goods_count)
            goods_amount = goods_price*goods_count
            // 设置商品的小计
            $(this).children('.col07').text(goods_amount.toFixed(2)+'元')
            total_count += goods_count
            total_price += goods_amount
        })
        // 设置商品的总价和总数目
        $('.settlements').find('em').text(total_price.toFixed(2))
        $('.settlements').find('b').text(total_count)
    }

    // 全选和全不选
    $('.settlements').find(':checkbox').change(function () {
        // 获取全选checkbox的选中状态
        is_checked = $(this).prop('checked')
        // 遍历所有商品对应的checkbox，设置checked属性和全选checkbox一样
        $('.cart_list_td').find(':checkbox').each(function () {
            $(this).prop('checked', is_checked)
        })
        // 更新商品的信息
        update_total_price()
    })

    // 商品对应的checkbox状态发生改变时，全选checkbox的改变
    $('.cart_list_td').find(':checkbox').change(function () {
            // 获取所有商品对应的checkbox的数目
            all_len = $('.cart_list_td').find(':checkbox').length
            // 获取所有被选中商品的checkbox的数目
            checked_len  = $('.cart_list_td').find(':checked').length
            if (checked_len < all_len){
                $('.settlements').find(':checkbox').prop('checked', false)
            }
            else {
                 $('.settlements').find(':checkbox').prop('checked', true)
            }

            // 更新商品的信息
            update_total_price()
        })
    // 更新redis数据库中购物车的商品数目
    error_update = false
    function update_remote_cart_info(goods_id, goods_count){
        csrf = $('input[name="csrfmiddlewaretoken"]').val()
        params = {'goods_id': goods_id, 'goods_count': goods_count,
                    'csrfmiddlewaretoken': csrf}
        // 设置同步
        $.ajaxSettings.async = false
        // 发起请求，访问/cart/update/
        $.post('/cart/update/', params, function (data) {
            if (data.res == 5){
                // 后台修改数据成功
                error_update = false
            }
            else{
                // 后台修改数据失败
                error_update = true
                alert(data.errmsg)
            }
        })
        // 将请求设置为异步
        $.ajaxSettings.async = true
    }

    // 更新total_count

    
    // 商品数量增加
    $('.add').click(function () {
        // 获取商品的数目和商品的id
        goods_count = $(this).next().val()
        goods_id = $(this).next().attr('goods_id')
        // 更新购物车信息
        goods_count = parseInt(goods_count)+1
        // 向数据库提交更改
        update_remote_cart_info(goods_id, goods_count)
        // 根据更新的结果进行操作
        if (error_update == false){
            // 更新成功,设置商品的购买数目
            $(this).next().val(goods_count)
            // 获取商品对应的checkbox的选中状态
            is_checked = $(this).parents('ul').find(':checkbox').prop('checked')
            if (is_checked){
                // 更新订单商品的总数目，总金额，商品小计
                update_total_price()
            }
        }
    })

    // 商品数量减少
    $('.minus').click(function () {
        // 获取商品的数目和商品的id
        goods_count = $(this).prev().val()
        goods_id = $(this).prev().attr('goods_id')
        // 更新购物车信息
        goods_count = parseInt(goods_count-1)
        if (goods_count <= 0){
            goods_count = 1
        }
        // 向数据库提交更改
        update_remote_cart_info(goods_id, goods_count)
        // 根据更新的结果进行操作
        if (error_update == false){
            // 更新成功,设置商品的购买数目
            $(this).prev().val(goods_count)
            // 获取商品对应的checkbox的选中状态
            is_checked = $(this).parents('ul').find(':checkbox').prop('checked')
            if (is_checked){
                // 更新订单商品的总数目，总金额，商品小计
                update_total_price()
            }
        }
    })

    // 手动输入商品数量
    pre_goods_count = 0
    $('.num_show').focus(function () {
        pre_goods_count = $(this).val()
    })
    $('.num_show').blur(function () {
        // 获取商品的数目和商品的id
        goods_count = $(this).val()
        goods_id = $(this).attr('goods_id')
        // 校验用户输入的商品数目
        if (isNaN(goods_count) || goods_count.trim().length==0 || parseInt(goods_count) <= 0){
            // 设置回输入之前的值
            $(this).val(pre_goods_count)
            return
        }
        // 更新购物车信息
        goods_count = parseInt(goods_count)
        update_remote_cart_info(goods_id, goods_count)
        // 根据更新的结果进行操作
        if (error_update == false){
            // 更新成功,设置商品的购买数目
            $(this).prev().val(goods_count)
            // 获取商品对应的checkbox的选中状态
            is_checked = $(this).parents('ul').find(':checkbox').prop('checked')
            if (is_checked){
                // 更新订单商品的总数目，总金额，商品小计
                update_total_price()
            }
            else{
                // 设置回输入之前的值
                $(this).val(pre_goods_count)
            }
        }
    })
    // 购物车商品信息的删除
    $('.cart_list_td').children('.col08').children('a').click(function () {
        // 获取删除用户的商品的id
        goods_ul = $(this).parents('ul')
        goods_id = goods_ul.find('.num_show').attr('goods_id')
        csrf = $('input[name="csrfmiddlewaretoken"]').val()
        params = {'goods_id': goods_id,
                'csrfmiddlewaretoken': csrf}
        // 发起ajax请求
        $.post('/cart/delete/', params, function (data) {
            if (data.res == 3){
                // 商品删除成功
                // 移除商品对应的ul元素
                goods_ul.remove()
                // 判断商品对应的checkbox是否被选中
                is_checked = goods_ul.find(':checkbox').prop('checked')
                if (is_checked){
                    update_total_price()
                }
                // 更新页面购物车商品总数
                $(".total_count").html(data.goods_type_count)
            }

        })

    })







})




