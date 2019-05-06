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
      success:function(data){
        //need to finish
        $('#confPathLabel').val = data['confPath'];
        console.log("update conf path successfully!");
      },
      error:function(data){
        alert(data);
      }
    })
  })
}
function getConfInfo1(){
  $('#getConfInfo1').click(function () {
        //发送POST请求,与后端双向传输json数据
        $.ajax({
            url: '/api/',
            data:{},
            type: 'GET',
            contentType: 'application/json;charset=utf-8',
            success: function (data) {
                //显示结果
                $('#confInfo1').val = data['confInfo1'];
                console.log("get confinfo1 successfully!");
            },
            error:function(data){
              alert("data")
            }
        })
    })
}

function getConfInfo2(){
  $('#getConfInfo2').click(function () {
        //发送POST请求,与后端双向传输json数据
        $.ajax({
            url: '/api/',
            data:{},
            type: 'GET',
            contentType: 'application/json;charset=utf-8',
            success: function (data) {
                //显示结果
                $('#confInfo2').val = data['confInfo2'];
                console.log("get confinfo2 successfully!");
            },
            error:function(data){
              alert("data")
            }
        })
    })
}
function getConfInfo3(){
  $('#getConfInfo3').click(function () {
        //发送POST请求,与后端双向传输json数据
        $.ajax({
            url: '/api/',
            data:{},
            type: 'GET',
            contentType: 'application/json;charset=utf-8',
            success: function (data) {
                //显示结果
                $('#confInfo3').val = data['confInfo3'];
                console.log("get confinfo3 successfully!");
            },
            error:function(data){
              alert("data")
            }
        })
    })
}
function updateConfInfo1(){
  $('#updateConfInfo1').click(function(){
    data = $('confInfoText1').val();
    $.ajax({
      url:'/api/',
      data:data,
      type:"POST",
      contentType:'application/json;charset=utf-8',
      success:function(data){
        $('#confInfoText1').val = data['confInfoText1'];
        console.log("update conf info 1 successfully!");
      },
      error:function(data){
        alert(data);
      }
    })
  })
}
function updateConfInfo2(){
  $('#updateConfInfo2').click(function(){
    data = $('confInfoText2').val();
    $.ajax({
      url:'/api/',
      data:data,
      type:"POST",
      contentType:'application/json;charset=utf-8',
      success:function(data){
        $('#confInfoText2').val = data['confInfoText2'];
        console.log("update conf info 2 successfully!");
      },
      error:function(data){
        alert(data);
      }
    })
  })
}
function updateConfInfo3(){
  $('#updateConfInfo3').click(function(){
    data = $('confInfoText3').val();
    $.ajax({
      url:'/api/',
      data:data,
      type:"POST",
      contentType:'application/json;charset=utf-8',
      success:function(data){
        $('#confInfoText3').val = data['confInfoText3'];
        console.log("update conf info 3 successfully!");
      },
      error:function(data){
        alert(data);
      }
    })
  })
}
