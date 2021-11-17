# -*- coding: utf-8 -*-

import operator, os ,sys, time, re, oss2
import log_func


'''oss使用类'''
class oss_usage:

    '''类参数初始化'''
    def __init__(self):
        self.endpoint = 'oss-cn-hangzhou-internal.aliyuncs.com'
        self.public_endpoint = 'oss-cn-hangzhou.aliyuncs.com'
        self.bucket_name = "uniondrug-kdbackup"
        self.ackID = 'xxxxxx'
        self.ackSc = 'xxxxxx'
        self.auth = oss2.Auth(self.ackID, self.ackSc)
        self.bucket = oss2.Bucket(self.auth, self.public_endpoint, self.bucket_name)
        self.log = log_func.debug_log(logger_name='oss_uasge', log_file=os.path.join(os.getcwd(), 'logs', 'oss.log'))


    '''根据路径获取文件名'''
    def get_path_filename(self, path):

        file_name = path[path.rfind(os.path.sep) + 1 : len(path)]

        return file_name



    '''根据路径获取前缀日期'''
    def get_path_prefix(self, path):

        re_time = re.search(r'[A-Z].*\d{8}[0-1][0-9]', path).group()

        time_prefix = re.search(r'\d{6}', re_time).group()

        # self.log.debug(time_prefix)
        
        return time_prefix




    '''确认文件在oss上是否存在'''
    def ensure_file(self, path):

        oss_filename = os.path.join(self.get_path_prefix(path), self.get_path_filename(path)).replace(os.path.sep, '/')

        if self.bucket.object_exists(oss_filename):

            self.log.debug(f'{oss_filename} is on the OSS!')
            return True

        else:

            self.log.debug(f'{oss_filename} is not on the OSS!')
            return False



    '''上传文件'''
    def upload_file(self, path):
           
        if not os.path.exists(path):
            pass

        else:
            self.log.debug(f'开始上传 {path} 到 oss！')

            # 记录开始时间
            start_time = time.time()

            # 如果文件不存在于oss上
            if not self.ensure_file(path):

                oss_filename = os.path.join(self.get_path_prefix(path), self.get_path_filename(path)).replace(os.path.sep, '/')

                # 上传文件
                oss2.resumable_upload(self.bucket, oss_filename, path, progress_callback=self.percentage)

                # 输出完成信息
                self.log.info(r'本地文件 {} --> {}/{} 上传完成，耗时 {} 秒。'.format(path, self.bucket_name, oss_filename, time.time() - start_time))

            else:
                # 如果文件存在于oss上
                self.log.debug(r'{} 已存在于 {}/{} 上。'.format(self.get_path_filename(path), self.bucket_name, self.get_path_prefix(path)))




    '''上传下载进度'''
    def percentage(self, consumed_bytes, total_bytes):
        if total_bytes:
            rate = int(100 * (float(consumed_bytes) / float(total_bytes)))

            print('\r{0}% '.format(rate), end='')

            sys.stdout.flush()






