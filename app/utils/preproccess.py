import app.utils.pg as db

def get_tool_schema(tool_id: int):
    tool = db.get_by_id("apigent_tool", tool_id)
    if not tool:
        raise Exception(f"Tool not found: {tool_id}")
    
    conditions = db.QueryCondition(
        limit=1000,
        where="tool_id = %s",
        params=(tool_id,),
        order_by="id ASC"
    )
    fields = db.list("apigent_field", conditions)
    # if not fields:
    #     raise Exception(f"Fields not found: {tool_id}")
    
    # 构建参数 schema
    properties = {}
    required = []
    for field in fields:
        param = {
            "type": field["data_type"],
            "description": field["description"]
        }
        
        # 添加格式信息
        if field["format"]:
            param["format"] = field["format"]
            
        # 处理数组类型
        if field["is_array"]:
            param["type"] = "array"
            param["items"] = {
                "type": field["array_items_type"]
            }
            if field["array_items_format"]:
                param["items"]["format"] = field["array_items_format"]
                
        # 添加枚举值
        if field["enum_values"]:
            param["enum"] = field["enum_values"]
            
        properties[field["name"]] = param
        
        # 添加必填字段
        if field["is_required"]:
            required.append(field["name"])
    
    # 构建函数 schema
    function_schema = {
        "type": "function",
        "function": {
            "name": tool["name"],
            "key": tool["key"],
            "description": tool["description"],
            "parameters": {
                "type": "object",
                "properties": properties,
                "required": required
            }
        }
    }
    
    return function_schema

