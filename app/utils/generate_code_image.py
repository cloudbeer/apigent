from code_to_image import code_to_image

# 读取 pg.py 文件内容
with open("app/utils/pg.py", "r", encoding="utf-8") as f:
    code = f.read()

# 生成图片
code_to_image(
    code=code,
    output_path="pg_code.png",
    style="monokai",
    font_size=14
) 