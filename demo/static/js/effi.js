// this part need to give some functions to
// make page effi update its different charts and
// button state and so on

function updateCpu(){
  $('#cpuOcc').click(function () {
        //发送POST请求,与后端双向传输json数据
        $.ajax({
            url: '/api/',
            data:{},
            type: 'GET',
            contentType: 'application/json;charset=utf-8',
            success: function (data) {
                //显示结果
                cpuChart.segment.value = data['cpu'];
                cpuChart.update();
            }
        })
    })
}

function updateRam(){
  $('#ramOcc').click(function () {
        //发送POST请求,与后端双向传输json数据
        $.ajax({
            url: '/api/',
            data: {},
            type: 'GET',
            contentType: 'application/json;charset=utf-8',
            success: function (data) {
                //显示结果
                ramChart.segment.value = data['ram'];
                ramChart.update();
            }
        })
    })
}

function updateSpeed(){
  $('#netSpeed').click(function () {
        //发送POST请求,与后端双向传输json数据
        $.ajax({
            url: '/api/',
            data: {},
            type: 'GET',
            contentType: 'application/json;charset=utf-8',
            success: function (data) {
                //显示结果
                netSpeedChart.segment.value = data['cpu'];
                netSpeedChart.update();
            }
        })
    })
}

function changeState(){
  $('#changeButton').click(function () {
        //发送POST请求,与后端双向传输json数据
        $.ajax({
            url: '/api/',
            data: JSON.stringify({ 'curState': $('#stateButton').val() }),
            type: 'POST',
            contentType: 'application/json;charset=utf-8',
            success: function (data) {
                //显示结果
                $("#stateButton").val(data['state'])
            }
        })
    })
}

function toSeeState(){
  $('#stateButton').click(function () {
        //发送get请求,与后端请求当前服务器状态
        $.ajax({
            url: '/api/',
            data: {},
            type: 'GET',
            contentType: 'application/json;charset=utf-8',
            success: function (data) {
                //显示结果
                $("#stateButton").val(data['state'])
            }
        })
    })
}

function restart(){
  $('#restartButton').click(function () {
        //发送get请求,与后端请求当前服务器状态
        $.ajax({
            url: '/api/',
            data: JSON.stringify({ 'restart': "true"}),
            type: 'POST',
            contentType: 'application/json;charset=utf-8',
            success: function (data) {
                //显示结果
                if(data['result'] == "success"){
                  alert("restart successfully!");
                }
                else{
                  alert("restart failed!");
                }
            }
        })
    })
}
