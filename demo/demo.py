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
import psutil
import subprocess

app = Flask(__name__)

line_parser = apache_log_parser.make_parser("%h %l %u %t \"%r\" %>s %b")

#----------------API后端----------------------
"""
全局工具
"""
#上一次请求的网络数据初始值
last_network_data=-1
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

#获取apache的pid
def get_apache_pid(pid_path):
    if os.path.exists(pid_path):
        with open('C:/Apache24/logs/httpd.pid') as f:
            pid=int(f.read())
        if psutil.pid_exists(pid):
            return pid
        else:
            return -1
    else:
        return -1

#获取所有模块信息
def get_module_info():
    modules={}
    #从文件中读取所有动态模块的信息
    with open('modules_list.txt','r') as f:
        for line in f:
            attributes=line.strip().split(' ')
            if len(attributes)==2:
                #获取属性
                name=attributes[0]
                path=attributes[1]
                #添加属性
                modules[name]={}
                modules[name]['path']=path
                modules[name]['type']='shared'
                modules[name]['status']='uninstalled'
                #将某些模块标记为不可卸载
                if name in ['authz_core_module','log_config_module','autoindex_module','dir_module']:
                    modules[name]['type']='static'
    #读取apache的现有模块
    proc = subprocess.run([storage['httpd_path'],'-M'],stdout=subprocess.PIPE)
    exist_modules_textlist=proc.stdout.decode('utf-8').split('\n')
    for index in range(len(exist_modules_textlist)):
        if index==0: #去掉首行
            continue
        #解析模块的名称和类型
        text=exist_modules_textlist[index].strip()
        attributes=text.split(' ')
        if len(attributes)==2:
            name=attributes[0]
            module_type=attributes[1]
            if module_type=='(static)': #静态模块
                modules[name]={}
                modules[name]['type']='static'
                modules[name]['status']='installed'
            else: #动态模块
                modules[name]['status']='installed'
    return modules

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
    print(request)
    print(data)
    path=data['path']
    print(path)
    #检查路径是否存在
    if os.path.exists(path):
        #保存并返回成功信息
        storage['config_path']=path
        print("success")
        return success('保存成功')
    else:
        #返回错误信息
        print("fail")
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
@app.route('/api/filter_log_text/',methods=['POST'])
def filter_log_text():
    data = request.json
    key_list = list(data.keys())
    #检查是否已保存日志文件路径
    if 'log_path' not in storage:
        return error('日志文件路径未保存')
    path = storage['log_path']
    #检查日志文件是否存在
    if not os.path.exists(path):
        return error('日志文件不存在')
    #读取并解析日志文件 
    with open(path,'r') as f:
        log_text = f.read()
    log_text_list = log_text.split('\n')
    log_json=[]
    for item in log_text_list:
        try: #去除空行等情况
            log_line_data = line_parser(item)
        except:
            continue
        line={}
        line['remote_host'] = log_line_data['remote_host']
        line['request_method'] = log_line_data['request_method']
        line['request_url'] = log_line_data['request_url']
        line['status'] = log_line_data['status']
        line['time_received'] = log_line_data['time_received']
        line['text']=item
        log_json.append(line)
    filter_text = []
    for item in log_json:
        match_flag = True
        for key in key_list:
            if item[key]!=data[key]:
                match_flag = False
        if match_flag == True:
            filter_text.append(item['text']) #仅返回日志文本

    return jsonify(filter_text)

"""
 性能监控
"""

#保存Apache目录路径
@app.route('/api/save_apache_path/',methods=['POST'])
def save_apache_path():
    #接收前端发来的json数据
    data=request.json
    path=data['path']
    #检查路径是否存在
    if os.path.exists(path):
        if os.path.exists(os.path.join(path,'bin/httpd.exe')):
            storage['apache_path']=path
            storage['httpd_path']=os.path.join(path,'bin/httpd.exe')
            storage['pid_path']=os.path.join(path,'logs/httpd.pid')
            return success('保存成功')
        else:
            return error('Apache目录中没有httpd.exe，请确认已安装Apache并设置正确的Apache目录')
    else:
        #返回错误信息
        return error('目录路径不存在')

#读取保存的Apache目录路径
@app.route('/api/load_apache_path/',methods=['GET'])
def load_apache_path():
    #检查是否已保存Apache目录路径
    if 'apache_path' in storage:
        #返回已保存的Apache目录路径
        result={'path':storage['apache_path']}
        return jsonify(result)
    else:
        #返回错误信息
        return error('Apache目录路径未保存')

#查看apache系统状态(running/stop)
@app.route('/api/apache_status/',methods=['GET'])
def apache_status():
    #检查是否已保存Apache目录路径
    if 'apache_path' not in storage:
        return error('Apache目录路径未保存')
    elif not os.path.exists(storage['httpd_path']):
        return error('Apache目录中没有httpd.exe，请确认已安装Apache并设置正确的Apache目录')
    #获取pid
    httpd_pid=get_apache_pid(storage['pid_path'])
    #判断是否正在运行
    if httpd_pid>=0:
        status='running'
    else:
        status='stop'
    #返回结果
    return jsonify({'status':status})

