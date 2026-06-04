# import cv2
# import math
# import numpy as np
import random
from typing import Literal
from PIL import Image
# from PIL import ImageDraw, ImageFont
from ..base_io import load_image, StrPath
from .img_info import correct_position


# def _get_adaptive_font_size(img_w: int, img_h: int, base_size: int) -> int:
#     """根据图片尺寸计算自适应字体大小，占图片短边的 10%~50%"""
#     short_side = min(img_w, img_h)
#     min_size = max(int(short_side * 0.1), 8)
#     max_size = max(int(short_side * 0.5), min_size)
#     # 当 base_size 小于 min_size 时，优先使用 min_size 确保文字不会太小
#     if base_size < min_size:
#         return min_size
#     return min(base_size, max_size)

# 预设水印颜色
# WATERMARK_COLORS = {
#     "gray": (128, 128, 128),
#     "orange": (255, 165, 0),
#     "blue": (0, 0, 255),
#     "red": (255, 0, 0),
# }

# 颜色填充
def color_fill( image_path, modify_info, output_path ) :
    modify_info = correct_position( modify_info )
    if modify_info is None:
        return
    fill_action = modify_info[ 'type' ]
    if "white" in fill_action :
        color = "white"
    elif "black" in fill_action :
        color = "black"
    else :
        color = "white"

    # 加载图片
    img = Image.open( image_path )

    # 获取要修改的区域的坐标
    start_x = modify_info[ 'startX' ]
    start_y = modify_info[ 'startY' ]
    end_x = modify_info[ 'endX' ]
    end_y = modify_info[ 'endY' ]

    rectangle_width = round( end_x - start_x )
    rectangle_height = round( end_y - start_y )

    # 创建遮罩区域
    white_rectangle = Image.new( 'RGB', (rectangle_width, rectangle_height), color )
    # 将白色矩形粘贴到原图的指定位置
    img = paste_image( img, white_rectangle, (start_x, start_y, end_x, end_y), "PIL" )

    # 检测img是否为RGB格式，确保图像模式为 'RGB'
    if img.mode != 'RGB' :
        img = img.convert( 'RGB' )
    img.save( output_path )
    img.close()

    return


def paste_image( original_image , paste_img , box: tuple[int, int] | tuple[int, int, int, int] , backend: Literal["PIL"] = "PIL" ) -> Image.Image:
    original_image = load_image( original_image , backend )
    paste_img = load_image( paste_img , backend )

    if backend == "PIL" :
        rounded_box = tuple( round( element ) if isinstance( element , float ) else element for element in box )
        # isinstance(element, float) 是用来判断元素是否为浮点数类型，如果是则执行四舍五入操作，否则保持原样。
        original_image.paste( paste_img , rounded_box )  # pyright: ignore[reportArgumentType]

    # todo 下面这段代码存在问题，无法使用：ValueError: could not broadcast input array from shape (800,800,3) into shape (371,800,3)
    # elif backend == "cv2" and len( box ) == 4 :
    #     startX , startY , endX , endY = box[ 0 ] , box[ 1 ] , box[ 2 ] , box[ 3 ]
    #     # 计算偏移量
    #     offsetX , offsetY = endX - startX , endY - startY
    #     # 创建仿射变换矩阵
    #     matrix = np.float32( [ [ 1 , 0 , offsetX ] , [ 0 , 1 , offsetY ] ] )
    #     # 应用仿射变换
    #     transformed_image = cv2.warpAffine( paste_img , matrix ,
    #                                         (original_image.shape[ 1 ] , original_image.shape[ 0 ]) )
    #     # 将变换后的图像粘贴到原图像上
    #     # original_image[ startY :endY, startX :endX ] = transformed_image
    #     original_image[ round( startY ) :round( endY ) , round( startX ) :round( endX ) ] = transformed_image

    return original_image


# 在图像的四角随机一处添加水印
def paste_logo(
    image_path: StrPath,
    logo_path: StrPath,
    output_path: StrPath,
    choice: list[str] = ['top_left', 'top_right']
) -> StrPath:
    """
    Args:
        image_path: 原始图像路径
        logo_path: 水印图像路径
        output_path: 输出图像路径
        choice: 选择添加水印的位置，默认为 ['top_left', 'top_right'],
            可选:['top_left', 'top_right', 'bottom_left', 'bottom_right']
    """
    image = Image.open( image_path )
    logo = Image.open( logo_path )
    width , height = image.size
    logo_width , logo_height = logo.size

    # 考虑到10px的边距
    margin = 10

    # 随机选择一个四角位置
    corner = random.choice( choice )
    if corner == 'top_left' :
        x = y = margin
    elif corner == 'top_right' :
        x = width - logo_width - margin
        y = margin
    elif corner == 'bottom_left' :
        x = margin
        y = height - logo_height - margin
    else :
        x = width - logo_width - margin
        y = height - logo_height - margin

    # 在选定的位置粘贴水印
    image = paste_image( image , logo , (x , y) , "PIL" )
    # 保存修改后的图像
    image.save( output_path )
    image.close()
    logo.close()

    return output_path


