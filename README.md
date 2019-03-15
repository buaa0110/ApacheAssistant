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

- 比较本地和远程分支的差异

```
#比较本地和远程分支相差的commit
git fetch origin
git log master..origin/master

#比较本地和远程分支文件内容的改动
git fetch origin
git diff --stat master origin/master	#查看所有文件各修改了多少行
git diff master origin/master			#查看所有文件的具体内容改动
git diff master origin/master README.md	#查看某个文件的具体内容改动
```

### 关于华为云和github的协同管理问题

由于课程要求我们将代码托管交付华为云，因此有必要在华为云上维护相同的项目，处于节省时间和精力的考虑，现发布本项目在Git和华为云的协同方式

本质上，依然使用Git管理，区别在于，项目人员需要在本地仓库维护一个华为云的远程仓库

首先，请各位注意，确保自己在华为云上已经设置好了个人的ssh密钥和https密钥，相关步骤可以在华为云代码托管页面找到

完成密钥设置后，首先运行

    git remote add remoteName [URL]

+ 说明： remoteName可以自行指定

然后，按照正常的操作行为规范进行github项目的维护，例如push和pull，只是需要每次在git进行一次push之后，运行以下命令

    git push remoteName

+ 说明：此处的remoteName为项目组人员在上一步所设置


