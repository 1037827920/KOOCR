# 指定构建镜像所基于的基础镜像
FROM python:3.7-slim

# 将构建上下文的所有文件复制到镜像内的 /KOOCR 路径
COPY . ./KOOCR

RUN sed -i 's#http://deb.debian.org#https://mirrors.163.com#g' /etc/apt/sources.list.d/debian.sources \
    && apt update && apt install -y libglib2.0-dev libsm6 libxrender1 libxext-dev supervisor build-essential libgl1-mesa-glx\
    && rm -rf /var/lib/apt/lists/* \
    && /usr/local/bin/python -m pip install --upgrade pip -i https://pypi.tuna.tsinghua.edu.cn/simple \
    && pip3 install -r ./KOOCR/requirements.txt -i https://mirrors.aliyun.com/pypi/simple/ \
    && python3 ./KOOCR/install.py

# 暴露端口
EXPOSE 8089

# 启动命令
CMD ["supervisord","-c","/KOOCR/supervisord.conf"]