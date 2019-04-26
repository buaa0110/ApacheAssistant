# -*- coding: utf-8 -*-
from flask import Flask,render_template,request,abort,jsonify
import re
import json
from sqlitedict import SqliteDict
import os
import apache_log_parser
import shutil
import apache_log_parser
from pprint import pprint
from apacheconfig import *
app = Flask(__name__)

line_parser = apache_log_parser.make_parser("%h %l %u %t \"%r\" %>s %b")

#----------------API后端----------------------
"""
全局工具
"""
#持久化存储数据库，修改storage会自动保存
storage = SqliteDict('./database.sqlite', autocommit=True)

#解析配置文件
def parse_config():
    options = {
        'useapacheinclude':False,
        'namedblock': False,
        'noescape':True
    }
    with make_loader(**options) as loader:
        config = loader.load(storage['config_path'])

    #返回特定的配置项
    result={}
    #配置项含义
    # Listen 监听端口(数值)
    result['Listen']=config['Listen']
    # DocumentRoot 网页目录位置(文件夹路径字符串)
    result['DocumentRoot']=config['DocumentRoot']
    # Keep Alive开关(On/Off)
    result['KeepAlive']=config['KeepAlive']
    # Keep Alive超时时间(数值)
    result['KeepAliveTimeout']=config['KeepAliveTimeout']
    # MaxKeepAliveRequests 最大连接数(数值)
    result['MaxKeepAliveRequests']=config['MaxKeepAliveRequests']
    # LogFormat 日志记录格式(字符串)
    for obj in config['IfModule']:
        if 'log_config_module' in obj:
            log_module=obj
    result['LogFormat']=log_module['log_config_module']['LogFormat']

    return result

#返回成功信息
def success(info):
    return jsonify({'info':info})

#返回错误信息,HTTP 400 Bad Request
def error(info):
    return jsonify({'error':info}),400

#查看所有保存的信息
@app.route('/api/load_all_settings/',methods=['GET'])
def load_all_settings():
    result={}
    for key, value in storage.iteritems():
        result[key]=value
    return jsonify(result)

"""
配置管理
"""
#保存Apache配置文件路径
@app.route('/api/save_config_path/',methods=['POST'])
def save_config_path():
    #接收前端发来的json数据
    data=request.json
    path=data['path']

    #检查路径是否存在
    if os.path.exists(path):
        #保存并返回成功信息
        storage['config_path']=path
        return success('保存成功')
    else:
        #返回错误信息
        return error('路径不存在')

#读取保存的Apache配置文件路径
@app.route('/api/load_config_path/',methods=['GET'])
def load_config_path():
    #检查是否已保存配置文件路径
    if 'config_path' in storage:
        #返回已保存的配置文件路径
        result={'path':storage['config_path']}
        return jsonify(result)
    else:
        #返回错误信息
        return error('配置文件路径未保存')

#读取解析好的Apahce配置文件信息
@app.route('/api/load_config/',methods=['GET'])
def load_config():
    #解析配置文件
    result=parse_config()
    #返回解析的信息
    return jsonify(result)

#修改配置文件(前端仅发送要修改的项)
@app.route('/api/save_config/',methods=['POST'])
def save_config():
    #接收前端发来的json数据
    data=request.json

    #解析配置文件
    config=parse_config()
    #读取配置文件文本
    with open(storage['config_path'],'r') as f:
        config_text=f.read()

    #修改配置项
    for key in data:
        if key not in config:
            return error('配置项'+key+'不在配置文件中')
        old=config[key]
        new=data[key]
        config_text= re.sub(key+'\s+'+old,key+' '+new, config_text)

    #保存文件内容并返回成功信息
    with open(storage['config_path'],'w') as f:
        f.write(config_text)
    return success('保存成功')


"""
 日志管理
"""

