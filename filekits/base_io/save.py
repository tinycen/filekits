import json
import pandas as pd

# 将列表转为df并保存为指定格式的文件
def save_df( merged_list , output_path ) :
    df = pd.DataFrame( merged_list )
    if ".xlsx" in output_path :
        df.to_excel( output_path , index = False )
    elif ".csv" in output_path :
        df.to_csv( output_path , index = False )
    elif ".json" in output_path :
        df.to_json( output_path , orient = 'records' , force_ascii = False , indent = 4 )
    else :
        raise ValueError( "请输入正确的文件名后缀，支持 .xlsx、.csv 和 .json " )
    return

# 字典保存为json文件
def save_json( data_dict, output_file = 'output.json' ) :
    # 将字典转换为JSON格式字符串
    json_str = json.dumps( data_dict, ensure_ascii = False, indent = 4 )
    # 打开文件，以写入模式打开
    with open( output_file, 'w', encoding = 'utf-8' ) as f :
        # 将JSON字符串写入文件
        f.write( json_str )


# 列表保存为txt文件
def save_txt( merged_list , output_file = 'output.txt' ) :
    with open( output_file , 'w' , encoding = 'utf-8' ) as f :
        for item in merged_list :
            f.write( str( item ) + '\n' )