import os
from funcguard.tools import send_request


# 下载网络文件
def download_file(url, download_dir, file_name="", return_type="name"):
    """
    使用 send_request 自动重试功能下载网络文件
    
    Args:
        url: 文件URL
        download_dir: 下载目录
        file_name: 自定义文件名（可选，如果不提供则从URL提取）
        return_type: 返回类型，可选值：
            - "name": 仅返回文件名（默认）
            - "path": 仅返回完整路径
            - "both": 返回(路径, 文件名)元组
    
    Returns:
        根据return_type参数返回：
            - "name": 文件名
            - "path": 完整路径
            - "both": (路径, 文件名)元组
        示例用法：
            file_path, file_name = download_file(url, download_dir, return_type="both")
    """
    # 生成文件名
    if file_name == "":
        file_name = url.split("/")[-1]
    else:
        # 如果提供了自定义文件名但没有扩展名，从URL获取扩展名
        if '.' not in file_name:
            file_extension = url.split(".")[-1] if '.' in url.split("/")[-1] else ""
            if file_extension:
                file_name = f"{file_name}.{file_extension}"

    file_path = os.path.join(download_dir, file_name)

    # 检查文件是否已经存在
    if os.path.exists(file_path):
        print(f"文件 {file_name} 已经存在，跳过下载")
    else:
        # 设置请求头
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36"
        }
        
        # 使用 send_request 自动重试下载
        try:
            # 为阿里cdn添加特殊处理
            if "https://cbu01.alicdn.com" in url:
                response = send_request( method='GET', url=url, headers=headers, stream=True )
            else:
                response = send_request( method='GET', url=url, stream=True )
            
            # 以二进制模式写入文件
            with open(file_path, 'wb') as file:
                for chunk in response.iter_content(1024):
                    if chunk:  # 过滤掉空chunk
                        file.write(chunk)
                        
        except Exception as e:
            print(f"文件下载失败, url： {url} \n Reason：{e}")
            raise e  # 重新抛出异常，让调用者处理

    if return_type == "name":
        return file_name
    elif return_type == "path":
        return file_path
    elif return_type == "both":
        return file_path, file_name
    else:
        raise ValueError("return_type 参数错误，请传入 'name'、'path' 或 'both'")


# 批量下载文件(单线程)，默认下载图片
def download_files(files, output_folder, return_type="list", extensions=None, on_fail_action="skip"):
    """
    批量下载文件
    
    Args:
        files: 文件URL列表
        output_folder: 下载目录
        return_type: 返回类型，"list"或"dict"
        extensions: 允许的文件扩展名列表，None表示允许所有类型
        on_fail_action: 失败次数过多时的行为，可选值：
            - "skip": 跳过并结束整个循环（默认）
            - "raise": 抛出异常，报出错误
    
    Returns:
        根据return_type参数返回文件路径列表或字典列表
        
    Raises:
        RuntimeError: 当on_fail_action="raise"且下载失败次数过多时抛出
    """
    if extensions is None:
        extensions = []

    files_path = []
    i = 0  # 将i移到循环外部
    download_fail_count = 0  # 将失败计数器也移到外部，按整个批次计算
    failed_urls = []  # 记录失败的URL
    
    for url in files:
        # 提取文件扩展名
        ext = os.path.splitext(url)[1]

        # 判断是否允许该扩展名
        if extensions and ext.lower() not in extensions:
            print(f"跳过不支持的文件类型: {url}")
            continue

        # 替换文件类型后缀，避免后面重复拼接形成.jpg.jpg的情况
        file_name = url.split("/")[-1].replace(ext, "")

        # 如果文件名太短，加前缀防止重命名冲突
        if len(file_name) < 7:
            file_name = f"{i}_{file_name}"
            i += 1

        try:
            file_path = download_file(url, output_folder, file_name, return_type="path")
        except Exception as e:
            print(f"文件下载失败，已跳过：{url}")
            download_fail_count += 1
            failed_urls.append(url)
            
            if download_fail_count > 3:
                error_msg = f"文件下载失败次数过多，已失败 {download_fail_count} 个文件。失败的URL: {failed_urls}"
                
                if on_fail_action == "raise":
                    raise RuntimeError(error_msg)
                elif on_fail_action == "skip":
                    print(error_msg + "，已跳过剩余文件")
                    break  # 终止整个循环
                else:
                    raise ValueError("on_fail_action 参数错误，请传入 'skip' 或 'raise'")
            
            continue

        if return_type == "list":
            files_path.append(file_path)
        elif return_type == "dict":
            files_path.append({"path": file_path, "url": url})
        else:
            raise ValueError("return_type 参数错误，请传入 'list' 或 'dict'")

    return files_path