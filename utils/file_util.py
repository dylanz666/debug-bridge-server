import os
import shutil
from datetime import datetime


class FileUtil:
    def __init__(self) -> None:
        pass

    @staticmethod
    def read_lines(file_path):
        """
        按行读取文件内容
        :param file_path: 要读取的目标文件的路径
        :return: 读取出的内容列表
        """
        with open(file_path, "r+", encoding='utf-8') as file:
            return file.readlines()

    @staticmethod
    def read(file_path):
        """
        按行读取文件内容
        :param file_path: 要读取的目标文件的路径
        :return: 读取出的内容列表
        """
        with open(file_path, "r+", encoding='utf-8') as file:
            return file.read()

    @staticmethod
    def write_lines(file_path, lines):
        """
        按行写入文件
        :param file_path: 要写入的目标文件的路径
        :param lines: 要写入文件的数据列表，需要换行时，需要在列表元素中自行处理
        :return: 无
        """
        with open(file_path, "w+", encoding='utf-8') as f:
            f.writelines(lines)

    @staticmethod
    def write_line(file_path, line):
        """
        按行写入文件
        :param line: 要写入文件的一行数据，本方法默认在行末换行
        :param file_path: 要写入的目标文件的路径
        :return: 无
        """
        with open(file_path, "a", encoding='utf-8') as f:
            f.write(f"{line}\n")

    @staticmethod
    def clear(file_path):
        """
        清空文件中的内容
        :param file_path: 要清空内容的文件
        :return: 无
        """
        with open(file_path, "w", encoding='utf-8') as f:
            f.truncate()

    @staticmethod
    def write(file_path, data):
        """
        按行写入文件
        :param data: 要写入文件的数据，本方法默认在行末换行
        :param file_path: 要写入的目标文件的路径
        :return: 无
        """
        with open(file_path, "a", encoding='utf-8') as f:
            f.write(f"{data}\n")

    @staticmethod
    def makedirs_if_not_exist(*paths):
        """
        当文件夹路径不存在时，新建文件夹
        :param paths: 要判断、新建文件夹的路径，可传多个
        :return: 无
        """
        for path in paths:
            if not os.path.exists(path):
                os.system(f"echo {path} not exist, make it.")
                os.makedirs(path)

    @staticmethod
    def create_file_if_not_exist(file_path):
        if os.path.exists(file_path):
            return
        with open(file_path, "w") as file:
            file.write("")
            file.close()

    @staticmethod
    def remove_if_exist(*paths):
        """
        移除文件夹或文件
        :param paths: 要移除的文件夹或文件的路径，可传多个
        :return: 无
        """
        for path in paths:
            if not os.path.exists(path):
                continue
            os.system(f"echo {path} exists, delete it.")
            if os.path.isdir(path):
                shutil.rmtree(path)
                continue
            if os.path.isfile(path):
                os.remove(path)

    @classmethod
    def list_all_files(cls, dir_path):
        """
        采用递归方式，列出文件夹下的所有文件目录与文件
        :param dir_path: 要罗列文件目录与文件的文件路径
        :return: 文件路径dir_path下的所有文件目录与文件路径列表
        """
        if not os.path.exists(dir_path):
            return []
        files = []
        file_list = os.listdir(dir_path)  # 列出文件夹下所有的目录与文件
        for file_path in file_list:
            path = os.path.join(dir_path, file_path)
            if os.path.isdir(path):
                files.extend(cls.list_all_files(path))
            if os.path.isfile(path):
                files.append(path)
        return files

    @staticmethod
    def get_root_dir_path():
        return os.getcwd()

    @staticmethod
    def get_absolute_file_path(file_path):
        return os.path.join(os.getcwd(), file_path)

    @staticmethod
    def get_dirs_sorted_by_modification_time(dir_path):
        if not os.path.exists(dir_path):
            raise FileNotFoundError("The system cannot find the path specified")
        # get all dirs which under the input dir_path
        directories = [d for d in os.listdir(dir_path) if os.path.isdir(os.path.join(dir_path, d)) and d.isdigit()]

        # sort dirs
        dir_with_time = []
        for directory in directories:
            full_dir_path = os.path.join(dir_path, directory)
            modification_time = os.path.getmtime(full_dir_path)
            readable_time = datetime.fromtimestamp(modification_time).strftime('%Y-%m-%d %H:%M:%S')
            dir_with_time.append((full_dir_path + "\\s", readable_time))

        sorted_dirs = sorted(dir_with_time, key=lambda x: x[1], reverse=True)
        return [{"folder_name": d[0], "modification_time": d[1]} for d in sorted_dirs]


if __name__ == "__main__":
    pass
