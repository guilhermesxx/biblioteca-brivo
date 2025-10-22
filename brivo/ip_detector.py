import socket
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

@csrf_exempt
def get_current_ip(request):
    """Retorna o IP atual do servidor"""
    try:
        # Conecta a um servidor externo para descobrir o IP local
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return JsonResponse({'ip': ip, 'expo_url': f'exp://{ip}:8081'})
    except:
        return JsonResponse({'ip': '172.30.1.109', 'expo_url': 'exp://192.168.1.100:8081'})