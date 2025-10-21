#!/usr/bin/env python
"""
🚀 BRIVO AUTO-START SYSTEM
Sistema inteligente que detecta IP e sincroniza automaticamente
"""
import socket
import os
import sys
import subprocess
from pathlib import Path

def detect_current_ip():
    """Detecta IP atual da rede"""
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except:
        return "192.168.1.100"

def main():
    print("🚀 BRIVO AUTO-START SYSTEM")
    print("=" * 50)
    
    # Detecta IP
    current_ip = detect_current_ip()
    print(f"🔍 IP detectado: {current_ip}")
    
    # Executa comando customizado
    print("🔄 Sincronizando arquivos...")
    try:
        subprocess.run([
            sys.executable, 'manage.py', 'runserver_auto', '--port=8000'
        ], check=True)
    except subprocess.CalledProcessError as e:
        print(f"❌ Erro: {e}")
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main())