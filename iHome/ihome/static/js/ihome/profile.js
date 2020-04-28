function showSuccessMsg() {
    $('.popup_con').fadeIn('fast', function() {
        setTimeout(function(){
            $('.popup_con').fadeOut('fast',function(){}); 
        },1000) 
    });
}

function getCookie(name) {
    var r = document.cookie.match("\\b" + name + "=([^;]*)\\b");
    return r ? r[1] : undefined;
}

$(document).ready(function (){
    $("#form-avatar").submit(function (e){
        //阻止默认行为
        e.preventDefault();
        // 利用jquery.form.min.js库中的ajaxSubmit对表单进行异步提交
        $(this).ajaxSubmit({
            url: "/api/v1.0/user/avatar",
            type: "post",
            dataType: "json",
            headers: {
                 "X-CSRFToken":  getCookie("csrf_token")//csrf_token放到请求头中，方便后端进行验证
            },
            success: function (resp){
                if(resp.error == "0"){
                    //上传成功
                    var avatar_url = resp.data.avatar_url;
                    $("#user-avatar").attr("src", avatar_url)
                }
                else{
                    alert(resp.errmsg)
                }
            }
        })
    })
})
