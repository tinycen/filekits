from html.parser import HTMLParser
from typing import Optional, List, Tuple
from pathlib import Path
import re

from . import StrPath


class HTMLCleaner(HTMLParser):
    STYLE_ATTRS = {'class', 'style', 'cellspacing', 'cellpadding', 'border'}

    def __init__(self, remove_styles: bool = True):
        super().__init__()
        self.result = []
        self.skip_tags = {'meta', 'style', 'script'}
        self.skip_depth = 0
        self.vue_attr_pattern = re.compile(r'^data-v-[a-f0-9]+$')
        self.remove_styles = remove_styles

    def _filter_attrs(self, attrs: List[Tuple[str, str]]) -> List[Tuple[str, str]]:
        filtered = [
            (name, value) for name, value in attrs
            if not self.vue_attr_pattern.match(name)
        ]
        if self.remove_styles:
            filtered = [
                (name, value) for name, value in filtered
                if name not in self.STYLE_ATTRS
            ]
        return filtered

    def handle_starttag(self, tag, attrs):
        if tag.lower() in self.skip_tags:
            self.skip_depth += 1
            return
        if self.skip_depth > 0:
            return
        filtered = self._filter_attrs(attrs)  # pyright: ignore[reportArgumentType]
        attrs_str = ' '.join(f'{name}="{value}"' for name, value in filtered)
        if attrs_str:
            self.result.append(f'<{tag} {attrs_str}>')
        else:
            self.result.append(f'<{tag}>')

    def handle_endtag(self, tag):
        if tag.lower() in self.skip_tags:
            self.skip_depth = max(0, self.skip_depth - 1)
            return
        if self.skip_depth > 0:
            return
        self.result.append(f'</{tag}>')

    def handle_data(self, data):
        if self.skip_depth > 0:
            return
        self.result.append(data)

    def handle_comment(self, data):
        if self.skip_depth > 0:
            return
        self.result.append(f'<!--{data}-->')

    def handle_decl(self, decl):
        if self.skip_depth > 0:
            return
        self.result.append(f'<!{decl}>')

    def get_cleaned_html(self) -> str:
        return ''.join(self.result)


def clean_html(html_content: str, remove_styles: bool = True) -> str:
    """精简HTML内容，删除meta、style、script标签及其内容

    Args:
        html_content: HTML字符串内容
        remove_styles: 是否移除样式相关属性（class, style, cellspacing, cellpadding, border），默认True

    Returns:
        str: 精简后的HTML字符串
    """
    cleaner = HTMLCleaner(remove_styles=remove_styles)
    cleaner.feed(html_content)
    return cleaner.get_cleaned_html()


def clean_html_file(
    file_path: StrPath,
    output_path: Optional[StrPath] = None,
    encoding: str = 'utf-8',
    remove_styles: bool = True,
) -> str:
    """精简HTML文件，删除meta、style、script标签及其内容

    Args:
        file_path: HTML文件路径
        output_path: 可选，输出文件路径。若不指定则覆盖原文件
        encoding: 文件编码，默认utf-8
        remove_styles: 是否移除样式相关属性（class, style, cellspacing, cellpadding, border），默认True

    Returns:
        str: 精简后的HTML内容

    Raises:
        FileNotFoundError: 文件不存在时抛出
    """
    file_path = Path(file_path)
    if not file_path.exists():
        raise FileNotFoundError(f"文件不存在: {file_path}")

    html_content = file_path.read_text(encoding=encoding)
    cleaned_content = clean_html(html_content, remove_styles=remove_styles)

    if output_path is not None:
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(cleaned_content, encoding=encoding)
    else:
        file_path.write_text(cleaned_content, encoding=encoding)

    return cleaned_content


def clean_html_dir(
    dir_path: StrPath,
    encoding: str = 'utf-8',
    remove_styles: bool = True,
) -> List[Path]:
    """遍历文件夹，清理其中所有的HTML文件

    Args:
        dir_path: 文件夹路径
        encoding: 文件编码，默认utf-8
        remove_styles: 是否移除样式相关属性（class, style, cellspacing, cellpadding, border），默认True

    Returns:
        List[Path]: 已清理的HTML文件路径列表

    Raises:
        FileNotFoundError: 文件夹不存在时抛出
        NotADirectoryError: 路径不是文件夹时抛出
    """
    dir_path = Path(dir_path)
    if not dir_path.exists():
        raise FileNotFoundError(f"文件夹不存在: {dir_path}")
    if not dir_path.is_dir():
        raise NotADirectoryError(f"路径不是文件夹: {dir_path}")

    cleaned_files = []
    for html_file in dir_path.rglob('*.html'):
        clean_html_file(html_file, encoding=encoding, remove_styles=remove_styles)
        cleaned_files.append(html_file)

    return cleaned_files