# -*-coding:utf-8-*-
import json
import os
from pathlib import Path
from urllib.request import urlretrieve
import subprocess

class NpmTools:
    def node_modules(self, file_dir):
        """  通过递归遍历 node_modules 每个子包的package.json 解析下载链接 """
        links = []
        for root, dirs, files in os.walk(file_dir):
            if 'package.json' in files:
                package_json_file = os.path.join(root, 'package.json')
                try:
                    with open(package_json_file, 'r', encoding='UTF-8') as load_f:
                        load_dict = json.load(load_f)
                        # print(load_dict)
                        if '_resolved' in load_dict.keys():
                            links.append(load_dict['_resolved'])
                except Exception as e:
                    print(package_json_file)
                    print('Error:', e)
        return links


    def package_lock(self, package_lock_path):
        """ 通过递归遍历 package-lock.json 解析下载链接 """
        links = []
        with open(package_lock_path, 'r', encoding='UTF-8') as load_f:
            load_dict = json.load(load_f)
            # print(load_dict)
            self.search(load_dict, "resolved", links)
        return links


    def yarn_lock(self, package_lock_path):
        """ 通过递归遍历 xxx-yarn.lock 解析下载链接 """
        links = []
        with open(package_lock_path, 'r', encoding='UTF-8') as load_f:
            for line in load_f:
                if line.find('resolved') >= 0:
                    line = line.replace('resolved', '')
                    url = line.strip().strip('"')
                    links.append(url)
        return links


    def search(self, json_object, key, links):
        """  遍历查找指定的key   """
        for k in json_object:
            if k == key:
                links.append(json_object[k])
            if isinstance(json_object[k], dict):
                self.search(json_object[k], key, links)
            if isinstance(json_object[k], list):
                for item in json_object[k]:
                    if isinstance(item, dict):
                        self.search(item, key, links)


    def download_file(self, path, store_path):
        """ 根据下载链接下载  """
        # 判断输出的目录是否存在
        if store_path is None:
            print("没有传入要保存的地址！")
            return
        if not Path(store_path).exists():
            os.makedirs(store_path, int('0755'))

        links = []
        if path.endswith("package-lock.json"):
            links = self.package_lock(path)
        elif path.endswith("yarn.lock"):
            links = self.yarn_lock(path)
        else:
            links = self.node_modules(path)
        print("待下载总数:" + str(len(links)))
        # print(links)
        for url in links:
            try:
                filename = url.split('/')[-1]
                index = filename.find('?')
                if index > 0:
                    filename = filename[:index]
                index = filename.find('#')
                if index > 0:
                    filename = filename[:index]
                filepath = os.path.join(store_path, filename)
                if not Path(filepath).exists():
                    print("下载:" + url)
                    urlretrieve(url, filepath)
                # else:
                #     print("file already exists:", filename)
            except Exception as e:
                print('Error Url:' + url)
                print('Error:', e)

    def pack(self, file_dir, store_path):
         # 判断输出的目录是否存在
        if store_path is None:
            print("没有传入要保存的地址！")
            return
        if not Path(store_path).exists():
            os.makedirs(store_path, int('0755'))
        
        if Path(file_dir).joinpath('.pnpm').exists():
            file_dir = Path(file_dir).joinpath('.pnpm')
        else:
            file_dir = Path(file_dir).joinpath('node_modules')

        pack_dirs = set()
        pack_names = set()
        pack_map = {}
        for root, dirs, files in os.walk(file_dir):
            if 'package.json' in files:
                package_json_file = os.path.join(root, 'package.json')
                with open(package_json_file, 'r', encoding='UTF-8') as load_f:
                    load_dict = json.load(load_f)
                    name = load_dict.get('name', None)
                    version = load_dict.get('version', None)
                    if name is None or version is None:
                        continue
                    else:
                        name_version = f'{name}@{version}'
                        if name_version in pack_names:
                            continue
                        pack_dirs.add(root)
                        pack_names.add(name_version)
                        pack_map[root] = name_version

        for pack_path in pack_dirs:
            try:
                result = subprocess.run(['npm', 'pack', '--pack-destination', store_path], capture_output=True, text=True, cwd=pack_path)
                # 检查命令是否成功执行
                if result.returncode != 0:
                    # print(result.stderr)
                    name_version = pack_map[pack_path]
                    print(f'\033[31m打包失败: {name_version}\033[0m')
                    continue
                else:
                    print('打包完成：' + result.stdout, end='')
                    
            except Exception as e:
                print('Error:', e)
if __name__ == '__main__':
    npm_tools = NpmTools()
    # npm_tools.download_file("/home/gaojunxin/下载/tasks/package-lock.json", "/home/gaojunxin/下载/tasks/temp")
    npm_tools.pack("/home/gaojunxin/下载/tasks", "/home/gaojunxin/下载/tasks/temp")
    print("ok")

