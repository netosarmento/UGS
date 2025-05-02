# developed: Neto Sarmento.
# Instagram: nort_dev

from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
import requests


### CHAMANDO API CNS (carteira SUS) ###


class CNSView(APIView):
    def get(self, request, cns):
        # URL da API do SUS (substitua pela URL real)
        url = f'https://api.sus.gov.br/v1/cns/{cns}'  # Exemplo de URL real
        
        
        
        try:
            response = requests.get(url)
            response.raise_for_status()  # Levanta um erro para códigos de status HTTP 4xx/5xx
            data = response.json()  # Converte a resposta em JSON
            print(response.status_code)
            print(response.json())  
            return Response(data, status=status.HTTP_200_OK)
        except requests.exceptions.HTTPError as http_err:
            return Response({'error': str(http_err)}, status=response.status_code)
        except Exception as err:
            return Response({'error': str(err)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        

def buscar_cns_view(request):
    dados_paciente = None

    if request.method == 'POST':
        cns = request.POST.get('numero_cns')
        if cns:
            try:
                response = requests.get(f'http://127.0.0.1:8000/api/cns/{cns}/')
                if response.status_code == 200:
                    dados_paciente = response.json()
                else:
                    dados_paciente = {'error': 'CNS não encontrado ou inválido.'}
            except Exception as e:
                dados_paciente = {'error': str(e)}

    return render(request, 'api/buscar_cns.html', {'dados_paciente': dados_paciente})


### CHAMANDO API PEC ###

def dados_cidadao_view(request):
    cns = request.GET.get('cns')  # <- vindo da URL /dados-paciente/?cns=...
    if not cns:
        return render(request, 'api/erro.html', {'erro': 'CNS não informado'})

    url = f'https://api.saude.gov.br/pec/pacientes/{cns}'
    cert = ('/caminho/para/certificado.crt', '/caminho/para/chave.key')

    try:
        response = requests.get(url, cert=cert)
        if response.status_code == 200:
            dados = response.json()
            return render(request, 'api/dados_cidadao.html', {'dados': dados})
        else:
            return render(request, 'api/erro.html', {'erro': f'Erro {response.status_code}'})
    except Exception as e:
        return render(request, 'api/erro.html', {'erro': str(e)})