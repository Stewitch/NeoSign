from django.http import FileResponse, HttpResponse, Http404
from django.views import View
from PIL import Image
import io

from .models import SystemConfig


class FaviconView(View):
    """动态生成favicon.ico"""
    
    def get(self, request):
        try:
            config = SystemConfig.objects.first()
            if not config or not config.site_logo:
                raise Http404("No favicon available")
            
            # 读取上传的logo
            logo_path = config.site_logo.path
            
            # 打开图片并转换为favicon大小
            with Image.open(logo_path) as img:
                # 转换为RGBA以支持透明度
                img = img.convert('RGBA')
                # 调整大小为32x32（favicon标准大小）
                img.thumbnail((32, 32), Image.Resampling.LANCZOS)
                
                # 创建一个新的32x32图片，居中放置缩略图
                favicon = Image.new('RGBA', (32, 32), (0, 0, 0, 0))
                offset = ((32 - img.size[0]) // 2, (32 - img.size[1]) // 2)
                favicon.paste(img, offset)
                
                # 保存为ICO格式
                buffer = io.BytesIO()
                favicon.save(buffer, format='ICO', sizes=[(32, 32)])
                buffer.seek(0)
                
                response = HttpResponse(buffer.getvalue(), content_type='image/x-icon')
                # 设置缓存控制头：验证器驱动的缓存，确保更新时立即刷新
                response['Cache-Control'] = 'public, max-age=86400, must-revalidate'
                response['ETag'] = f'"{config.site_logo.name}:{hash(config.site_logo.name)}"'
                return response
                
        except Exception as e:
            raise Http404(f"Error generating favicon: {str(e)}")
