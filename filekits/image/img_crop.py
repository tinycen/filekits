import cv2
import numpy as np
from PIL import Image , ImageDraw
from .img_info import correct_position


# 删除png图片的透明区域
def crop_transparent( image_path , turn_jpg: bool = False ) :
    # 读取图片，包括 alpha 通道
    img = cv2.imread( image_path , cv2.IMREAD_UNCHANGED )
    if img is None :
        raise FileNotFoundError( f"无法读取图片: {image_path}" )
    if img.ndim < 3 or img.shape[ 2 ] < 4 :
        return image_path
    coords = np.argwhere( img[ ... , 3 ] )
    # 计算非透明部分的边界
    x0 , y0 = coords.min( axis = 0 )
    x1 , y1 = coords.max( axis = 0 ) + 1
    # 裁剪图片
    cropped_img = img[ x0 :x1 , y0 :y1 ]
    if cropped_img.size != 0 :
        # 保存裁剪后的图片
        if turn_jpg is False :
            cv2.imwrite( image_path , cropped_img )
        else :
            # 将透明背景转换为白色
            alpha_channel = cropped_img[ : , : , 3 ]
            _ , mask = cv2.threshold( alpha_channel , 0 , 255 , cv2.THRESH_BINARY )  # binarize mask
            color = cropped_img[ : , : , :3 ]
            new_img = cv2.bitwise_not( cv2.bitwise_not( color , mask = mask ) )
            image_path = image_path.rsplit( '.' , 1 )[ 0 ] + '.jpg'
            cv2.imwrite( image_path , new_img )

    return image_path


# 裁剪图像
def crop_image( image_path, modify_info, output_path, save_image = True, return_type = "remaining_image" ) :
    # 加载图片
    original_image = Image.open( image_path )
    crop_area = correct_position( modify_info )
    if crop_area is None :
        raise ValueError( "裁剪区域无效：起始位置与结束位置相同" )
    original_image = original_image.convert( 'RGB' )
    start_x = crop_area[ 'startX' ]
    start_y = crop_area[ 'startY' ]
    end_x = crop_area[ 'endX' ]
    end_y = crop_area[ 'endY' ]

    width, height = original_image.size
    start_x = max( 0, start_x )
    start_y = max( 0, start_y )
    end_x = min( width, end_x )
    end_y = min( height, end_y )

    if return_type == "croped_image" :
        # 根据指定区域从原图中裁剪图像
        remaining_image = original_image.crop( (start_x, start_y, end_x, end_y) )
    else :
        # 获取原始图片的宽和高
        original_width, original_height = original_image.size

        # 如果裁剪区域距离图片的顶部或底部在范围以内，就把宽设置到直达顶部或底部的宽
        if start_y <= 70 :
            remaining_image = original_image.crop( (0, end_y, original_width, original_height) )
        elif original_height - end_y <= 70 :
            remaining_image = original_image.crop( (0, 0, original_width, end_y) )
        else :
            raise Exception( "没有合适的裁剪区域：距离顶部或底部>70px" )

    if save_image :
        # 保存剩余的图片
        remaining_image.save( output_path )
        original_image.close()
        return None
    else :
        return remaining_image


# 同时裁剪多个区域，保留剩下的区域
def multi_crop_image( image_path, output_path, multi_regionCrop = None ) :
    # 加载图片
    if multi_regionCrop is None :
        multi_regionCrop = [ ]
    original_image = Image.open( image_path ).convert( 'RGB' )
    width, height = original_image.size

    # 创建一个全白图像（白色表示保留）
    mask = Image.new( 'RGBA', (width, height), color = (255, 255, 255) )
    # 创建一个可以在图片上绘制的对象
    draw = ImageDraw.Draw( mask )
    # 遍历每一个需要裁剪的区域
    for modify_info in multi_regionCrop :
        crop_area = correct_position( modify_info )
        if crop_area is None :
            continue
        start_x = crop_area[ 'startX' ]
        start_y = crop_area[ 'startY' ]
        end_x = crop_area[ 'endX' ]
        end_y = crop_area[ 'endY' ]

        start_x = round( max( 0, start_x ) )
        start_y = round( max( 0, start_y ) )
        end_x = round( min( width, end_x ) )
        end_y = round( min( height, end_y ) )

        # 如果裁剪区域距离图片的顶部或底部在30px以内，就把高设置到直达顶部或底部的高
        if start_y <= 30 :
            start_x = start_y = 0
            end_x = width
        elif height - end_y <= 30 :
            start_x = 0
            end_y = height
            end_x = width
        # 删除mask指定区域的像素（改为透明）
        draw.rectangle( [ (start_x, start_y), (end_x, end_y) ], fill = (0,) )

    # 将遮罩与原始图像进行"乘法"操作，从而达到裁剪的效果
    remaining_image = Image.composite( original_image, Image.new( 'RGBA', original_image.size ), mask )
    multi_crop_imagePath = output_path.rsplit( '.', 1 )[ 0 ] + '.png'
    remaining_image.save( multi_crop_imagePath )
    output_path = crop_transparent( multi_crop_imagePath, turn_jpg = True )
    original_image.close()
    return output_path