def paste_logo_random(
    image_path: StrPath,
    logo_path: StrPath,
    output_path: StrPath,
    opacity_range: tuple[float, float] = (0.15, 0.35),
    angle_range: tuple[float, float] = (-45.0, 45.0),
) -> StrPath:
    """
    在图像上随机位置、随机角度、随机透明度粘贴图片水印。

    Args:
        image_path: 原始图像路径
        logo_path: 水印图像路径
        output_path: 输出图像路径
        opacity_range: 透明度范围，默认 (0.15, 0.35)
        angle_range: 旋转角度范围（度），默认 (-45, 45)
    """
    image = Image.open(image_path).convert("RGBA")
    logo = Image.open(logo_path).convert("RGBA")

    img_w, img_h = image.size
    logo_w, logo_h = logo.size

    # 随机透明度
    opacity = random.uniform(opacity_range[0], opacity_range[1])
    # 调整 logo 透明度
    alpha = logo.getchannel("A")
    alpha = alpha.point(lambda p: int(p * opacity))
    logo.putalpha(alpha)

    # 随机旋转角度
    angle = random.uniform(angle_range[0], angle_range[1])
    rotated_logo = logo.rotate(angle, expand=True, resample=Image.Resampling.BICUBIC)  # pyright: ignore[reportAttributeAccessIssue]

    rot_w, rot_h = rotated_logo.size

    # 如果旋转后的水印大于原图，等比例缩小到原图的 50%
    max_allowed_w = int(img_w * 0.5)
    max_allowed_h = int(img_h * 0.5)
    if rot_w > img_w or rot_h > img_h:
        scale = min(max_allowed_w / rot_w, max_allowed_h / rot_h) if rot_w > 0 and rot_h > 0 else 1.0
        new_w = max(int(rot_w * scale), 1)
        new_h = max(int(rot_h * scale), 1)
        rotated_logo = rotated_logo.resize((new_w, new_h), resample=Image.Resampling.LANCZOS)  # pyright: ignore[reportAttributeAccessIssue]
        rot_w, rot_h = rotated_logo.size

    # 随机位置，确保不超出边界
    max_x = max(img_w - rot_w, 0)
    max_y = max(img_h - rot_h, 0)
    x = random.randint(0, max_x) if max_x > 0 else 0
    y = random.randint(0, max_y) if max_y > 0 else 0

    # 粘贴
    image.paste(rotated_logo, (x, y), rotated_logo)

    # 如果原图不是 RGBA，转回 RGB
    if image.mode == "RGBA":
        # 创建白色背景，避免透明区域
        background = Image.new("RGB", image.size, (255, 255, 255))
        background.paste(image, mask=image.split()[3])
        image = background

    image.save(output_path)
    image.close()
    logo.close()
    rotated_logo.close()

    return output_path


# 文字水印（测试没有通过，文字过小或者不显示，颜色异常）
# def paste_text_watermark(
#     image_path: StrPath,
#     output_path: StrPath,
#     text: str,
#     font_path: StrPath | None = None,
#     font_size: int = 40,
#     opacity_range: tuple[float, float] = (0.15, 0.35),
#     angle_range: tuple[float, float] = (-45.0, 45.0),
#     add_registered_symbol: bool = False,
#     text_color: tuple[int, int, int] | str | None = "random",
# ) -> StrPath:
#     """
#     在图像上随机位置、随机角度、随机透明度添加文字水印。

#     Args:
#         image_path: 原始图像路径
#         output_path: 输出图像路径
#         text: 水印文字内容
#         font_path: 字体文件路径，None 则使用默认字体
#         font_size: 字体大小，默认 40
#         opacity_range: 透明度范围，默认 (0.15, 0.35)
#         angle_range: 旋转角度范围（度），默认 (-45, 45)
#         add_registered_symbol: 是否在文字右上角添加 ® 角标
#         text_color: 文字颜色，支持：
#             - "random" 或 None：从预设颜色中随机选择（默认）
#             - 预设名称字符串："gray"/"orange"/"blue"/"red"
#             - RGB 元组：如 (255, 0, 0)
#     """
#     image = Image.open(image_path).convert("RGBA")
#     img_w, img_h = image.size

