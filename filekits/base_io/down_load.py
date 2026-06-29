import os
import base64
import requests
from urllib.parse import urlparse
from funcguard.tools import send_request
from . import StrPath

DEFAULT_HEADERS = {
    "Accept": "application/json, text/plain, */*",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36"
}


def _send_request_with_retry(url, headers=None, stream=False):
    """
    内部方法：发送带重试的请求，处理阿里CDN特殊逻辑

    Args:
        url: 请求的URL
        headers: 自定义请求头（可选）
        stream: 是否使用流式传输，默认 False

    Returns:
        response: 请求响应对象或解析后的数据
    """

    # 为阿里cdn添加特殊处理
    if "https://cbu01.alicdn.com" in url and not headers:
        headers = DEFAULT_HEADERS

    response = send_request(
        method="GET", url=url, headers=headers, return_type="response",
        curl_fallback=True, stream=stream
    )

    # 检查响应状态码，403/420 表示访问被拒绝，通常是下载失败或缺少 headers
    if response.status_code in (403, 420):
        hint = "，可能是请求缺少必要的 headers（如 User-Agent）" if headers is None else ""
        raise requests.HTTPError(
            f"下载失败，服务器返回 {response.status_code}{hint}，URL: {url}"
        )

    # 检查其他 HTTP 错误状态码
    response.raise_for_status()

    return response


def _write_response_to_file(response, file_path: StrPath, chunk_size: int = 524288):
    """
    将响应内容写入文件，支持流式分块写入

    Args:
        response: 请求响应对象（requests.Response 或 curl_cffi 响应）
        file_path: 目标文件路径
        chunk_size: 分块大小（字节），默认 512KB (524288)
    """
    with open(file_path, "wb") as f:
        if hasattr(response, "iter_content"):
            # 支持 iter_content 的响应对象，使用流式写入
            for chunk in response.iter_content(chunk_size):
                if chunk:
                    f.write(chunk)
        else:
            # 不支持 iter_content 的响应对象（如 curl_cffi），直接写入 content
            f.write(response.content)


# 下载网络文件
def download_file(url, download_dir: StrPath, file_name: StrPath = "", return_type="name", stream=True, headers=None):
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
        stream: 是否使用流式下载（默认True，适用于大文件）
        headers: 自定义请求头（可选）

    Returns:
        根据return_type参数返回：
            - "name": 文件名
            - "path": 完整路径
            - "both": (路径, 文件名)元组
        示例用法：
            file_path, file_name = download_file(url, download_dir, return_type="both")
    """
    # 生成文件名，去除查询参数
    parsed = urlparse(url)
    path = parsed.path
    if file_name == "":
        file_name = os.path.basename(path)
    else:
        # 如果提供了自定义文件名但没有扩展名，从URL获取扩展名
        if "." not in file_name:  # pyright: ignore[reportOperatorIssue]
            file_extension = os.path.splitext(path)[1]
            if file_extension:
                file_name = f"{file_name}{file_extension}"

    file_path = os.path.join(download_dir, file_name)  # pyright: ignore[reportCallIssue,reportArgumentType]

    # 检查文件是否已经存在
    if os.path.exists(file_path):
        print(f"文件 {file_name} 已经存在，跳过下载")
    else:
        try:
            response = _send_request_with_retry(url, headers=headers, stream=stream)

            # 使用辅助函数写入文件
            _write_response_to_file(response, file_path)

        except Exception as e:
            print(f"文件下载失败, url： {url} \nReason：{e}")
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
def download_files(
    files, output_folder: StrPath,
    return_type="list", extensions=None, failure_policy="raise", headers=None
):
    """
    批量下载文件

    Args:
        files: 文件URL列表
        output_folder: 下载目录
        return_type: 返回类型，"list"或"dict"
        extensions: 允许的文件扩展名列表，None表示允许所有类型
        failure_policy: 批量下载失败次数过多时的处理策略，可选值：
            - "raise": 抛出异常（默认）
            - "skip": 跳过当前失败文件，继续下载后续文件
        headers: 自定义请求头（可选）

    Returns:
        根据return_type参数返回文件路径列表或字典列表

    Raises:
        RuntimeError: 当failure_policy="raise"且下载失败次数过多时抛出
    """
    if extensions is None:
        extensions = []

    files_path = []
    download_fail_count = 0  # 将失败计数器移到外部，按整个批次计算
    # failed_urls = []  # 记录失败的URL
    # 使用 enumerate 可以解决 多线程下的 i 计数问题
    for idx, url in enumerate(files):
        # 提取文件扩展名（使用urlparse去除查询参数）
        parsed = urlparse(url)
        path = parsed.path
        ext = os.path.splitext(path)[1]

        # 判断是否允许该扩展名
        if extensions and ext.lower() not in extensions:
            print(f"跳过不支持的文件类型: {url}")
            continue

        # 替换文件类型后缀，避免后面重复拼接形成.jpg.jpg的情况
        file_name = os.path.basename(path).replace(ext, "")

        # 如果文件名太短，加前缀防止重命名冲突
        if len(file_name) < 7:
            file_name = f"{idx}_{file_name}"

        try:
            file_path = download_file(url, output_folder, file_name, return_type="path", headers=headers)
        except Exception as e:
            print(f"已跳过")
            download_fail_count += 1
            # failed_urls.append(url)

            if download_fail_count > 3:
                error_msg = f"文件下载失败次数过多，已达 {download_fail_count} 次。"

                if failure_policy == "raise":
                    raise RuntimeError(error_msg)
                elif failure_policy == "skip":
                    print(error_msg + f"当前策略为：{failure_policy}，文件继续下载")
                    continue  # 跳过当前文件，继续下载后续文件
                else:
                    raise ValueError(
                        "failure_policy 参数错误，请传入 'skip' 或 'raise'"
                    )

            continue

        if return_type == "list":
            files_path.append(file_path)
        elif return_type == "dict":
            files_path.append({"path": file_path, "url": url})
        else:
            raise ValueError("return_type 参数错误，请传入 'list' 或 'dict'")

    return files_path


# 下载网络文件并转为base64编码
def download_encode_base64(url, headers=None):
    """
    下载网络文件并直接返回base64编码

    Args:
        url: 文件URL
        headers: 自定义请求头（可选）
    """
    response = _send_request_with_retry(url, headers=headers)

    # 读取文件内容并转为base64
    file_data = response.content
    base64_data = base64.b64encode(file_data).decode("utf-8")

    return base64_data


# 批量 下载网络文件并转为base64编码
def batch_download_encode_base64(urls: list, skip_error=True, headers=None):
    """
    批量下载网络文件并转为base64编码

    Args:
        urls: 文件URL列表
        skip_error: 是否跳过错误文件，默认True
        headers: 自定义请求头（可选）

    Returns:
        list: 包含每个文件base64编码的列表

    Raises:
        Exception: 下载失败时抛出异常
    """
    base64_list = []
    for url in urls:
        try:
            base64_data = download_encode_base64(url, headers=headers)
            base64_list.append(base64_data)
        except Exception as e:
            if skip_error:
                print(f"跳过错误文件 {url}，错误信息：{e}")
            else:
                raise e
    return base64_list
