from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
import json
from .models import Usuario

@csrf_exempt
@require_http_methods(["POST"])
def simple_create_user(request):
    try:
        data = json.loads(request.body)
        
        # Log dos dados recebidos
        print(f"Dados recebidos: {data}")
        
        # Criar usuário diretamente
        usuario = Usuario.objects.create_user(
            ra=data['ra'],
            nome=data['nome'],
            email=data['email'],
            turma=data['turma'],
            tipo=data['tipo'],
            password=data['senha']
        )
        
        return JsonResponse({
            'success': True,
            'user_id': usuario.id,
            'nome': usuario.nome,
            'email': usuario.email
        })
        
    except Exception as e:
        print(f"Erro: {str(e)}")
        return JsonResponse({
            'error': str(e)
        }, status=400)

@csrf_exempt
@require_http_methods(["GET"])
def test_endpoint(request):
    return JsonResponse({'message': 'Endpoint funcionando'})