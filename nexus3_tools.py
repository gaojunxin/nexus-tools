import multiprocessing
import requests
import re
import json
from xml.dom.minidom import parse
import xml.dom.minidom
from requests.auth import HTTPBasicAuth
import os
import sys
if sys.version > '3':
    import queue as Queue
else:
    import Queue
import threading

class NexusTools:
    def __init__(self, repo_url, username, password):
        self.repo_url = repo_url
        self.username = username
        self.password = password
    def getLatestVersion(self, groupId, artifactId, nexusUrl, repository, cookie):
        # 从nexus获取指定项目的所有版本号
        version_list = self.__get_version_list(artifactId, groupId, nexusUrl, repository, cookie)

        # 计算出最大的版本号
        max_version = self.__get_max_version(version_list)
        #print('%s:%s:最新的版本号 >>>   %s'%(groupId, artifactId, max_version) )
        return max_version


    # 从集合中，查找出最大的版本号
    def __get_max_version(self, version_list):
        # 初始值设为 0.0.0
        # 数据格式为 ('完整的版本号'，主版本号, 次版本号, 小版本号)
        max_version_tup = ('0.0.0', 0, 0, 0)

        for current_version in version_list:
            # 对于形如 1.1.0-SNAPSHOT 的版本号，转换成 1.1.0
            temp_version = re.sub('-.*', '', current_version)
            num_list = temp_version.split('.')
            current_version_tup = [current_version, int(num_list[0]), int(num_list[1]), int(num_list[2])]

            # 与上一次记录的最大版本号比较，取二者最大值，作为最新的最大版本号
            max_version_tup = self.__get_max_version_tup(max_version_tup, current_version_tup)

        return max_version_tup[0]


    # 比较两个版本号，返回其中的最大者
    def __get_max_version_tup(self, tup_a, tup_b):
        # 依次比较3个版本号
        if tup_a[1] > tup_b[1]:
            return tup_a
        if tup_a[1] < tup_b[1]:
            return tup_b

        if tup_a[2] > tup_b[2]:
            return tup_a
        if tup_a[2] < tup_b[2]:
            return tup_b

        if tup_a[3] > tup_b[3]:
            return tup_a
        if tup_a[3] < tup_b[3]:
            return tup_b

        return tup_a


    # 查询指定项目的所有版本号
    def __get_version_list(self, artifactId, groupId, url, repository, cookie):
        response = self.__get_xml(groupId, artifactId, url, repository, cookie)

        version_list = []
        # 从响应参数中，提取出所有版本号，并追加至数组
        self.__fill_version(version_list, response)

        return version_list


    # 从响应参数中，提取出所有版本号，并追加至数组
    def __fill_version(self, version_list, response):
        # response = json.loads(response)
        DOMTree = xml.dom.minidom.parseString(response)
        metadata = DOMTree.documentElement
        versions = metadata.getElementsByTagName("version")
        for i in versions:
            version_list.append(i.childNodes[0].data)
        return version_list


    # json格式的post请求
    def __get_xml(self, groupId, artifactId, url, repository, cookie):
        headers = {'Cookie': cookie, 'content-type': 'application/json', 'charset': 'utf-8'}
        target_url = url+"/repository/%s/%s/%s/maven-metadata.xml"%(repository, groupId.replace(".","/"), artifactId)
        response = requests.get(target_url, headers=headers)
        return response.text
    
    def put_file(self, file_path, home_path):
        upload_url = file_path.replace(home_path+os.sep,'').replace('\\','/')
        print('正在上传' + file_path)
        try:
            url = self.repo_url+'/'+ upload_url
            r = requests.put(url, data=open(file_path,'rb').read(),files={},headers={}, auth=HTTPBasicAuth(self.username, self.password))
            r.raise_for_status()
        except requests.RequestException as e:
            print(e)

    def upload_jar(self, repo_path):
        for root, dirs, files in os.walk(repo_path):
            # root 表示当前正在访问的文件夹路径
            # dirs 表示该文件夹下的子目录名list
            # files 表示该文件夹下的文件list

            # 遍历文件
            for f in files:
                if(f.endswith('.pom') or f.endswith('.jar')):
                    file_path = os.path.join(root, f)
                    self.put_file(file_path , repo_path)

    class UploadThread (threading.Thread):
        def __init__(self, thread_id, queue, queue_lock, repo_path, uploader):
            super().__init__()
            self.thread_id = thread_id
            self.name = "线程-%d" % thread_id
            self.queue = queue
            self.queue_lock = queue_lock
            self.uploader = uploader
            self.repo_path = repo_path

        def run(self):
            print("Starting " + self.name)
            while True:
                with self.queue_lock:
                    if not self.queue.empty():
                        data = self.queue.get()
                        if data is None:
                            self.queue.task_done()
                            break
                        self.uploader.put_file(data, self.repo_path)
                        print("%s 上传成功 %s" % (self.name, data))
                        self.queue.task_done()
            print("退出线程 " + self.name)


    def upload_jar_thread(self, repo_path):
        thread_num = multiprocessing.cpu_count()
        queueLock = threading.Lock()
        workQueue = Queue.Queue()
        threads = []

        thread_id = 1
        with queueLock:
            for root, dirs, files in os.walk(repo_path):
                for f in files:
                    if f.endswith('.pom') or f.endswith('.jar'):
                        full_path = os.path.join(root, f)
                        workQueue.put(full_path)

        for _ in range(thread_num):
            thread = self.UploadThread(thread_id, workQueue, queueLock, repo_path, self)
            thread.start()
            threads.append(thread)
            thread_id += 1
        
        for _ in threads:
            workQueue.put(None)
        # Wait for queue to empty
        workQueue.join()
        
        # Wait for all threads to complete
        for t in threads:
            t.join()
            
        print("所有文件上传完成!")
    
    def upload_npm(self, repo_path):
        pass

if __name__ == '__main__':
    repoPath='/home/gaojunxin/mvn/repository'
    nexus_tools = NexusTools("xx", 'xx', 'xxx')
    # nexus_tools.upload_jar_thread(repoPath)
    nexus_tools.upload_jar(repoPath)