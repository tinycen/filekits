# FileKits - Python文件处理工具包

一个简洁高效的Python文件处理工具包，提供了文件读写、网络下载、文件夹操作、图像处理等常用功能，让文件处理变得更加简单。

## 🚀 功能特性

- **文件读写**：支持txt、json、yaml、excel等多种格式的文件读写
- **网络下载**：支持单文件和多文件下载，自动重试机制
- **文件夹操作**：文件查找、文件夹清理等实用功能
- **数据处理**：字典工具、pandas数据处理辅助功能
- **图像处理**：支持图像格式转换、裁剪、缩放、绘制、合成等图像处理功能

## 📁 项目结构

```
filekits/
├── __init__.py
├── base_io/               
│   ├── __init__.py         # 基础IO操作模块
│   ├── load.py             # 文件读取功能
│   ├── save.py             # 文件保存功能
│   ├── folder.py           # 文件夹操作
│   └── down_load.py        # 网络文件下载
├── image/                 
│   ├── __init__.py         # 图像处理模块
│   ├── convert.py          # 图像格式转换
│   ├── draw.py             # 图像绘制功能
│   ├── img_crop.py         # 图像裁剪
│   ├── img_fill.py         # 图像填充/合成
│   ├── img_info.py         # 图像信息获取
│   └── img_scale.py        # 图像缩放
└── utils/                 
    ├── __init__.py         # 工具模块
    ├── dict_util.py        # 字典处理工具
    └── pd_util.py          # pandas数据处理工具
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
lower_list = load_txt('example.txt', lower_list=1)
```

#### 读取JSON文件
```python
from filekits.base_io import load_json

data = load_json('data.json')
```

#### 读取YAML文件
```python
from filekits.base_io import load_yaml

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
```

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
from filekits.utils.dict_util import remove_keys

data = {"name": "Alice", "age": 25, "password": "secret"}
clean_data = remove_keys(data, ["password"])
# 结果: {"name": "Alice", "age": 25}
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
from filekits.image import draw_mask, add_text

# 绘制遮罩图像（指定区域为白色，其余为黑色）
cropped_path, area = draw_mask('image.jpg', 
                              {'startX': 100, 'startY': 100, 'endX': 300, 'endY': 300},
                              './output', 'mask.jpg')

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
from filekits.image import paste_image, paste_logo

# 在指定位置粘贴图像
from PIL import Image
base_img = Image.open('base.jpg')
paste_img = Image.open('paste.png')
result = paste_image(base_img, paste_img, (100, 100, 300, 300))
result.save('result.jpg')

# 在图像四角随机添加水印
paste_logo('image.jpg', 'logo.png', 'output.jpg', 
           choice=['top_left', 'top_right', 'bottom_left', 'bottom_right'])
```

#### 图像信息
```python
from filekits.image import is_dark_color

# 判断颜色是否为深色（用于文字颜色选择）
is_dark = is_dark_color([100, 100, 100])  # RGB值
```


## ⚙️ 配置说明

### 网络下载配置
- 自动重试机制：使用`funcguard.tools.send_request`实现自动重试
- User-Agent：内置浏览器User-Agent，避免被服务器拒绝
- 特殊网站处理：针对阿里CDN等特定网站有优化处理

### 文件格式支持
- **文本文件**：.txt
- **数据文件**：.json, .yaml, .yml
- **表格文件**：.xlsx, .csv
- **图片文件**：.jpg, .png, .gif, .bmp, .webp等（通过下载功能和图像处理模块）

## 📝 注意事项

1. **编码问题**：所有文本操作默认使用UTF-8编码
2. **文件存在检查**：下载文件时会自动检查文件是否已存在，避免重复下载
3. **错误处理**：批量下载时支持失败跳过或抛出异常两种模式
4. **路径处理**：使用绝对路径或相对路径均可，程序会自动处理

## 📄 许可证

MIT License