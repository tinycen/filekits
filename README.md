# FileKits - Python文件处理工具包

一个简洁高效的Python文件处理工具包，提供了文件读写、网络下载、文件夹操作、图像处理等常用功能，让文件处理变得更加简单。

## 🚀 功能特性

- **文件读写**：支持txt、json、yaml、excel等多种格式的文件读写
- **网络下载**：支持单文件和多文件下载，自动重试机制
- **文件夹操作**：文件查找、文件夹清理等实用功能
- **数据处理**：字典工具、pandas数据处理辅助功能
- **图像处理**：支持图像格式转换、裁剪、缩放、绘制、合成、去重等图像处理功能
- **Markdown转换**：支持多种文件格式转换为Markdown，以及Markdown转HTML

## 📁 项目结构

```
filekits/
├── __init__.py
├── base_io/               
│   ├── __init__.py         # 基础IO操作模块
│   ├── load.py             # 文件读取功能
│   ├── save.py             # 文件保存功能
│   ├── folder.py           # 文件夹操作
│   ├── down_load.py        # 网络文件下载
│   ├── markdown_convert.py # Markdown转换功能
│   └── html_clean.py       # HTML清理功能
├── image/                 
│   ├── __init__.py         # 图像处理模块
│   ├── convert.py          # 图像格式转换
│   ├── draw.py             # 图像绘制功能
│   ├── img_crop.py         # 图像裁剪
│   ├── img_fill.py         # 图像填充/合成
│   ├── img_info.py         # 图像信息获取
│   ├── img_scale.py        # 图像缩放
│   └── img_dedup.py        # 图像去重
└── utils/                 
    ├── __init__.py         # 工具模块
    └── dict_util.py        # 字典处理工具
```

## 📦 安装/更新

```bash
pip install --upgrade filekits
```

## 🛠️ 使用方法

### 1. 文件读取

#### 读取文本文件
```python
from filekits.base_io import load_txt

# 读取txt文件为列表
text_list = load_txt('example.txt')

# 读取为字符串
text_str = load_txt('example.txt', return_type="str")

# 转换为小写列表
lower_list = load_txt('example.txt', to_lowercase=True)
```

#### 读取 JSON/YAML 文件
```python
from filekits.base_io import load_json, load_yaml
data = load_json('data.json')
config = load_yaml('config.yaml')
```

#### 读取Excel文件
```python
from filekits.base_io import load_excel

# 读取为pandas DataFrame
df = load_excel('data.xlsx', return_type="df")

# 读取为openpyxl工作表
wb, sheet, rows = load_excel('data.xlsx', return_type="sheet")
```

#### 读取图像文件
```python
from filekits.base_io import load_image

# 使用PIL后端读取图像（返回PIL.Image对象）
img = load_image('image.jpg', backend="PIL")

# 使用OpenCV后端读取图像（返回numpy数组）
img_cv = load_image('image.jpg', backend="cv2")

# 也可以直接传入图像对象
img_obj = load_image(pil_image_obj)  # 或 load_image(cv2_image_array)
```

### 2. 文件保存

#### 保存DataFrame
```python
from filekits.base_io import save_df
import pandas as pd

df = pd.DataFrame({'name': ['Alice', 'Bob'], 'age': [25, 30]})

# 保存为Excel
save_df(df, 'output.xlsx')

# 保存为CSV
save_df(df, 'output.csv')

# 保存为JSON
save_df(df, 'output.json')
```

#### 保存JSON文件
```python
from filekits.base_io import save_json

data = {"name": "Alice", "age": 25}
save_json(data, 'data.json')

# 启用简化模式：自动截断长字符串、缩减长列表
large_data = {"content": "这是一段很长的文本内容...", "items": [1, 2, 3, 4, 5]}
save_json(large_data, 'data.json', simplify=True)

# 自定义简化参数：字符串截断30字符，列表保留5个元素
save_json(large_data, 'data.json', simplify=True, max_length=30, max_list=5)
```

