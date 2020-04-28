function getCookie(name) {
    var r = document.cookie.match("\\b" + name + "=([^;]*)\\b");
    return r ? r[1] : undefined;
}

function logout() {
    $.ajax({
        url: "/api/v1.0/session",
        type: "delete",
        headers: {
             "X-CSRFToken":  getCookie("csrf_token")//csrf_token放到请求头中，方便后端进行验证
        },
        success: function (resp){
            if(resp.error == "0"){
                //退出成功
                location.href = "/index.html";
            }
        }
    });
}

$(document).ready(function(){

})