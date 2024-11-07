# KOOCR

1. 安装依赖(ubuntu22)

```bash
sudo apt install nodejs npm
# nvm node管理器安装
curl -o- https://gitee.com/RubyMetric/nvm-cn/raw/main/install.sh | bash
chmod +x ~./.nvm/nvm.sh
source ~/.bashrc
# 升级node为v17.9.1
nvm install v17.9.1
# 切换淘宝镜像源
vim ~/.npmrc
# 修改registry字段
https://registry.npmmirror.com
# 安装python依赖
sudo apt install python-is-python3
sudo apt install python3-pip
sudo apt-get install libjpeg-dev
pip install -r requirements.txt
# 更换pip源
mkdir -p ~/.pip
vim ~/.pip/pip.conf
# 添加如下内容
[global]
index-url = https://pypi.tuna.tsinghua.edu.cn/simple
```

2. 前端安装依赖

```bash
npm install
```

3. 运行前端

```bash
npm run serve
```

4. 构建前端部署到后端

```bash
npm run build
```

5. 运行后端和前端

```bash
python backend/main.py
```