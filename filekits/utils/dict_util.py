import json


# 从字典中移除指定的键
def remove_keys(data: dict, keys_to_remove: list) -> dict:
    """从字典中移除指定的键列表
    
    Args:
        data: 要处理的字典
        keys_to_remove: 需要移除的键列表
        
    Returns:
        处理后的字典
    """
    for key in keys_to_remove:
        if key in data:
            del data[key]
    return data


def simplify_dict(data, max_length: int = 15, max_list: int = 3, parse_json_str: bool = False):
    """递归简化字典/列表：截断过长字符串、缩减过长列表

    Args:
        data: 要简化的数据（字典、列表等）
        max_length: 字符串截断阈值，超过时截断并添加省略号
        max_list: 列表/元组保留的最大元素数量，超过时只保留前 N 个
        parse_json_str: 是否尝试将字符串值解析为嵌套 JSON 结构，默认否

    Returns:
        简化后的数据（类型与输入保持一致）
    """

    def _simplify(value):
        if value is None:
            return None
        if isinstance(value, str):
            # 可选：解析嵌套的 JSON 字符串
            if parse_json_str:
                try:
                    parsed = json.loads(value)
                    if isinstance(parsed, (dict, list)):
                        return _simplify(parsed)
                except (json.JSONDecodeError, TypeError):
                    pass
            if len(value) > max_length:
                return value[:max_length] + "..."
            return value
        if isinstance(value, (list, tuple)):
            items = value[:max_list] if len(value) > max_list else value
            result = [_simplify(item) for item in items]
            if len(value) > max_list:
                result.append(f"...(+{len(value) - max_list} more)")
            return result
        if isinstance(value, dict):
            return {k: _simplify(v) for k, v in value.items()}
        return value

    return _simplify(data)