import os
from typing import TypedDict

from PIL import Image, ImageDraw, ImageFont, ImageStat

from ..base_io import StrPath
from .img_info import is_dark_color


# ---------------------------------------------------------------------------
# 类型别名
# ---------------------------------------------------------------------------

class RectRegion(TypedDict):
    startX: int
    startY: int
    endX:   int
    endY:   int


# ---------------------------------------------------------------------------
# 私有辅助函数
# ---------------------------------------------------------------------------


def _expand_polygon(
    vertices: list[tuple[float, float]],
    expand_px: int,
    canvas_size: tuple[int, int],
) -> list[tuple[float, float]]:
    """
    将多边形的每个顶点沿「顶点→质心」反方向（即向外）移动 *expand_px* 像素。

    结果坐标会被裁剪到 *canvas_size* = (width, height) 范围内。
    """
    width, height = canvas_size
    cx = sum(p[0] for p in vertices) / len(vertices)
    cy = sum(p[1] for p in vertices) / len(vertices)

    expanded: list[tuple[float, float]] = []
    for x, y in vertices:
        dx, dy = x - cx, y - cy
        dist = (dx ** 2 + dy ** 2) ** 0.5
        if dist < 1e-6:
            ex, ey = x, y
        else:
            ex = x + (dx / dist) * expand_px
            ey = y + (dy / dist) * expand_px
        ex = max(0.0, min(width  - 1, ex))
        ey = max(0.0, min(height - 1, ey))
        expanded.append((ex, ey))

    return expanded


# ---------------------------------------------------------------------------
# 公开函数
# ---------------------------------------------------------------------------

def create_rect_mask(
    img_path: StrPath,
    rect: RectRegion,
    mask_path: StrPath,
    crop_dir: StrPath,
    crop_expansion: int = 200,
) -> tuple[str, RectRegion]:
    """
    生成矩形 mask：*rect* 内部填白色，其余填黑色。

    当 *crop_expansion* > 0 时，会以 *rect* 为中心向外各扩展 *crop_expansion*
    像素裁剪出一个小图块（保存到 *crop_dir*/cropped_image.jpg），mask 也只覆盖
    该图块，从而减少后续 inpainting 的显存占用。

    Parameters
    ----------
    img_path       : 原始图片路径
    rect           : 目标矩形区域 {"startX", "startY", "endX", "endY"}
    mask_path      : mask 图像的保存路径
    crop_dir       : 裁剪小图块的输出目录（crop_expansion > 0 时使用）
    crop_expansion : 裁剪时在 rect 四周额外保留的像素数；
                     为 0 时生成与原图等大的 mask，不裁剪

    Returns
    -------
    (cropped_img_path, crop_rect)
    - cropped_img_path : 裁剪小图块的路径；crop_expansion == 0 时返回 ""
    - crop_rect        : 图块在原图中的坐标；crop_expansion == 0 时返回原始 rect
    """
    # 归一化：确保左上角 < 右下角
    x0 = min(rect['startX'], rect['endX'])
    y0 = min(rect['startY'], rect['endY'])
    x1 = max(rect['startX'], rect['endX'])
    y1 = max(rect['startY'], rect['endY'])

    img = Image.open(img_path)
    img_w, img_h = img.size

    if crop_expansion == 0:
        # 生成与原图等大的 纯黑色 mask
        canvas = Image.new('RGB', (img_w, img_h), color=(0, 0, 0))
        cropped_img_path = ""
        crop_rect: RectRegion = rect
        draw_x0, draw_y0, draw_x1, draw_y1 = x0, y0, x1, y1
    else:
        # 计算裁剪窗口（不超出图片边界）
        crop_x0 = max(0,      x0 - crop_expansion)
        crop_y0 = max(0,      y0 - crop_expansion)
        crop_x1 = min(img_w,  x1 + crop_expansion)
        crop_y1 = min(img_h,  y1 + crop_expansion)

        crop_rect = {
            'startX': crop_x0, 'startY': crop_y0,
            'endX':   crop_x1, 'endY':   crop_y1,
        }

        tile = img.crop((crop_x0, crop_y0, crop_x1, crop_y1)).convert('RGB')
        # 生成与图块等大的 纯黑色 mask
        canvas = Image.new('RGB', tile.size, color=(0, 0, 0))

        # 将 rect 坐标转换到图块局部坐标系
        draw_x0, draw_y0 = x0 - crop_x0, y0 - crop_y0
        draw_x1, draw_y1 = x1 - crop_x0, y1 - crop_y0

        cropped_img_path = os.path.join(str(crop_dir), 'cropped_image.jpg')
        tile.save(cropped_img_path)

    img.close()

    ImageDraw.Draw(canvas).rectangle(
        [(draw_x0, draw_y0), (draw_x1, draw_y1)],
        fill=(255, 255, 255),
    )
    canvas.save(mask_path)

    return cropped_img_path, crop_rect


