# 文件IO操作模块
# 提供文件读写、下载、文件夹操作等功能
# 该模块封装了常用的文件操作功能，包括文件保存、加载、下载和文件夹管理

from os import PathLike
from typing import Union

# 通用路径类型定义，支持 str、bytes 和 PathLike
# 用于替代 str 类型注解，避免 os.path.join() 返回类型导致的编辑器误报
StrPath = Union[str, bytes, PathLike]

# 文件保存相关
from .save import save_df, save_json, save_txt , batch_save_df

# 文件加载相关  
from .load import load_txt, load_yaml, load_excel, load_json, load_base64, load_image

# 文件下载相关
# 使用括号格式是为了提高多函数导入的可读性
from .down_load import (
    download_file,
    download_files,
    download_encode_base64,
    batch_download_encode_base64,

)

# 文件夹操作相关
from .folder import (
    find_files, 
    clear_folder, 
    find_parent_folder, 
    print_folder_tree 
)

# 定义 __all__ 列表，明确指定哪些符号会被导出
__all__ = [
    # 类型定义
    'StrPath',
    
    # 文件保存
    'save_df',
    'save_json',
    'save_txt',
    'batch_save_df',
    
    # 文件加载
    'load_txt',
    'load_yaml',
    'load_excel',
    'load_json',
    'load_base64',
    'load_image',
    
    # 文件下载
    'download_file',
    'download_files',
    'download_encode_base64',
    'batch_download_encode_base64',
    
    # 文件夹操作
    'find_files',
    'clear_folder',
    'find_parent_folder',
    'print_folder_tree'
]