#改变apache系统状态
@app.route('/api/control_apache/',methods=['POST'])
def control_apache():
    #检查是否已保存Apache目录路径
    if 'apache_path' not in storage:
        return error('Apache目录路径未保存')
    elif not os.path.exists(storage['httpd_path']):
        return error('Apache目录中没有httpd.exe，请确认已安装Apache并设置正确的Apache目录')
    #接收前端发来的json数据
    data=request.json
    command=data['command']
    #检查命令是否正确
    if command in ['stop','start','restart']:
        proc=subprocess.run([storage['httpd_path'],'-k',command],stdout=subprocess.PIPE)
        print(proc.stdout)
        return success('操作成功')
    else:
        #返回错误信息
        return error('命令有误,应为stop/start/restart')
    
#查看apache的性能参数
@app.route('/api/apache_params/',methods=['GET'])
def apache_params():
    #检查是否已保存Apache目录路径
    if 'apache_path' not in storage:
        return error('Apache目录路径未保存')
    elif not os.path.exists(storage['httpd_path']):
        return error('Apache目录中没有httpd.exe，请确认已安装Apache并设置正确的Apache目录')
    #获取pid
    httpd_pid=get_apache_pid(storage['pid_path'])
    result={}
    #判断是否正在运行
    if httpd_pid>=0: #正在运行
        p=psutil.Process(httpd_pid)
        #CPU占用，数值范围0~100，可以直接在后面加百分号
        result['cpu_percent']=p.cpu_percent()
        #内存占用，数值范围0~100，可以直接在后面加百分号
        result['memory_percent']=p.memory_percent()
        #连接数，非负整数
        result['connections']=len(p.connections())
        #与上一次网络传输量的差值，单位为MB
        global last_network_data
        new_network_data = psutil.net_io_counters().bytes_sent + psutil.net_io_counters().bytes_recv
        new_network_data=round(new_network_data/1024.0/1024.0,2)
        if last_network_data<0: #第一次请求
            network_data=0
        else: #后面的请求
            network_data=new_network_data-last_network_data
        #更新上一次请求的值
        last_network_data=new_network_data
        if network_data<0.2: #避免负值
            network_data=0
        # print('new:',new_network_data,'last',last_network_data,'diff',network_data)
        result['network_data']=network_data
    else: #已停止
        result['cpu_percent']=0.0
        result['memory_percent']=0.0
        result['connections']=0
        result['network_data']=0
    #返回结果
    return jsonify(result)

"""
 模块管理
"""

#获得模块列表
@app.route('/api/modules_list/',methods=['GET'])
def modules_list():
    #检查是否已保存Apache目录路径
    if 'apache_path' not in storage:
        return error('Apache目录路径未保存')
    elif not os.path.exists(storage['httpd_path']):
        return error('Apache目录中没有httpd.exe，请确认已安装Apache并设置正确的Apache目录')
    #获取模块信息
    modules=get_module_info()
    #生成列表
    static_list=[]
    shared_list=[]
    for name in modules:
        if modules[name]['type']=='static':
            static_list.append({'name':name})
        else:
            shared_list.append({'name':name,'status':modules[name]['status'],'path':modules[name]['path']})
    result={'static_list':static_list,'shared_list':shared_list}
    #返回结果
    return jsonify(result)

#安装模块
@app.route('/api/install_module/',methods=['POST'])
def install_module():
    #检查是否已保存Apache目录路径
    if 'apache_path' not in storage:
        return error('Apache目录路径未保存')
    elif not os.path.exists(storage['httpd_path']):
        return error('Apache目录中没有httpd.exe，请确认已安装Apache并设置正确的Apache目录')
    #接收前端发来的json数据
    data=request.json
    name=data['name']
    #获取模块信息
    modules=get_module_info()
    if name not in modules:
        return error('模块名称有误')
    else:
        module=modules[name]
        #安装模块
        #读取配置文件文本
        with open(storage['config_path'],'r') as f:
            config_text=f.read()

        #修改配置项
        config_text= re.sub('#+\s*LoadModule\s+'+name+'\s+'+module['path'],'LoadModule '+name+' '+module['path'], config_text)

        #保存文件内容
        with open(storage['config_path'],'w') as f:
            f.write(config_text)
        
        #重新启动apache
        subprocess.run([storage['httpd_path'],'-k','restart'],stdout=subprocess.PIPE)

        return success('操作成功')

#卸载模块
@app.route('/api/remove_module/',methods=['POST'])
def remove_module():
    #检查是否已保存Apache目录路径
    if 'apache_path' not in storage:
        return error('Apache目录路径未保存')
    elif not os.path.exists(storage['httpd_path']):
        return error('Apache目录中没有httpd.exe，请确认已安装Apache并设置正确的Apache目录')
    #接收前端发来的json数据
    data=request.json
    name=data['name']
    #获取模块信息
    modules=get_module_info()
    if name not in modules:
        return error('模块名称有误')
    else:
        module=modules[name]
        if module['type']=='static':
            return error('模块'+name+'是静态模块，不可卸载')
        else:
            #安装模块
            #读取配置文件文本
            with open(storage['config_path'],'r') as f:
                config_text=f.read()

            #修改配置项
            config_text= re.sub('#*LoadModule\s+'+name+'\s+'+module['path'],'#LoadModule '+name+' '+module['path'], config_text)

            #保存文件内容
            with open(storage['config_path'],'w') as f:
                f.write(config_text)
            
            #重新启动apache
            subprocess.run([storage['httpd_path'],'-k','restart'],stdout=subprocess.PIPE)

            return success('操作成功')

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
