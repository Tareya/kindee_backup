# -*- coding: utf-8 -*-


import os, time, datetime, sys, re
import zipfile, shutil

from functools import reduce
from oss_usage import oss_usage
import log_func

'''金蝶备份类'''
class kindee_backup:

    '''初始化类'''
    def __init__(self):

        self.oss = oss_usage()
        self.log = log_func.debug_log(logger_name='kindee_backup', log_file=os.path.join(os.getcwd(), 'logs', 'bakcup.log'))     # 日志对象
        self.src_dir = 'E:\\kdbackup'
        self.dest_dir = 'F:\\kdbackup_data'


    '''获取所有需要备份的路径列表'''
    def get_all_path(self):
        
        path_list = []

        re_timestamp = re.compile('\d{6}')

        for time in os.listdir(self.dest_dir):

            path = os.path.join(self.dest_dir, re_timestamp.match(time).group())

            path_list.append(path)

        return path_list



    '''遍历文件，获取前缀'''
    def get_prefix(self, path):

        name_list = []
        prefix_list = []
        
        # 定义正则匹配实例
        re_prefix = re.compile('.*\d{14}')

        for file in os.listdir(path):
            try:
                name_list.append(re_prefix.match(file).group())

            except:
            	pass
        # print(name_list)

        func = lambda x,y:x if y in x else x + [y]

        prefix_list =  reduce(func, [[],] + name_list)

        return prefix_list           



    '''打包文件'''
    def zip_files(self, prefix):
        
        # 创建zip归档目录
        if not os.path.exists('zips'):
            
            self.log.debug('Floder zips does not exist, start to create the floder.')
            os.mkdir('zips')

        if not os.path.exists(os.path.join(os.getcwd(), 'zips', f'{prefix}.zip')):

            start_time = time.time()

            self.log.debug(f'Start to build {prefix}.zip .')
            # 创建一个文件对象，准备写入内容
            zip_file = zipfile.ZipFile(os.path.join('zips', f'{prefix}.zip'), 'w')

            # 写入要压缩的文件
            zip_file.write(f'{prefix}.bak', compress_type=zipfile.ZIP_DEFLATED)
            zip_file.write(f'{prefix}.dbb', compress_type=zipfile.ZIP_DEFLATED)

            # 写入完成后，关闭对象
            zip_file.close()

            self.log.debug('Finish to build {}.zip completely! Cost {} Sec.'.format(prefix, time.time() - start_time))



    '''进行批量压缩'''
    def zip_all(self):

        for path in self.get_all_path():

            os.chdir(path)

            for prefix in self.get_prefix(path):

                try:
                    self.zip_files(prefix)

                except Exception as e:
                    
                    self.log.error('Error: {}'.format(e))



    '''备份文件上传至oss'''
    def upload_oss(self, path):

        os.chdir(os.path.join(path, 'zips'))

        for file in os.listdir(os.getcwd()):
            try:
                # 上传备份文件
                self.log.debug('开始上传文件 {}.'.format(os.path.join(os.getcwd(), file)))                
                self.oss.upload_file(os.path.join(path, 'zips', file))

                # 移除已上传的文件
                # self.log.debug('上传完成，开始移除 {}.'.format(os.path.join(os.getcwd(), file)))
                # os.remove(os.path.join(path, file))

            except Exception as e:
               	self.log.error('Error: {}'.format(e))


    '''进行批量上传oss'''
    def upload_all(self):

        for path in self.get_all_path():

            self.upload_oss(path)



    '''找到需要备份的文件'''
    def find_files(self, src_dir):
        
        y_timestamp = datetime.datetime.now()

        yesterday = y_timestamp.strftime('%Y%m%d')

        file_list = []

        for file in os.listdir(src_dir):
            try:
                file_name = re.search(f'.*{yesterday}.*', os.path.join(src_dir, file)).group()

                file_list.append(file_name)
            
            except:
                pass

        return file_list
                


    '''移动文件到备份目录'''
    def move_files(self, dest_dir):
                    
        if not os.path.exists(dest_dir):

            os.mkdir(dest_dir)

        for file in self.find_files(self.src_dir):
            try:
                self.log.debug('开始移动文件 {} 到 {}'.format(file, dest_dir))    
                shutil.move(file, dest_dir)

            except:

                pass



    '''每日定时备份任务'''
    def daily_task(self):

        n_timestamp = datetime.datetime.now().strftime('%Y%m')

        bak_dir = os.path.join(self.dest_dir, n_timestamp)

        # 移动前一日备份文件到备份目录
        self.move_files(bak_dir)

        os.chdir(bak_dir)

        # 获取需要压缩的文件前缀
        for prefix in self.get_prefix(os.getcwd()):           
            # 开始压缩文件
            self.zip_files(prefix)

        # 开始上传至oss
        self.upload_oss(os.getcwd())


    


if __name__ == '__main__':

    backup = kindee_backup()

    backup.daily_task()

    # backup.zip_all()

    # backup.upload_all()