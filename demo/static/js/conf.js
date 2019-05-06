// this part need to give some functions to
// make page conf update its different charts and
// button state and so on

function getConfPath(){
  $('#getConfPathButton').click(function () {
        //发送POST请求,与后端双向传输json数据
        $.ajax({
            url: '/api/',
            data:{},
            type: 'GET',
            contentType: 'application/json;charset=utf-8',
            success: function (data) {
                //显示结果
                $('#confPathLabel').val = data['confPath'];
            },
            error:function(data){
              alert("data")
            }
        })
    })
}
function updateConfPath(){
  $('#updateConfPathButton').click(function(){
    data = $('#confPathText').val();
    $.ajax({
      url:'/api/',
      data:data,
      type:'POST',
      contentType:'application/json;charset=utf-8',
      success:function(){
        //need to finish
        $('#')
      },
      error:function(data){
        alert(data);
      }
    })
  })
}
