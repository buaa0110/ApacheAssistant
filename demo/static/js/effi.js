// this part need to give some functions to
// make page effi update its different charts and
// button state and so on

function updateCpu(){
  $('#cpuOcc').click(function () {
        //发送POST请求,与后端双向传输json数据
        $.ajax({
            url: '/api/',
            data:{},
            type: 'get',
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
            url: '/api/savedata/',
            data: JSON.stringify({ 'savetext': $('#savetext').val() }),
            type: 'get',
            contentType: 'application/json;charset=utf-8',
            success: function (data) {
                //显示结果
                cpuChart.segment.value = data['cpu'];
                cpuChart.update();
            }
        })
    })
}

function updateSpeed(){
  $('#netSpeed').click(function () {
        //发送POST请求,与后端双向传输json数据
        $.ajax({
            url: '/api/savedata/',
            data: JSON.stringify({ 'savetext': $('#savetext').val() }),
            type: 'get',
            contentType: 'application/json;charset=utf-8',
            success: function (data) {
                //显示结果
                cpuChart.segment.value = data['cpu'];
                cpuChart.update();
            }
        })
    })
}

function changeState(){
  $('#cpuOcc').click(function () {
        //发送POST请求,与后端双向传输json数据
        $.ajax({
            url: '/api/savedata/',
            data: JSON.stringify({ 'savetext': $('#savetext').val() }),
            type: 'get',
            contentType: 'application/json;charset=utf-8',
            success: function (data) {
                //显示结果
                cpuChart.segment.value = data['cpu'];
                cpuChart.update();
            }
        })
    })
}

function toSeeState(){
  $('#cpuOcc').click(function () {
        //发送POST请求,与后端双向传输json数据
        $.ajax({
            url: '/api/savedata/',
            data: JSON.stringify({ 'savetext': $('#savetext').val() }),
            type: 'get',
            contentType: 'application/json;charset=utf-8',
            success: function (data) {
                //显示结果
                cpuChart.segment.value = data['cpu'];
                cpuChart.update();
            }
        })
    })
}
