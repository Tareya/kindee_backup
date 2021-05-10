# -*- coding: utf-8 -*-

'''

Notice!!

Before you use this files，make sure you have install oss2 module.

IF not, please execute 'pip install oss2' first。

Usage:

  Downlaod files:

    python download_from_oss.py -f file1 -f file2 -o ./dest/

  Show fileLists on the oss:

    python download_from_oss.py -l

  Upload file to the oss:

    python download_from_oss.py -f ./file1 -f ./file2 -p log/test1 --upload

NOTES:

1. When the mode is Show files '-l' , other args is not used.

2. When the mode is download files, '-f' appended with the file name on the oss,

    you can check the name by show fileLists on the oss.

    The '-o' means save the files at local path.

3. When the mode is upload files, '-f' means the files at local machine,

    '-p' means the prefix you want add to the filename on the oss,

    this is the way to distinguish the different floder.

4. When you using internal networks! You should use '-i' argument,

    just for free transform.

'''


from __future__ import print_function

import os,time,sys

import operator,oss2,argparse

from itertools import  islice


'''oss工具类'''
class oss_tools:

    '''初始化类'''
    def __init__(self):
        self.auth = oss2.Auth('LTAI4FkeRPyPu7kEY8EPMTdv', 'UDdpw9F0YqOA0eyoKU71bsVHaIscN6')    # AK 认证
        self.endpoint = 'oss-cn-hangzhou-internal.aliyuncs.com'                                # 内网 endpoint
        self.public_endpoint = 'oss-cn-hangzhou.aliyuncs.com'                                  # 公网 endpoint
        self.bucket_name = "uniondrug-kdbackup"                                                # bucket
        self.FLAGS = None




    '''下载文件'''
    def download_files(self, bucket):
        # 如果不存在路径，则创建
        if not os.path.exists(self.FLAGS.outputPath):

            os.mkdir(self.FLAGS.outputPath)

            print("The floder {0} is not existed, will creat it".format(FLAGS.outputPath))


        # 记录进程开始时间
        start_time = time.time()

        # 记录临时文件
        for tmp_file in self.FLAGS.files:

            # 判断文件是否存在于oss上
            if not bucket.object_exists(tmp_file):

                # 若不存在，则输出未找到文件
                print("File {0} is not on the OSS!".format(tmp_file))

            else:

                # 若存在，则开始下载文件
                print("Will download {0} !".format(tmp_file))

                # 记录开始时间
                tmp_time = time.time()

                # 截取文件名
                file_name = tmp_file[tmp_file.rfind("/") + 1 : len(tmp_file)]

                # 拼接路径
                local_filename = os.path.join(self.FLAGS.outputPath, file_name)

                # 从oss下载文件到本地
                oss2.resumable_download(bucket, tmp_file, local_filename, progress_callback=self.percentage)

                print("\nFile {0} -> {1} downloads finished, cost {2} Sec.".format(tmp_file,local_filename,time.time() - tmp_time))

        # 下载完成后，输出完成时间，并输出耗时
        print("All download tasks have finished!")

        print("Cost {0} Sec.".format(time.time() - start_time))



    '''上传文件'''
    def upload_files(self, bucket):
        # 记录进程开始时间
        start_time = time.time()

        for tmp_file in self.FLAGS.files:

            # 判断本地是否存在文件
            if not os.path.exists(tmp_file):

                print("File {0} is not exists!".format(tmp_file))

            else:

                print("Will upload {0} to the oss!".format(tmp_file))

                # 记录开始时间
                tmp_time = time.time()

                # 截取文件名称
                file_name = tmp_file[tmp_file.rfind("/") + 1 : len(tmp_file)]

                # 拼接路径
                oss_filename = os.path.join(self.FLAGS.prefix, file_name)

                # 开始上传文件
                oss2.resumable_upload(bucket, oss_filename, tmp_file, progress_callback=self.percentage)

                print("\nFile {0} -> {1} uploads finished, cost {2} Sec.".format(tmp_file, oss_filename, time.time() - tmp_time))

        # 上传完成后，输出完成时间，并输出耗时
        print("All upload tasks have finished!")

        print("Cost {0} Sec.".format(time.time() - start_time))



    '''遍历文件'''
    def show_files(self, bucket):

        print("Show All OSS Files:")

        for oss_file in islice(oss2.ObjectIterator(bucket), None):

            print(oss_file.key)



    '''上传下载进度'''
    def percentage(self, consumed_bytes, total_bytes):

        if total_bytes:

            rate = int(100 * (float(consumed_bytes) / float(total_bytes)))

            print('\r{0}% '.format(rate), end='')

            sys.stdout.flush()



    '''增加参数'''
    def parser(self):

        # 初始化实例
        arg_parser = argparse.ArgumentParser()

        # 定义文件操作参数
        arg_parser.add_argument(

            '-f',

            '--file',

            dest ='files',

            action ='append',

            default = [],

            help = 'the file name you want to operate!'

        )

        # 定义遍历文件参数
        arg_parser.add_argument(

            '-l',

            '--listfiles',

            default = False,

            dest = 'listFiles',

            action = 'store_true',

            help = 'If been True, list the All the files on the oss !'
        )

        # 定义下载文件存放目录参数
        arg_parser.add_argument(

            '-o',

            '--outputPath',

            dest = 'outputPath',

            default = './',

            type = str,

            help = 'the floder you want to save the files!'

        )

        # 定义使用内网endpoint参数
        arg_parser.add_argument(

            '-i',

            '--internal',

            dest = 'internal',

            default = False,

            action = 'store_true',

            help = 'id you want to use the internal network of aliyun ECS!'
        )

        # 定义文件上传参数
        arg_parser.add_argument(

            '--upload',

            dest = 'upload',

            default = False,

            action = 'store_true',

            help = 'If been used, the mode will become upload mode!'
        )

        # 定义oss文件前缀
        arg_parser.add_argument(

            '-p',

            '--prefix',

            dest = 'prefix',

            default = '',

            type = str,

            help = 'the prefix add to the upload files!'

        )


        self.FLAGS, unparsed = arg_parser.parse_known_args()

        print(self.FLAGS)


    '''运行主体'''
    def main(self):

        # 判断入参，区分使用不同的 endpoint
        if self.FLAGS.internal:
            # 如果使用的是内网
            bucket = oss2.Bucket(self.auth, self.endpoint, self.bucket_name)

            tmp_endpoint = self.endpoint

        else:
            # 如果使用的是公网
            bucket = oss2.Bucket(self.auth, self.public_endpoint, self.bucket_name)

            tmp_endpoint = self.public_endpoint

        print("Your oss endpoint is {0}, the bucket is {1}".format(tmp_endpoint, self.bucket_name))


        # 判断入参，区分不同的操作
        if self.FLAGS.listFiles:

            self.show_files(bucket)

        elif self.FLAGS.upload:

            self.upload_files(bucket)

        else:

            self.download_files(bucket)



if __name__ == '__main__':

    # 初始化对象
    oss = oss_tools()

    # 识别参数
    oss.parser()
    
    # 运行主体
    oss.main()

