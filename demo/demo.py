# -*- coding: utf-8 -*-
from flask import Flask,render_template,request,abort,jsonify
from ApacheConfigParser.ApacheConfig import ApacheParser
import json
app = Flask(__name__)

#----------------API后端----------------------
#GET请求后端示例，实现读取文件内容功能
@app.route('/api/readfile/')
def readfile():
    with open('ApacheConfigParser/examples/test_apache_config.conf','r') as f:
        text=f.read()
    result='读取到的文件内容:\n'+text
    return result

#POST请求后端示例，实现修改ServerName功能
@app.route('/api/change/',methods=['POST'])
def change():
    name=request.form['name'] #name为收到的参数
    with open('ApacheConfigParser/examples/test_apache_config.conf','rb') as f:
        parsed = ApacheParser(f) #调用ApacheConfigParser解析文件,注意使用rb模式读取文件
    result='要修改为的ServerName:'+name+'\n'
    result+='============修改前的内容============\n'
    result+=parsed.render().decode('utf-8')
    #修改ServerName
    parsed.findAll('VirtualHost').findChildren('ServerName').update(name)
    result+='============修改后的内容============\n'
    result+=parsed.render().decode('utf-8')
    return result

#传输json数据后端示例
@app.route('/api/transferjson/',methods=['POST'])
def transferjson():
    data=request.json #前端发来的json数据
    result={
        '后端接收到的数据':data,
        '后端框架':'Flask'
    }
    return jsonify(result) #后端传回json数据

#持久化存储后端示例，实现在settings.json文件中保存和读取数据功能
@app.route('/api/savedata/',methods=['POST'])
def savedata():
    data=request.json #前端发来的数据
    #写文件
    with open('settings.json','w') as f:
        f.write(json.dumps(data,ensure_ascii=False,indent=2))
    return '保存到settings.json成功'

@app.route('/api/loaddata/')
def loaddata():
    #读文件
    with open('settings.json', 'r') as f:
        data = json.load(f)
    return jsonify(data) #后端传回的数据
#----------------页面----------------------
#homepage
@app.route('/')
def index():
    return render_template('index.html')
#aboutpage
@app.route('/about')
def about():
    return render_template('about.html')
#contactpage
@app.route('/contact')
def contact():
    return render_template('contact.html')
#----------------启动服务器----------------------
if __name__ == '__main__':
    app.run(debug=True) #开启debug模式后修改文件内容能够自动重启服务器