#     # 解析颜色
#     if text_color is None or text_color == "random":
#         color = random.choice(list(WATERMARK_COLORS.values()))
#     elif isinstance(text_color, str):
#         color = WATERMARK_COLORS.get(text_color, (128, 128, 128))
#     else:
#         color = text_color

#     # 根据图片尺寸自适应调整字体大小
#     adaptive_font_size = _get_adaptive_font_size(img_w, img_h, font_size)

#     # 加载字体
#     if font_path is not None:
#         font = ImageFont.truetype(str(font_path), adaptive_font_size)
#         if add_registered_symbol:
#             reg_font = ImageFont.truetype(str(font_path), max(int(adaptive_font_size * 0.45), 8))
#         else:
#             reg_font = None
#     else:
#         font = ImageFont.load_default()
#         reg_font = ImageFont.load_default() if add_registered_symbol else None

#     # 计算主文字尺寸
#     draw = ImageDraw.Draw(Image.new("RGBA", (1, 1), (0, 0, 0, 0)))
#     bbox_main = draw.textbbox((0, 0), text, font=font)
#     main_w = bbox_main[2] - bbox_main[0]
#     main_h = bbox_main[3] - bbox_main[1]

#     # 随机透明度
#     opacity = random.uniform(opacity_range[0], opacity_range[1])
#     alpha = int(255 * opacity)
#     fill_color = color + (alpha,)

#     if add_registered_symbol and reg_font is not None and font_path is not None:
#         # 计算 ® 尺寸
#         bbox_reg = draw.textbbox((0, 0), "\u00AE", font=reg_font)
#         reg_w = bbox_reg[2] - bbox_reg[0]
#         reg_h = bbox_reg[3] - bbox_reg[1]

#         # 画布尺寸：主文字宽度 + ® 宽度，高度取较大值并留出上方空间
#         total_w = main_w + reg_w
#         total_h = max(main_h, reg_h + int(adaptive_font_size * 0.15))

#         text_layer = Image.new("RGBA", (int(total_w), int(total_h)), (0, 0, 0, 0))
#         text_draw = ImageDraw.Draw(text_layer)

#         # 主文字基线对齐，放在左下角
#         text_y = total_h - main_h
#         text_draw.text((-bbox_main[0], text_y), text, font=font, fill=fill_color)

#         # ® 放在右上角，与主文字顶部对齐并稍微上浮
#         reg_x = main_w - int(reg_w * 0.15)
#         reg_y = max(0, int(adaptive_font_size * 0.05))
#         text_draw.text((reg_x, reg_y), "\u00AE", font=reg_font, fill=fill_color)
#     else:
#         # 无角标，直接绘制主文字
#         text_layer = Image.new("RGBA", (int(main_w), int(main_h)), (0, 0, 0, 0))
#         text_draw = ImageDraw.Draw(text_layer)
#         text_draw.text((-bbox_main[0], -bbox_main[1]), text, font=font, fill=fill_color)

#     # 随机旋转
#     angle = random.uniform(angle_range[0], angle_range[1])
#     rotated_text = text_layer.rotate(angle, expand=True, resample=Image.Resampling.BICUBIC)  # pyright: ignore[reportAttributeAccessIssue]

#     rot_w, rot_h = rotated_text.size

#     # 如果旋转后的文字大于原图，等比例缩小到原图的 50%
#     max_allowed_w = int(img_w * 0.5)
#     max_allowed_h = int(img_h * 0.5)
#     if rot_w > img_w or rot_h > img_h:
#         scale = min(max_allowed_w / rot_w, max_allowed_h / rot_h) if rot_w > 0 and rot_h > 0 else 1.0
#         new_w = max(int(rot_w * scale), 1)
#         new_h = max(int(rot_h * scale), 1)
#         rotated_text = rotated_text.resize((new_w, new_h), resample=Image.Resampling.LANCZOS)  # pyright: ignore[reportAttributeAccessIssue]
#         rot_w, rot_h = rotated_text.size

#     # 随机位置
#     max_x = max(img_w - rot_w, 0)
#     max_y = max(img_h - rot_h, 0)
#     x = random.randint(0, max_x) if max_x > 0 else 0
#     y = random.randint(0, max_y) if max_y > 0 else 0

#     image.paste(rotated_text, (x, y), rotated_text)

#     # 转回 RGB
#     if image.mode == "RGBA":
#         background = Image.new("RGB", image.size, (255, 255, 255))
#         background.paste(image, mask=image.split()[3])
#         image = background

#     image.save(output_path)
#     image.close()
#     text_layer.close()
#     rotated_text.close()

#     return output_path

