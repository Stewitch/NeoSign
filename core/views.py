from django.http import FileResponse, HttpResponse, Http404, JsonResponse
from django.views import View
from django.conf import settings
from PIL import Image
import io
import os

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
                response['Cache-Control'] = 'public, max-age=3600'  # 缓存1小时
                return response
                
        except Exception as e:
            raise Http404(f"Error generating favicon: {str(e)}")


class AmapSecurityKeyView(View):
    """代理高德地图安全密钥，避免直接暴露在前端"""
    
    def get(self, request):
        # 检查是否启用 nginx 代理模式
        if settings.AMAP_PROXY_MODE != 'nginx':
            return JsonResponse({'error': 'Proxy mode not enabled'}, status=403)
        
        try:
            config = SystemConfig.objects.first()
            if not config or not config.map_security_key:
                return JsonResponse({'error': 'Security key not configured'}, status=404)
            
            # 返回安全密钥（仅当通过 nginx 代理时）
            response = JsonResponse({
                'securityJsCode': config.map_security_key
            })
            response['Cache-Control'] = 'public, max-age=3600'
            return response
            
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
