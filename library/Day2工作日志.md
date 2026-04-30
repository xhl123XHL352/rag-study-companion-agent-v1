**完成昨日任务流程规划**



Windows 下建议你直接执行

先进入项目根目录：



cd "C:\\Users\\creat\\Downloads\\Edit-Banana-main\\Edit-Banana-main"

然后执行：



git clone https://github.com/facebookresearch/sam3.git sam3\_src

克隆完后执行：



pip install -e .\\sam3\_src

安装完后验证

执行：



python -c "from sam3.model\_builder import build\_sam3\_image\_model; from sam3.model.sam3\_image\_processor import Sam3Processor; print('OK')"

如果输出：



OK

就说明 sam3 库安装成功了。



然后再跑你的命令

再回到项目根目录运行：



python -m icon\_extractor.cli "input/test.png" -o "./icon\_output"



**！！！最后一步报错：缺triton等包，貌似只能在Linux上面跑**



### **解决方案（暂拟）：**

用自己电脑本地的WSL镜像：



一、进入 WSL

在 Windows 终端里输入：



wsl

或者直接打开 Ubuntu 应用。



二、找到你的 Windows 项目目录

你 Windows 上的目录：



C:\\Users\\creat\\Downloads\\Edit-Banana-main\\Edit-Banana-main

在 WSL 里会变成：



/mnt/c/Users/creat/Downloads/Edit-Banana-main/Edit-Banana-main

你可以进入：



cd /mnt/c/Users/creat/Downloads/Edit-Banana-main/Edit-Banana-main

三、先装基础环境

在 WSL Ubuntu 里执行：



sudo apt update

sudo apt install -y python3 python3-venv python3-pip git

如果要 OCR：



sudo apt install -y tesseract-ocr tesseract-ocr-chi-sim

四、创建虚拟环境

在项目目录里：



python3 -m venv .venv

source .venv/bin/activate

升级一下：



pip install -U pip setuptools wheel

五、安装 PyTorch

如果你先只想测试 CPU

直接：



pip install torch torchvision

如果你的 WSL 支持 GPU，再装 CUDA 对应版本

比如 cu118：



pip install torch torchvision --index-url https://download.pytorch.org/whl/cu118

不过这个要先确认 nvidia-smi 正常。



六、安装项目依赖

pip install -r requirements.txt

七、安装官方 sam3

在项目根目录执行：



git clone https://github.com/facebookresearch/sam3.git sam3\_src

pip install -e ./sam3\_src

如果 GitHub 不稳，可以换镜像：



git clone --depth 1 https://gitclone.com/github.com/facebookresearch/sam3.git sam3\_src

pip install -e ./sam3\_src

八、验证 sam3

执行：



python -c "from sam3.model\_builder import build\_sam3\_image\_model; from sam3.model.sam3\_image\_processor import Sam3Processor; print('OK')"

如果输出 OK，说明库安装通了。



九、放模型文件

你 Windows 上的模型文件如果已经在项目目录里，WSL 也能直接看到，因为它就在 /mnt/c/... 下面。



你只要保证这些文件存在：



/mnt/c/Users/creat/Downloads/Edit-Banana-main/Edit-Banana-main/models/sam3\_ms/sam3.pt

/mnt/c/Users/creat/Downloads/Edit-Banana-main/Edit-Banana-main/models/bpe\_simple\_vocab\_16e6.txt.gz

十、复制配置文件

如果还没有：



cp config/config.yaml.example config/config.yaml

十一、运行

python -m icon\_extractor.cli "input/test.png" -o "./icon\_output"





学习笔记：



1、

python icon\_extractor/cli.py ...

直接将cli当单python文件运行，搜索路径到cli所在目录



python -m icon\_extractor.cli ...

\-m是--module 将cli作为模块执行（将icon\_extractor当作python包）搜索路径为终端所在路径



2、

把你本地文件夹传到 Ubuntu

适合你现在本地已经有一份现成目录。



你当前真正项目目录应该是：



C:\\Users\\creat\\Downloads\\Edit-Banana-main\\Edit-Banana-main

方法 1：用 scp 直接传

在你 Windows 的 PowerShell 里执行：



scp -r "C:\\Users\\creat\\Downloads\\Edit-Banana-main\\Edit-Banana-main" username@服务器IP:\~/



例如：

scp -r "C:\\Users\\creat\\Downloads\\Edit-Banana-main\\Edit-Banana-main" xinhonglei@172.26.10.105:\~/



传完后服务器上会有：



\~/Edit-Banana-main



**现在是禁止像虚拟机传数据嘛，试了好多次scp命令不行哎**

