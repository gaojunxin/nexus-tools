from nexus3_tools import NexusTools
from npm_pack import NpmTools
import argparse

def main():
    parser = argparse.ArgumentParser(description='Nexus Tools CLI')
    
    subparsers = parser.add_subparsers(dest='command')
    
    upload_parser = subparsers.add_parser('upload', help='上传包到Nexus仓库')
    upload_parser.add_argument('path', type=str, help='需要上传的包的根路径，比如：.m2/repository/')
    upload_parser.add_argument('-r', '--repo', type=str, default='', help='Nexus仓库地址')
    upload_parser.add_argument('-u', '--username', type=str, default='', help='Nexus用户名')
    upload_parser.add_argument('-p', '--userpass', type=str, default='', help='Nexus密码')
    
    npm_down_parser = subparsers.add_parser('npm-down', help='根据package-lock.json下载npm包')
    npm_down_parser.add_argument('path', type=str, default='./package-lock.json', help='package-lock.json的路径')
    npm_down_parser.add_argument('store_path', type=str, default='./store', help='tarballs文件存储路径')
    
    npm_pack_parser = subparsers.add_parser('npm-pack', help='将node_modules打包成tarballs文件')
    npm_pack_parser.add_argument('path', type=str, default='./node_modules', help='node_modules的路径')
    npm_pack_parser.add_argument('store_path', type=str, default='./store', help='tarballs文件存储路径')
    
    args = parser.parse_args()
    
    if args.command == 'upload':
        path = args.path
        repo = args.repo
        username = args.username
        userpass = args.userpass
        masked_password = '*' * len(userpass)
        print(f'准备上传：{path}，仓库地址：{repo}，用户名：{username}，密码：{masked_password}')
    elif args.command == 'npm-down':
        path = args.path
        store_path = args.store_path
        print(f'准备下载：{path}，存储位置：{store_path}')
        npm_tools = NpmTools()
        npm_tools.download_file(path, store_path)
    elif args.command == 'npm-pack':
        path = args.path
        store_path = args.store_path
        print(f'准备打包：{path}，存储位置：{store_path}')
        npm_tools = NpmTools()
        npm_tools.pack(path, store_path)


if __name__ == "__main__":
    main()