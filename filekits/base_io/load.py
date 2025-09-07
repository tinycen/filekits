import json
import yaml
import base64
import openpyxl
import pandas as pd

# 读取txt文档，返回列表
def load_txt(file_path, lower_list=0, return_type="list"):
    f = open(file_path, "r", encoding='utf-8')
    text = f.read()
    f.close()
    if return_type == "str":
        return text
    else:
        my_list = text.split("\n")
        if lower_list == 1:  # 转换为小写
            new_list = [word.lower() for word in my_list]
            return new_list
        else:
            return my_list


# 读取yaml文件
def load_yaml(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        data = yaml.safe_load(f)
    return data


# 读取Excel文件，返回pandas.DataFrame 或者 sheet
def load_excel(file_path, return_type, sheet_name=None, skiprows=0, header=0):
    '''
    for i in range (2 , num+1) :  # 第1行是 标题，所以从第2行开始
        sku = sheet.cell (i , 2).value
    '''
    if return_type == "sheet":
        wb = openpyxl.load_workbook(file_path)
        sheet = wb.active
        if sheet is not None:
            num = sheet.max_row
        else:
            num = 0
        print("共有行：{}".format(num))
        return wb, sheet, num
    elif return_type == "df":
        if sheet_name is None:
            sheet_name = 0
        df = pd.read_excel(file_path, sheet_name=sheet_name, header=header,
                            skiprows=skiprows if skiprows != 0 else None)
        return df
    else:
        raise ValueError("return_type参数错误！")


# 读取json文件，返回字典
def load_json(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    return data


# 读取任意文件转为 base64 编码
def load_base64(file_path):
    with open(file_path, "rb") as file:
        file_data = file.read()
    base64_data = base64.b64encode(file_data).decode('utf-8')
    return base64_data