import socket
import os
import re
from pathlib import Path
from django.core.management.base import BaseCommand
from django.core.management import execute_from_command_line
from django.conf import settings

class Command(BaseCommand):
    help = '🚀 Inicia servidor com detecção automática de IP e atualização de arquivos'

    def add_arguments(self, parser):
        parser.add_argument('--port', type=str, default='8000', help='Porta do servidor')

    def handle(self, *args, **options):
        port = options['port']
        
        # 1. Detecta IP atual
        current_ip = self.detect_current_ip()
        self.stdout.write(f"🔍 IP detectado: {current_ip}")
        
        # 2. Atualiza arquivos automaticamente
        self.update_backend_files(current_ip)
        self.update_frontend_files(current_ip)
        
        # 3. Inicia servidor
        self.stdout.write(f"🚀 Iniciando servidor em {current_ip}:{port}")
        execute_from_command_line(['manage.py', 'runserver', f'0.0.0.0:{port}'])

    def detect_current_ip(self):
        """Detecta o IP atual da máquina na rede local"""
        try:
            # Conecta a um servidor externo para descobrir IP local
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.connect(("8.8.8.8", 80))
            ip = s.getsockname()[0]
            s.close()
            return ip
        except:
            return "192.168.1.100"  # Fallback

    def update_backend_files(self, new_ip):
        """Atualiza arquivos do backend com novo IP"""
        base_dir = Path(settings.BASE_DIR)
        
        # Atualiza .env
        env_file = base_dir / '.env'
        if env_file.exists():
            content = env_file.read_text(encoding='utf-8')
            # Atualiza ALLOWED_HOSTS
            content = re.sub(
                r'DJANGO_ALLOWED_HOSTS=.*',
                f'DJANGO_ALLOWED_HOSTS=127.0.0.1,{new_ip},localhost,192.168.100.235,172.30.1.109,172.30.1.85,172.30.1.144,10.133.196.163,172.30.1.87',
                content
            )
            env_file.write_text(content, encoding='utf-8')
            self.stdout.write(f"✅ Atualizado .env com IP: {new_ip}")

        # Atualiza ip_detector.py
        ip_detector_file = base_dir / 'brivo' / 'ip_detector.py'
        if ip_detector_file.exists():
            content = ip_detector_file.read_text(encoding='utf-8')
            # Atualiza IP de fallback
            content = re.sub(
                r"return JsonResponse\(\{'ip': '.*?', 'expo_url':",
                f"return JsonResponse({{'ip': '{new_ip}', 'expo_url':",
                content
            )
            ip_detector_file.write_text(content, encoding='utf-8')
            self.stdout.write(f"✅ Atualizado ip_detector.py")

    def update_frontend_files(self, new_ip):
        """Atualiza arquivos do frontend com novo IP"""
        # Caminho para o frontend (assumindo estrutura do projeto)
        frontend_dir = Path(settings.BASE_DIR).parent / 'Brivo-mobile'
        
        if not frontend_dir.exists():
            self.stdout.write("⚠️ Diretório frontend não encontrado")
            return

        # Atualiza api.ts
        api_file = frontend_dir / 'services' / 'api.ts'
        if api_file.exists():
            content = api_file.read_text(encoding='utf-8')
            
            # Atualiza BASE_URL hardcoded
            content = re.sub(
                r"const BASE_URL = 'http://.*?:8000';",
                f"const BASE_URL = 'http://{new_ip}:8000';",
                content
            )
            
            # Atualiza IP padrão na função getBaseURL
            content = re.sub(
                r"return savedIP \? `http://\$\{savedIP\}` : 'http://.*?:8000';",
                f"return savedIP ? `http://${{savedIP}}` : 'http://{new_ip}:8000';",
                content
            )
            
            # Atualiza fallback
            content = re.sub(
                r"return 'http://.*?:8000';",
                f"return 'http://{new_ip}:8000';",
                content
            )
            
            api_file.write_text(content, encoding='utf-8')
            self.stdout.write(f"✅ Atualizado api.ts com IP: {new_ip}")

        # Atualiza useDeepLink.ts
        deeplink_file = frontend_dir / 'hooks' / 'useDeepLink.ts'
        if deeplink_file.exists():
            content = deeplink_file.read_text(encoding='utf-8')
            
            # Atualiza lista de IPs comuns
            content = re.sub(
                r"const commonIPs = \[[\s\S]*?\];",
                f"""const commonIPs = [
        '{new_ip}:8000',
        '192.168.1.100:8000',
        '192.168.0.100:8000', 
        '192.168.100.235:8000',
        '10.0.0.100:8000',
        '172.16.0.100:8000'
      ];""",
                content
            )
            
            # Atualiza IP padrão de fallback
            content = re.sub(
                r"return '.*?:8000';",
                f"return '{new_ip}:8000';",
                content
            )
            
            deeplink_file.write_text(content, encoding='utf-8')
            self.stdout.write(f"✅ Atualizado useDeepLink.ts")

        # Atualiza QR Code system
        qr_generator_file = frontend_dir / 'qr-system' / 'qr-generator.js'
        if qr_generator_file.exists():
            content = qr_generator_file.read_text(encoding='utf-8')
            
            # Força o IP detectado no QR generator
            content = re.sub(
                r"getLocalIP\(\) \{[\s\S]*?return 'localhost';",
                f"""getLocalIP() {{
        // IP detectado automaticamente pelo sistema Django
        return '{new_ip}';""",
                content
            )
            
            qr_generator_file.write_text(content, encoding='utf-8')
            self.stdout.write(f"✅ Atualizado qr-generator.js")

        # Atualiza qrcode.html
        qrcode_file = frontend_dir / 'qrcode.html'
        if qrcode_file.exists():
            content = qrcode_file.read_text(encoding='utf-8')
            
            # Atualiza IPs possíveis
            content = re.sub(
                r"const possibleIPs = \[.*?\];",
                f"const possibleIPs = ['{new_ip}', 'localhost', '127.0.0.1', '192.168.1.100', '192.168.0.100', '192.168.100.235'];",
                content
            )
            
            # Atualiza fallback
            content = re.sub(
                r"return 'exp://.*?:8081';",
                f"return 'exp://{new_ip}:8081';",
                content
            )
            
            qrcode_file.write_text(content, encoding='utf-8')
            self.stdout.write(f"✅ Atualizado qrcode.html")

        self.stdout.write(f"🎯 Todos os arquivos sincronizados com IP: {new_ip}")