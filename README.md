# nexus-tools



```shell
# 安装以来
poetry install 

# 上传包
poetry run python main.py upload -r http://baidu.com -u admin -p 1234 ~/.m2

# 下载包
poetry run python main.py npm-down /home/gaojunxin/下载/tasks/package-lock.json /home/gaojunxin/下载/tasks/temp

# 打包npm依赖
poetry run python main.py npm-pack /home/gaojunxin/下载/tasks /home/gaojunxin/下载/tasks/temp
```