from pathlib import Path
from typing import Any, Optional

from . import StrPath


def _check_markitdown():
    try:
        from markitdown import MarkItDown
        return MarkItDown
    except ImportError:
        raise ImportError(
            "markitdown 未安装，请使用以下命令安装:\n"
            "  pip install filekits[markdown]\n"
            "或仅安装基础版本:\n"
            "  pip install markitdown"
        )


def _check_markdown_it():
    try:
        from markdown_it import MarkdownIt
        return MarkdownIt
    except ImportError:
        raise ImportError(
            "markdown-it-py 未安装，请使用以下命令安装:\n"
            "  pip install filekits[markdown]\n"
            "或仅安装基础版本:\n"
            "  pip install markdown-it-py"
        )


def file_to_markdown(
    file_path: StrPath,
    output_path: Optional[StrPath] = None,
    enable_plugins: bool = False,
    llm_client=None,
    llm_model: Optional[str] = None,
) -> str:
    """将指定文件转换为Markdown格式

    支持的文件格式包括: PDF, Word, Excel, PowerPoint, HTML, 图片, 音频,
    CSV, JSON, XML, ZIP, YouTube URLs, EPubs 等。

    Args:
        file_path: 要转换的文件路径
        output_path: 可选，Markdown输出文件路径。若不指定则只返回内容不保存
        enable_plugins: 是否启用插件，默认False
        llm_client: 可选，OpenAI兼容的LLM客户端，用于图片描述和OCR
        llm_model: 可选，LLM模型名称，如 "gpt-4o"

    Returns:
        str: 转换后的Markdown文本内容

    Raises:
        FileNotFoundError: 文件不存在时抛出
    """

    file_path = Path(file_path)
    if not file_path.exists():
        raise FileNotFoundError(f"文件不存在: {file_path}")

    kwargs: dict[str, Any] = {"enable_plugins": enable_plugins}
    if llm_client is not None:
        kwargs["llm_client"] = llm_client
    if llm_model is not None:
        kwargs["llm_model"] = llm_model

    MarkItDown = _check_markitdown()
    md = MarkItDown(**kwargs)
    result = md.convert(str(file_path))
    content = result.text_content

    if output_path is not None:
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(content, encoding="utf-8")

    return content


def files_to_markdown(
    file_paths: list[StrPath],
    output_dir: Optional[StrPath] = None,
    enable_plugins: bool = False,
    llm_client=None,
    llm_model: Optional[str] = None,
) -> dict[str, str]:
    """批量将多个文件转换为Markdown格式

    Args:
        file_paths: 要转换的文件路径列表
        output_dir: 可选，输出目录。若指定则将Markdown文件保存到该目录
        enable_plugins: 是否启用插件，默认False
        llm_client: 可选，OpenAI兼容的LLM客户端
        llm_model: 可选，LLM模型名称

    Returns:
        dict: 文件路径到Markdown内容的映射字典
    """
    results = {}
    for file_path in file_paths:
        file_path = Path(file_path)
        if output_dir is not None:
            output_path = Path(output_dir) / f"{file_path.stem}.md"
        else:
            output_path = None

        content = file_to_markdown(
            file_path=file_path,
            output_path=output_path,
            enable_plugins=enable_plugins,
            llm_client=llm_client,
            llm_model=llm_model,
        )
        results[str(file_path)] = content

    return results