#保存Apache日志文件路径/api/save_log_path/
@app.route('/api/save_log_path/', methods=['POST'])
def save_log_path():
    #接收前端发来的json数据
    data = request.json
    path = data['path']

    #检查路径是否存在
    if os.path.exists(path):
        #保存并返回保存成功信息
        storage['log_path'] = path
        return success('保存成功')
    else:
        #返回错误信息
        return error('路径不存在')


#读取保存的Apache日志文件路径
@app.route('/api/load_log_path/',methods=['GET'])
def load_log_path():
    #检查是否已经保存日志文件路径
    if 'log_path' in storage:
        #返回已保存的日志文件路径
        result = {'path':storage['log_path']}
        return jsonify(result)
    else:
        #返回错误信息
        return error('日志文件路径未保存')

#读取Apahce日志文件并解析
@app.route('/api/load_log_text/',methods=['GET'])
def load_log_text():
    if 'log_path' in storage:
        path = storage['log_path']
        if os.path.exists(path):
            with open(path,'r') as f:
                log_text = f.read()
            log_text_list = log_text.split('\n')
            line={}
            log_json=[]
            for item in log_text_list:
                log_line_data = line_parser(item)
                line['remote_host'] = log_line_data['remote_host']
                line['request_method'] = log_line_data['request_method']
                line['request_url'] = log_line_data['request_url']
                line['status'] = log_line_data['status']
                line['time_received'] = log_line_data['time_received']
                log_json.append(line)
            storage['log_text'] = log_json
            return success('读取日志文件成功')
        else:
            return error('日志文件路径不存在')
    else:
        return error('日志文件路径未保存')

#清除日志文件内容
@app.route('/api/clear_log_text/',methods=['POST'])
def clear_log_text():
    if 'log_path' in storage:
        path = storage['log_path']
        if os.path.exists(path):
            with open(path,'w') as f:
                f.write("")
            return success('清除成功')
        else:
            return error('日志文件路径不存在')
    else:
        return error('日志文件路径未保存')

#备份日志文件内容
@app.route('/api/backup_log_text/',methods=['POST'])
def backup_log_text():
    if 'log_path' in storage:
        path = storage['log_path']
        backup_path = path+"_backup"
        if os.path.exists(path):
            shutil.copyfile(path,backup_path)
            return success('备份成功')
        else:
            return error('日志文件路径不存在')
    else:
        return error('日志文件路径未保存')

#筛选日志内容字段
@app.route('/api/filter_log_text/',methods=['GET'])
def filter_log_text():
    data = request.json
    key_list = list(data.keys())
    log_text = storage['log_text']
    filter_text = []
    for item in log_text:
        match_flag = True
        for key in key_list:
            if item[key]!=data[key]:
                match_flag = False
        if match_flag == True:
            filter_text.append(item)

    storage['filter_text'] = filter_text
    return success("筛选成功")





#----------------页面----------------------
#homepage主页
@app.route('/')
def index():
    return render_template('index.html')
#aboutpage关于我们
@app.route('/about')
def about():
    return render_template('about.html')
#contactpage联系我们
@app.route('/contact')
def contact():
    return render_template('contact.html')
# 应用介绍
@app.route('/introduction')
def introduction():
    return render_template('introduction.html')
# 使用说明
@app.route('/introduction/usecase')
def usecase():
    return render_template("usecase.html")
#功能介绍
@app.route('/introduction/function')
def function():
    return render_template("function.html")
#具体功能
@app.route('/func')
def func():
    return render_template("func.html")
#配置管理
@app.route('/func/conf')
def conf():
    return render_template("conf.html")
# 性能监控
@app.route('/func/effi')
def effi():
    return render_template("effi.html")
#日志管理
@app.route('/func/path')
def path():
    return render_template("path.html")
#模块管理
@app.route('/func/module')
def module():
    return render_template("module.html")

#----------------启动服务器----------------------
if __name__ == '__main__':
    app.run(debug=True) #开启debug模式后修改文件内容能够自动重启服务器
