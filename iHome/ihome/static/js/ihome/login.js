function getCookie(name) {
    var r = document.cookie.match("\\b" + name + "=([^;]*)\\b");
    return r ? r[1] : undefined;
}

$(document).ready(function() {
    $("#mobile").focus(function(){
        $("#mobile-err").hide();
    });
    $("#password").focus(function(){
        $("#password-err").hide();
    });
    $(".form-login").submit(function(e){
        e.preventDefault();
        mobile = $("#mobile").val();
        passwd = $("#password").val();
        if (!mobile) {
            $("#mobile-err span").html("请填写正确的手机号！");
            $("#mobile-err").show();
            return;
        } 
        if (!passwd) {
            $("#password-err span").html("请填写密码!");
            $("#password-err").show();
            return;
        }

        // 返回的数据（手机号，密码）
        req_dict = {
            mobile: mobile,
            password: passwd
        }
        //转换成json
        req_json = JSON.stringify(req_dict)
        $.ajax({
            url: "/api/v1.0/login",
            type: "post",
            data: req_json,
            contentType: "application/json",
            dataType: "json",
            headers: {
                "X-CSRFToken":  getCookie("csrf_token") //csrf_token放到请求头中，方便后端进行验证
            },
            success: function (resp){
                if(resp.error == "0"){
                    //登录成功
                    location.href = "/index.html";
                }else{
                    alert(resp.errmsg)
                }
            }
        })
    });
})