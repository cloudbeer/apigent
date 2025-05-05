from pygments import highlight
from pygments.lexers import PythonLexer
from pygments.formatters import ImageFormatter
from PIL import Image
import io

def code_to_image(code: str, output_path: str, style: str = "monokai", font_size: int = 14):
    """
    将代码转换为图片
    
    Args:
        code: 要转换的代码字符串
        output_path: 输出图片的路径
        style: 代码高亮样式
        font_size: 字体大小
    """
    # 使用 pygments 进行代码高亮
    formatter = ImageFormatter(
        style=style,
        font_name="Menlo",  # macOS 系统默认等宽字体
        font_size=font_size,
        line_numbers=True,
        line_number_bg="#2d2d2d",
        line_number_fg="#999999",
        line_number_pad=10,
        line_pad=5,
        image_pad=20,
        image_bg="#2d2d2d"
    )
    
    # 生成高亮后的图片数据
    image_data = highlight(code, PythonLexer(), formatter)
    
    # 将图片数据转换为 PIL Image 对象
    image = Image.open(io.BytesIO(image_data))
    
    # 保存图片
    image.save(output_path) 