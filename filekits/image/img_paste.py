# import cv2
# import numpy as np
from ..base_io import load_image

# 粘贴图像
def paste_image( original_image , paste_img , box , backend = "PIL" ):
    original_image = load_image( original_image , backend )
    paste_img = load_image( paste_img , backend )

    if backend == "PIL" :
        rounded_box = tuple( round( element ) if isinstance( element , float ) else element for element in box )
        # isinstance(element, float) 是用来判断元素是否为浮点数类型，如果是则执行四舍五入操作，否则保持原样。
        original_image.paste( paste_img , rounded_box )     # pyright: ignore[reportAttributeAccessIssue]

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
