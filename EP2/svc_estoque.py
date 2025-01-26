"""
------------------ Exercício de Programação 2 ------------------
Nome: Luiza de Melo Gomes
Matrícula: 2021040075
Disciplina: Fundamentos de Sistemas Paralelos Distribuídos
----------------------------------------------------------------
"""

import grpc
from concurrent import futures
import sys
import estoque_pb2
import estoque_pb2_grpc


class Produto(): 
    def __init__(self, prod_id, descricao, quantidade): 
        self.prod_id = prod_id
        self.descricao = descricao 
        self.quantidade = quantidade

class ServidorEstoque(estoque_pb2_grpc.ServidorServicer):

    def __init__(self, server, *args, **kwargs):
        self.server = server
        self.counter_id = 0
        self.produtos = {}

    def adiciona_produto(self, request, contexto): 
        self.counter_id += 1
        self.produtos[self.counter_id] = Produto(self.counter_id, request.descricao, request.quantidade)
        return estoque_pb2.adiciona_produto_message_response(prod_id=self.counter_id)

    def altera_quantidade_produto(self, request, context):
        
        if request.prod_id not in self.produtos: 
            return estoque_pb2.altera_produto_message_response(status=-2) # Produto inválido

        if self.produtos[request.prod_id].quantidade + request.valor < 0: 
            return estoque_pb2.altera_produto_message_response(status=-1) # Quantidade final inválida

        # Produto válido e quantidade válida
        self.produtos[request.prod_id].quantidade += request.valor
        return estoque_pb2.altera_produto_message_response(status=1)

    def lista_produtos(self, request, context):
        return_list = [estoque_pb2.produto(
            prod_id=produto.prod_id,
            quantidade=produto.quantidade,
            descricao=produto.descricao
        ) 
        for produto in self.produtos.values()
        ]

        return estoque_pb2.lista_produtos_message_response(lista_produtos=return_list)
    
    def termina_execucao(self, request, context):
        num_produtos = len(self.produtos)

        # Espera 1 segundo para terminar de enviar a mensagem para o servidor de pedidos
        self.server.stop(1)
        return estoque_pb2.termina_execucao_message_response(quantidade_produtos=num_produtos)


def serve():

    if len(sys.argv) != 2: 
        print("Usage: python3 svc_estoque.py <porto>")
        sys.exit(1)

    porto = sys.argv[1]

    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    servicer = ServidorEstoque(server) 
    estoque_pb2_grpc.add_ServidorServicer_to_server(servicer, server)
    server.add_insecure_port(f'[::]:{porto}')
    server.start()
    server.wait_for_termination()


if __name__ == '__main__':
    serve()