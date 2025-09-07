import os
import shutil

# 遍历文件夹地址，返回指定类型或包含指定名称的文件列表
def find_files( folder_path , extension , filename_match = "" ) :
    file_list = [ ]
    # 遍历目录
    for root , dirs , files in os.walk( folder_path ) :
        # 遍历文件，检查文件扩展名
        for filename in files :
            if filename.endswith( extension ) :
                if filename_match == "" :
                    file_list.append( os.path.join( root , filename ) )
                else :
                    if filename_match in filename :
                        file_list.append( os.path.join( root , filename ) )
    return file_list


# 清空指定文件夹
def clear_folder( folder_path ) :
    # 检测文件夹是否存在，如果不存在就创建
    if not os.path.exists( folder_path ) :
        os.makedirs( folder_path )
    shutil.rmtree( folder_path )
    os.mkdir( folder_path )