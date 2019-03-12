# ApacheAssistant
software experiment of buaa

## 项目git管理说明

+ 初次参与

本项目目前采用git进行管理，参与者初次使用

    git clone  https://github.com/buaa0110/ApacheAssistant.git

命令克隆本项目至本地开发环境

+ 提交

当开发者需要提交新的修改时，应依次使用以下命令

    git add .
    git commit -m "提交信息"
    git push

+ 合并修改

当开发者本地进行了修改而尚未确定origin是否有修改或者确定origin已存在修改时，请使用

    git stash
    git pull
    git stash pop

命令将本地修改与origin变化合并后在进行提交
