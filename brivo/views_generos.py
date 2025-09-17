from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from .constants import GENEROS_SUBGENEROS

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def listar_generos_subgeneros(request):
    """
    Endpoint para listar todos os gêneros e subgêneros disponíveis.
    Retorna a estrutura completa para o frontend.
    """
    return Response({
        'generos_subgeneros': GENEROS_SUBGENEROS,
        'total_generos': len(GENEROS_SUBGENEROS),
        'total_subgeneros': sum(len(subgeneros) for subgeneros in GENEROS_SUBGENEROS.values())
    }, status=status.HTTP_200_OK)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def listar_generos(request):
    """
    Endpoint para listar apenas os gêneros principais.
    """
    generos = list(GENEROS_SUBGENEROS.keys())
    return Response({
        'generos': generos,
        'total': len(generos)
    }, status=status.HTTP_200_OK)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def listar_subgeneros_por_genero(request, genero):
    """
    Endpoint para listar subgêneros de um gênero específico.
    """
    if genero not in GENEROS_SUBGENEROS:
        return Response({
            'erro': f'Gênero "{genero}" não encontrado'
        }, status=status.HTTP_404_NOT_FOUND)
    
    subgeneros = GENEROS_SUBGENEROS[genero]
    return Response({
        'genero': genero,
        'subgeneros': subgeneros,
        'total': len(subgeneros)
    }, status=status.HTTP_200_OK)