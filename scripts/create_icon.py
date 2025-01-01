from PIL import Image, ImageDraw, ImageFont
from pathlib import Path

def create_icon():
    # 创建 resources 目录
    root_dir = Path(__file__).parent.parent
    resources_dir = root_dir / 'resources'
    resources_dir.mkdir(exist_ok=True)
    
    # 创建一个 256x256 的图像
    img = Image.new('RGBA', (256, 256), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    
    # 绘制一个简单的图标
    draw.ellipse([20, 20, 236, 236], fill='#2c2c2c')
    draw.ellipse([40, 40, 216, 216], fill='#3c3c3c')
    
    # 添加文字
    try:
        font = ImageFont.truetype("msyh.ttc", 100)  # 使用微软雅黑
    except:
        font = ImageFont.load_default()
    
    draw.text((128, 128), "M", fill='white', font=font, anchor="mm")
    
    # 保存为ico文件
    icon_path = resources_dir / 'icon.ico'
    img.save(str(icon_path), format='ICO')
    print(f"图标已保存到: {icon_path}")

if __name__ == '__main__':
    create_icon() 