#### 保存文本文件
```python
from filekits.base_io import save_txt

# 保存列表到txt文件
my_list = ['line1', 'line2', 'line3']
save_txt(my_list, 'output.txt')

# 保存字符串到txt文件
my_text = "这是一段文本内容"
save_txt(my_text, 'output.txt')
```

### 3. 文件夹操作

#### 查找文件
```python
from filekits.base_io import find_files

# 查找所有jpg文件
jpg_files = find_files('/path/to/folder', '.jpg')

# 查找包含特定名称的文件
specific_files = find_files('/path/to/folder', '.txt', 'log')
```

#### 向上查找指定文件夹
```python
from filekits.base_io import find_parent_folder

# 从当前文件位置开始，向上查找指定名称的文件夹
# 例如查找名为 "project" 的父文件夹路径
project_path = find_parent_folder("project")

if project_path:
    print(f"找到文件夹路径: {project_path}")
else:
    print("未找到指定的文件夹")
```

#### 清空文件夹
```python
from filekits.base_io import clear_folder

# 清空并重新创建文件夹
clear_folder('/path/to/clean')
```

### 4. 网络文件下载

#### 单文件下载
```python
from filekits.base_io import download_file

# 下载文件
file_path = download_file('https://example.com/file.jpg', './downloads')

# 自定义文件名
file_path = download_file('https://example.com/file.jpg', './downloads', 'myfile.jpg')

# 返回完整信息
file_path, file_name = download_file('https://example.com/file.jpg', './downloads', return_type="both")

# 禁用流式下载（适用于小文件）
file_path = download_file('https://example.com/file.jpg', './downloads', stream=False)
```

#### 批量下载
```python
from filekits.base_io import download_files

urls = [
    'https://example.com/image1.jpg',
    'https://example.com/image2.jpg'
]

# 批量下载图片
file_paths = download_files(urls, './images')

# 只下载特定类型文件
file_paths = download_files(urls, './downloads', extensions=['.jpg', '.png'])

# 返回字典格式（包含URL信息）
file_dicts = download_files(urls, './downloads', return_type="dict")

# 自定义请求头
file_paths = download_files(urls, './downloads', headers={"User-Agent": "Custom/1.0"})

# 设置失败策略：跳过失败文件继续下载
file_paths = download_files(urls, './downloads', failure_policy="skip")
```

**failure_policy 参数说明：**
- `"raise"`（默认）：当失败次数超过3次时，抛出 `RuntimeError` 异常
- `"skip"`：当失败次数超过3次时，打印警告并继续下载后续文件

#### 下载并转为Base64
```python
from filekits.base_io import download_encode_base64

# 下载文件并直接获取base64编码
base64_str = download_encode_base64('https://example.com/image.jpg')

# 适用于需要直接处理文件内容而不保存到本地的场景
# 如：直接上传到云存储、嵌入到HTML/CSS、API传输等
```

#### 批量下载并转为Base64
```python
from filekits.base_io import batch_download_encode_base64

urls = [
    'https://example.com/image1.jpg',
    'https://example.com/image2.jpg'
]

# 批量下载并获取base64编码
base64_list = batch_download_encode_base64(urls)
```

### 5. 工具函数

#### 字典操作
```python
from filekits.utils.dict_util import remove_keys, simplify_dict, dict_dumps

# 从字典中移除指定的键
data = {"name": "Alice", "age": 25, "password": "secret"}
clean_data = remove_keys(data, ["password"])
# 结果: {"name": "Alice", "age": 25}

# 递归简化字典：截断过长字符串、缩减过长列表
complex_data = {
    "content": "这是一段非常长的文本内容，需要被截断处理",
    "items": [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
}
simplified = simplify_dict(complex_data, max_length=15, max_list=3)
# 结果: {"content": "这是一段非常长的文...", "items": [1, 2, 3, "...(+7 more)"]}

# 将字典转换为JSON字符串，可选先简化处理
json_str = dict_dumps(complex_data, simplify=True, max_length=20, max_list=5)
print(json_str)
```

