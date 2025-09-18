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


# 从当前文件路径开始，往上层遍历，遇到指定名称的文件夹后停止，返回对应的绝对路径
def find_parent_folder( target_folder_name ) :
    # 获取当前文件路径
    current_file_path = os.path.dirname( __file__ )
    
    # 从当前路径开始往上遍历
    current_path = current_file_path
    
    while current_path and current_path != os.path.dirname( current_path ) :
        # 检查当前目录名是否为目标文件夹名
        if os.path.basename( current_path ) == target_folder_name :
            return current_path
        
        # 移动到父目录
        parent_path = os.path.dirname( current_path )
        
        # 如果已经到达根目录，停止遍历
        if parent_path == current_path :
            break
            
        current_path = parent_path
    
    # 如果没有找到目标文件夹，返回None
    return None