def create_polygon_mask(
    img_path: StrPath,
    polygons: list[list[tuple[float, float]]],
    mask_path: StrPath,
    expand_px: int = 20,
) -> StrPath | Image.Image:
    """
    生成多边形 mask：每个多边形内部填白色，其余填黑色。

    始终生成与原图等大的 mask，不做裁剪。

    Parameters
    ----------
    img_path  : 原始图片路径（仅用于获取画布尺寸）
    polygons  : 多边形列表，每个多边形为 [(x1,y1), (x2,y2), ...] 顶点序列
    mask_path : mask 图像的保存路径；传入 "" 时不保存，直接返回 Image 对象
    expand_px : 多边形各顶点向外扩展的像素数

    Returns
    -------
    mask_path 不为空时返回保存路径；为空时返回内存中的 Image.Image 对象。
    """
    img = Image.open(img_path)
    canvas_size = img.size
    img.close()

    # 生成与原图等大的 纯黑色 mask
    canvas = Image.new('RGB', canvas_size, color=(0, 0, 0))
    draw = ImageDraw.Draw(canvas)

    for polygon in polygons:
        expanded = _expand_polygon(polygon, expand_px, canvas_size)
        draw.polygon(expanded, fill=(255, 255, 255))

    if mask_path:
        canvas.save(mask_path)
        return mask_path
    return canvas


def add_text(
    img: StrPath | Image.Image,
    box_infos: list[dict],
    font_path: dict,
    output_path: StrPath = 'add_text.jpg',
) -> StrPath:
    """
    将文字绘制到图片的指定区域，自动适配横排 / 竖排及字号。

    Parameters
    ----------
    img         : 图片路径或已打开的 Image 对象
    box_infos   : 文字区域列表，每项包含 "text_translated"、"box"、
                  "width"、"height"、"short_side" 字段
    font_path   : 字体文件路径字典，包含 "Bold" 和 "Medium" 两个键
    output_path : 输出图片路径
    """
    image = img if isinstance(img, Image.Image) else Image.open(img)
    draw = ImageDraw.Draw(image)

    for box_info in box_infos:
        text      = box_info['text_translated']
        box       = box_info['box']
        box_w     = box_info['width']
        box_h     = box_info['height']
        wh_ratio  = box_w / box_h

        left_x  = min(p[0] for p in box)
        right_x = max(p[0] for p in box)
        top_y   = min(p[1] for p in box)
        bottom_y = max(p[1] for p in box)

        # 字体选择
        short_side  = box_info['short_side']
        font_file   = font_path['Bold'] if short_side >= 30 else font_path['Medium']

        # 根据背景亮度决定文字颜色
        avg_color  = ImageStat.Stat(image.crop((left_x, top_y, right_x, bottom_y))).mean[:3]
        font_color = (255, 255, 255) if is_dark_color(avg_color) else (0, 0, 0)

        # 竖排时逐字换行
        display_text = '\n'.join(text) if wh_ratio < 0.5 else text

        # 二分查找最大适配字号
        lo, hi, best_size = 2, 50, 0
        while lo <= hi:
            mid  = (lo + hi) // 2
            font = ImageFont.truetype(font_file, mid)
            l, t, r, b = draw.textbbox((0, 0), display_text, font=font)
            if (r - l) <= box_w and (b - t) <= box_h:
                best_size = mid
                lo = mid + 1
            else:
                hi = mid - 1

        if best_size == 0:
            print(f"Warning: Text '{text}' is too small to fit in box ({box_w}x{box_h}).")
            continue  # 任何字号都放不下，跳过

        font = ImageFont.truetype(font_file, best_size)
        _, t, _, b = draw.textbbox((0, 0), display_text, font=font)
        # 左对齐、垂直居中
        x = int(left_x)
        y = int((top_y + bottom_y) / 2 - (b - t) / 2)
        draw.text((x, y), display_text, font=font, fill=font_color)

    image.save(output_path)
    return output_path