### 6. 图像处理

#### 图像格式转换
```python
from filekits.image import to_jpg

# 将PNG、GIF、WebP等格式转换为JPG
jpg_path = to_jpg('image.png', output_folder='./output', delete_origin=False)
```

#### 图像裁剪
```python
from filekits.image import crop_transparent

# 删除PNG图片的透明区域
cropped_path = crop_transparent('image.png')

# 同时转换为JPG格式（透明背景变为白色）
cropped_jpg = crop_transparent('image.png', turn_jpg=True)
```

#### 图像缩放
```python
from filekits.image import scale_image

# 将第2张图片强制缩放到和第1张图片一样大小
scale_image('reference.jpg', 'target.jpg')
```

#### 图像绘制
```python
from filekits.image import create_rect_mask, create_polygon_mask, add_text

# 绘制矩形遮罩（指定区域为白色，其余为黑色）
# 当 crop_expansion > 0 时会裁剪出小图块，减少显存占用
cropped_path, area = create_rect_mask(
    'image.jpg',
    {'startX': 100, 'startY': 100, 'endX': 300, 'endY': 300},
    'mask.jpg',
    './output',
    crop_expansion=200
)

# 绘制多边形遮罩（支持多个多边形区域）
# 始终生成与原图等大的 mask，不做裁剪
polygons = [[(100, 100), (300, 100), (300, 300), (100, 300)]]
mask_path = create_polygon_mask('image.jpg', polygons, 'polygon_mask.jpg', expand_px=20)

# 在图像上添加文字
font_path = {'Bold': 'font_bold.ttf', 'Medium': 'font_medium.ttf'}
box_infos = [{
    'text_translated': 'Hello World',
    'box': [(50, 50), (200, 50), (200, 100), (50, 100)],
    'width': 150, 'height': 50, 'short_side': 40
}]
output_path = add_text('image.jpg', box_infos, font_path, 'output.jpg')
```

#### 图像合成
```python
from filekits.image import paste_image, paste_logo, paste_logo_random

# 在指定位置粘贴图像
from PIL import Image
base_img = Image.open('base.jpg')
paste_img = Image.open('paste.png')
result = paste_image(base_img, paste_img, (100, 100, 300, 300))
result.save('result.jpg')

# 在图像四角随机添加水印
paste_logo('image.jpg', 'logo.png', 'output.jpg', 
           choice=['top_left', 'top_right', 'bottom_left', 'bottom_right'])

# 在图像上随机位置、随机角度、随机透明度粘贴水印
paste_logo_random('image.jpg', 'logo.png', 'output.jpg')

# 自定义 alpha 缩放范围和角度范围
# alpha_scale_range: 原图 alpha 值的缩放系数，0.2 表示原透明度的 20%
paste_logo_random('image.jpg', 'logo.png', 'output.jpg',
                  alpha_scale_range=(0.1, 0.5),
                  angle_range=(-30.0, 30.0))
```

#### 图像信息
```python
from filekits.image import is_dark_color

# 判断颜色是否为深色（用于文字颜色选择）
is_dark = is_dark_color([100, 100, 100])  # RGB值
```

#### 图像去重
```python
from filekits.image import dedup_images

image_urls = [
    'https://example.com/image1.jpg',
    'https://example.com/image2.jpg',
    'https://example.com/image3.jpg'
]

# 对图片URL列表进行去重，返回不重复的URL列表
unique_urls = dedup_images(image_urls, './download_temp')
```

### 7. Markdown转换

将各种文件格式转换为Markdown，适用于文本分析、LLM处理等场景。

**基础版本支持的输入格式：**
- PDF
- PowerPoint (PPTX)
- Word (DOCX)
- Excel (XLSX)
- HTML
- CSV、JSON、XML
- ZIP文件（遍历内容）
- YouTube URLs
- EPubs
- 图片（EXIF元数据）
- 音频（EXIF元数据和语音转录）

