from html.parser import HTMLParser
from typing import Optional, List, Tuple
from pathlib import Path
import re

from . import StrPath


class HTMLCleaner(HTMLParser):
    def __init__(self):
        super().__init__()
        self.result = []
        self.skip_tags = {'meta', 'style', 'script'}
        self.skip_depth = 0
        self.vue_attr_pattern = re.compile(r'^data-v-[a-f0-9]+$')

    def _filter_attrs(self, attrs: List[Tuple[str, str]]) -> List[Tuple[str, str]]:
        return [
            (name, value) for name, value in attrs
            if not self.vue_attr_pattern.match(name)
        ]

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


def clean_html(html_content: str) -> str:
    """精简HTML内容，删除meta、style、script标签及其内容

    Args:
        html_content: HTML字符串内容

    Returns:
        str: 精简后的HTML字符串
    """
    cleaner = HTMLCleaner()
    cleaner.feed(html_content)
    return cleaner.get_cleaned_html()


def clean_html_file(
    file_path: StrPath,
    output_path: Optional[StrPath] = None,
    encoding: str = 'utf-8',
) -> str:
    """精简HTML文件，删除meta、style、script标签及其内容

    Args:
        file_path: HTML文件路径
        output_path: 可选，输出文件路径。若不指定则覆盖原文件
        encoding: 文件编码，默认utf-8

    Returns:
        str: 精简后的HTML内容

    Raises:
        FileNotFoundError: 文件不存在时抛出
    """
    file_path = Path(file_path)
    if not file_path.exists():
        raise FileNotFoundError(f"文件不存在: {file_path}")

    html_content = file_path.read_text(encoding=encoding)
    cleaned_content = clean_html(html_content)

    if output_path is not None:
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(cleaned_content, encoding=encoding)
    else:
        file_path.write_text(cleaned_content, encoding=encoding)

    return cleaned_content