def dir_to_markdown(
    dir_path: StrPath,
    output_dir: Optional[StrPath] = None,
    file_extensions: Optional[list[str]] = None,
    recursive: bool = False,
    enable_plugins: bool = False,
    llm_client=None,
    llm_model: Optional[str] = None,
) -> dict[str, str]:
    """自动发现目录中的文件并批量转换为Markdown格式

    Args:
        dir_path: 源目录路径
        output_dir: 可选，输出目录。若指定则将Markdown文件保存到该目录
        file_extensions: 可选，要处理的文件扩展名列表，如 [".pdf", ".docx", ".xlsx"]
                        若不指定则处理所有MarkItDown支持的格式
        recursive: 是否递归处理子目录，默认False
        enable_plugins: 是否启用插件，默认False
        llm_client: 可选，OpenAI兼容的LLM客户端
        llm_model: 可选，LLM模型名称

    Returns:
        dict: 文件路径到Markdown内容的映射字典

    Raises:
        NotADirectoryError: 目录不存在时抛出
    """
    dir_path = Path(dir_path)
    if not dir_path.is_dir():
        raise NotADirectoryError(f"目录不存在: {dir_path}")

    if file_extensions is not None:
        file_extensions = [ext if ext.startswith(".") else f".{ext}" for ext in file_extensions]

    if recursive:
        glob_func = dir_path.rglob
    else:
        glob_func = dir_path.glob

    target_files = []
    if file_extensions:
        for ext in file_extensions:
            target_files.extend(glob_func(f"*{ext}"))
    else:
        for item in glob_func("*"):
            if item.is_file():
                target_files.append(item)

    return files_to_markdown(
        file_paths=target_files,
        output_dir=output_dir,
        enable_plugins=enable_plugins,
        llm_client=llm_client,
        llm_model=llm_model,
    )


def markdown_to_html(
    markdown_text: str,
    output_path: Optional[StrPath] = None,
    plugins: Optional[list[str]] = None,
) -> str:
    """将Markdown文本转换为HTML格式

    Args:
        markdown_text: Markdown格式的文本内容
        output_path: 可选，HTML输出文件路径。若不指定则只返回内容不保存
        plugins: 可选，markdown-it插件列表，如 ["table", "strikethrough"]

    Returns:
        str: 转换后的HTML文本内容
    """

    MarkdownIt = _check_markdown_it()
    md = MarkdownIt("commonmark")

    if plugins:
        for plugin in plugins:
            md.enable(plugin)

    html_content = md.render(markdown_text)

    if output_path is not None:
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(html_content, encoding="utf-8")

    return html_content


def markdown_file_to_html(
    markdown_path: StrPath,
    output_path: Optional[StrPath] = None,
    plugins: Optional[list[str]] = None,
) -> str:
    """读取Markdown文件并转换为HTML格式

    Args:
        markdown_path: Markdown文件路径
        output_path: 可选，HTML输出文件路径。若不指定则默认使用相同文件名但.html扩展名
        plugins: 可选，markdown-it插件列表

    Returns:
        str: 转换后的HTML文本内容

    Raises:
        FileNotFoundError: 文件不存在时抛出
    """
    markdown_path = Path(markdown_path)
    if not markdown_path.exists():
        raise FileNotFoundError(f"文件不存在: {markdown_path}")

    markdown_text = markdown_path.read_text(encoding="utf-8")

    if output_path is None:
        output_path = markdown_path.with_suffix(".html")

    return markdown_to_html(
        markdown_text=markdown_text,
        output_path=output_path,
        plugins=plugins,
    )


def batch_markdown_to_html(
    markdown_dir: StrPath,
    output_dir: Optional[StrPath] = None,
    recursive: bool = False,
    plugins: Optional[list[str]] = None,
) -> dict[str, str]:
    """批量将目录中的Markdown文件转换为HTML格式

    Args:
        markdown_dir: Markdown文件所在目录
        output_dir: 可选，HTML输出目录。若不指定则保存到Markdown文件同目录
        recursive: 是否递归处理子目录，默认False
        plugins: 可选，markdown-it插件列表

    Returns:
        dict: Markdown文件路径到HTML内容的映射字典

    Raises:
        NotADirectoryError: 目录不存在时抛出
    """
    markdown_dir = Path(markdown_dir)
    if not markdown_dir.is_dir():
        raise NotADirectoryError(f"目录不存在: {markdown_dir}")

    if recursive:
        md_files = list(markdown_dir.rglob("*.md"))
    else:
        md_files = list(markdown_dir.glob("*.md"))

    results = {}
    for md_file in md_files:
        if output_dir is not None:
            rel_path = md_file.relative_to(markdown_dir)
            html_path = Path(output_dir) / rel_path.with_suffix(".html")
        else:
            html_path = None

        html_content = markdown_file_to_html(
            markdown_path=md_file,
            output_path=html_path,
            plugins=plugins,
        )
        results[str(md_file)] = html_content

    return results
