# 判断颜色是否为深色
def is_dark_color( rgb ) :
    # 简单亮度判断公式，可根据需要调整
    brightness = sum( rgb ) / 3
    return brightness < 128


# 获得正确的位置
def correct_position( modify_info, return_type = "VOC" ) :
    #  box 矩形框，可能是左上到右下划的，也有可能 是右下到左上等，所以再此进行纠正
    startX = round( modify_info[ 'startX' ] )
    startY = round( modify_info[ 'startY' ] )
    endX = round( modify_info[ 'endX' ] )
    endY = round( modify_info[ 'endY' ] )
    if startX == endX and startY == endY :
        print( f"图像尺寸有误(裁剪开始位置=结束位置)：{modify_info}" )
        return None

    # 检查并修正左上角和右下角的位置
    if startX > endX :
        startX, endX = endX, startX
    if startY > endY :
        startY, endY = endY, startY

    modify_info[ 'startX' ] = startX
    modify_info[ 'startY' ] = startY
    modify_info[ 'endX' ] = endX
    modify_info[ 'endY' ] = endY

    if return_type == "VOC" :
        return modify_info

    elif return_type == "COCO" :
        width = endX - startX
        height = endY - startY
        area = width * height
        modify_info[ 'bbox' ] = [ startX, startY, width, height ]
        modify_info[ 'area' ] = area
        return modify_info
    return None