> **注意**：如需启用OCR功能（从PDF/DOCX/PPTX/XLSX中的嵌入图片提取文字），需要额外安装`markitdown-ocr`插件并配置LLM客户端。

#### 文件转Markdown
```python
from filekits.base_io import file_to_markdown

# 单个文件转换（基础版本）
content = file_to_markdown('document.pdf')

# 转换并保存到文件
content = file_to_markdown('document.pdf', output_path='output.md')

# 启用OCR插件（需要先安装markitdown-ocr）
from openai import OpenAI
content = file_to_markdown(
    'document.pdf',
    enable_plugins=True,
    llm_client=OpenAI(),
    llm_model="gpt-4o"
)
```

#### 批量文件转Markdown
```python
from filekits.base_io import files_to_markdown

file_paths = ['file1.pdf', 'file2.docx', 'file3.xlsx']

# 批量转换（返回字典：文件路径 -> Markdown内容）
results = files_to_markdown(file_paths)

# 批量转换并保存到目录
results = files_to_markdown(file_paths, output_dir='./output')
```

#### 目录批量转Markdown
```python
from filekits.base_io import dir_to_markdown

# 转换目录中所有支持的文件
results = dir_to_markdown('/path/to/docs')

# 只处理特定类型文件
results = dir_to_markdown('/path/to/docs', file_extensions=['.pdf', '.docx'])

# 递归处理子目录
results = dir_to_markdown('/path/to/docs', recursive=True)

# 递归处理并保存到输出目录
results = dir_to_markdown('/path/to/docs', output_dir='./output', recursive=True)
```

#### Markdown转HTML
```python
from filekits.base_io import markdown_to_html

# 将Markdown文本转为HTML
html_content = markdown_to_html('# Hello\nWorld')

# 转换并保存到文件
html_content = markdown_to_html('# Hello\nWorld', output_path='output.html')
```

#### Markdown文件转HTML
```python
from filekits.base_io import markdown_file_to_html

# 读取Markdown文件并转为HTML（默认保存为同名.html文件）
html_content = markdown_file_to_html('document.md')

# 指定输出路径
html_content = markdown_file_to_html('document.md', output_path='output.html')
```

#### 批量Markdown转HTML
```python
from filekits.base_io import batch_markdown_to_html

# 批量转换目录中的Markdown文件
results = batch_markdown_to_html('/path/to/markdown_files')

# 递归处理子目录
results = batch_markdown_to_html('/path/to/markdown_files', recursive=True)

# 指定输出目录
results = batch_markdown_to_html('/path/to/markdown_files', output_dir='./html_output')
```

### 8. HTML清理

精简HTML内容，删除meta、style、script标签及其内容，适用于清理爬取的网页数据。

#### 清理HTML字符串
```python
from filekits.base_io import clean_html

html = '<html><head><style>body{color:red}</style></head><body>Hello</body></html>'
cleaned = clean_html(html)
# 结果: <html><head></head><body>Hello</body></html>

# 保留样式属性
cleaned = clean_html(html, remove_styles=False)
```

#### 清理HTML文件
```python
from filekits.base_io import clean_html_file

# 清理并覆盖原文件
cleaned_content = clean_html_file('page.html')

# 清理并保存到新文件
cleaned_content = clean_html_file('page.html', output_path='cleaned.html')
```

#### 批量清理文件夹中的HTML文件
```python
from filekits.base_io import clean_html_dir

# 递归清理文件夹中所有HTML文件（直接覆盖原文件）
cleaned_files = clean_html_dir('/path/to/html_folder')

# 自定义编码
cleaned_files = clean_html_dir('/path/to/html_folder', encoding='gbk')

# 保留样式属性
cleaned_files = clean_html_dir('/path/to/html_folder', remove_styles=False)
```

## 📄 许可证

MIT License