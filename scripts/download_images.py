import json
import requests
from pathlib import Path
import concurrent.futures

def download_image(img_data):
    try:
        file_name = img_data['file_name']
        # 从服务器获取图片URL
        response = requests.get(f"https://mygoapi.miyago9267.com/mygo/img?keyword={img_data['name']}")
        if response.status_code == 200:
            data = response.json()
            if data['urls']:
                img_url = data['urls'][0]['url']
                img_response = requests.get(img_url)
                if img_response.status_code == 200:
                    img_path = Path(__file__).parent.parent / 'images' / file_name
                    img_path.write_bytes(img_response.content)
                    print(f"Downloaded: {file_name}")
                    return True
    except Exception as e:
        print(f"Error downloading {file_name}: {e}")
    return False

def main():
    # 创建images目录
    images_dir = Path(__file__).parent.parent / 'images'
    images_dir.mkdir(exist_ok=True)
    
    # 读取图片映射
    map_path = Path(__file__).parent.parent / 'data' / 'image_map.json'
    with open(map_path, 'r', encoding='utf-8') as f:
        image_map = json.load(f)
    
    # 并行下载图片
    with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
        results = list(executor.map(download_image, image_map))
    
    success = sum(1 for r in results if r)
    print(f"\nDownloaded {success} of {len(image_map)} images")

if __name__ == "__main__":
    main() 