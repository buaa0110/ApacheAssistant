# ApacheAssistant demo

## 安装及运行

首先安装Python 3.5及以上版本，然后安装flask等依赖库

```
pip install flask apacheconfig apache_log_parser psutil sqlitedict
```

进入demo.py所在目录，执行

```
python demo.py
```

在浏览器中输入127.0.0.1:5000即可看到页面

## 后端开发进度

### API版本：V0.2

- /api/save_config/ 修改配置文件API修改为前端仅发送要修改的项
- 增加/api/load_all_settings/ 查看所有保存的信息（如配置文件路径等）API，用于读取database.sqlite文件，仅用于debug

### API实现进度

#### 配置管理

- [x] /api/save_config_path/	保存Apache配置文件路径
- [x] /api/load_config_path/	读取保存的Apache配置文件路径
- [x] /api/load_config/	读取解析好的Apahce配置文件信息
- [x] /api/save_config/	修改配置文件（前端仅发送要修改的项）

#### 日志管理

- [ ] /api/save_log_path/	保存Apache日志文件路径
- [ ] /api/load_log_path/	读取保存的Apache日志文件路径
- [ ] /api/load_log_text/	读取Apahce日志文件文本
- [ ] /api/save_log_text/	保存修改过的Apahce日志文件文本

#### 性能监控

- [ ] /api/apache_status/	查看apache系统状态(running/stop)
- [ ] /api/control_apache/	改变apache系统状态(stop/start/restart)
- [ ] /api/apache_params/	查看apache的性能参数

#### 模块管理

- [ ] /api/modules_list/	获得模块列表
- [ ] /api/install_module/	安装模块
- [ ] /api/remove_module/	卸载模块

#### 全局工具

- [x] /api/load_all_settings	查看所有保存的信息

## 使用的框架

- 后端框架

  Flask（使用Python编写的轻量级Web框架），参考教程：http://docs.jinkan.org/docs/flask/index.html

- 前端框架

  jQuery（快速、简洁的JavaScript框架），参考教程：http://www.runoob.com/jquery/jquery-tutorial.html

  Semantic-UI（简单、美观的CSS框架），官方网站：https://semantic-ui.com/


## 功能实现

#### 以读取文件内容为例

1. 用户点击<读取文件内容>按钮

2. 前端向后端/api/readfile/发出GET请求，具体代码如下：

   ```javascript
   //templates/index.html文件
   //<读取文件内容>按钮
   $('#readfile').click(function () {
       //发送GET请求
       $.get('/api/readfile/', function (data) {
           //显示结果
           $('#result').text(data)
           $('#result').html($('#result').html().replace(/\n/g, '<br/>'))
       })
   })
   ```

3. 后端收到请求，读取本机上指定位置的文件，然后将文件内容传输给前端，具体代码如下：

   ```python
   #demo.py文件
   #GET请求后端示例，实现读取文件内容功能
   @app.route('/api/readfile/')
   def readfile():
       with open('ApacheConfigParser/examples/test_apache_config.conf','r') as f:
           text=f.read()
       result='读取到的文件内容:\n'+text
       return result
   ```

4. 前端收到内容后在页面中显示文件内容

   ![](readme_image/demo2.png)

## 文件结构

与项目相关的文件和文件夹有：

| 文件或文件夹    | 功能                                                   |
| --------------- | ------------------------------------------------------ |
| demo.py         | 后端入口                                               |
| settings.json   | 持久化存储内容的文件                                   |
| static/         | 前端js、css文件存储位置                                |
| templates/      | 前端页面html文件存储位置                               |
| example_config/ | 配置文件示例httpd.conf和日志文件示例access.log存储位置 |