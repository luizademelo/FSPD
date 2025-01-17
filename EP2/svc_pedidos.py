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
import pedidos_pb2
import pedidos_pb2_grpc
import estoque_pb2
import estoque_pb2_grpc


class ServidorPedidos(pedidos_pb2_grpc.ServidorPedidosServicer):
    def __init__(self, server, estoque_server_address):

        self.server = server

        # Conectando com o servidor de estoque
        self.estoque_channel = grpc.insecure_channel(estoque_server_address)
        self.estoque_stub = estoque_pb2_grpc.ServidorStub(self.estoque_channel)

        self.pedidos = {}
        self.pedido_counter = 1

    def cria_pedido(self, request, context):
        resultado_pedido = []
        pedido_id = self.pedido_counter
        self.pedido_counter += 1

        for item in request.itens:
            prod_id, quantidade = item.prod_id, item.quantidade
            response = self.estoque_stub.altera_quantidade_produto(
                estoque_pb2.altera_produto_message(prod_id=prod_id,valor=-quantidade)
            )
            if response.status == 1:  # Sucesso
                resultado_pedido.append((prod_id, 0, quantidade))
            else: # Quantidade inválida
                resultado_pedido.append((prod_id, response.status, quantidade)) 

        self.pedidos[pedido_id] = {"itens": resultado_pedido}


        return pedidos_pb2.cria_pedido_response(
            pedido_id=pedido_id,
            resultado=[
                pedidos_pb2.resultado_item(prod_id=prod_id, status=status)
                for prod_id, status, _ in resultado_pedido
            ],
        )

    def cancela_pedido(self, request, context):
        pedido_id = request.pedido_id
        
        if pedido_id not in self.pedidos: 
            # Pedido não está na lista de pedidos
            return pedidos_pb2.cancela_pedido_response(status=-1)

        pedido = self.pedidos[pedido_id]
        
        # Devolvendo os itens para o estoque
        for prod_id, status, quantidade in pedido["itens"]:
            if status == 0:  # Selecionando somente itens que foram reservados
                self.estoque_stub.altera_quantidade_produto(
                    estoque_pb2.altera_produto_message(prod_id=prod_id, valor=quantidade)
                )

        del self.pedidos[pedido_id]  # Removendo o pedido 
        return pedidos_pb2.cancela_pedido_response(status=0)

    def fim_da_execucao(self, request, context):
        # Terminar o servidor de estoque
            # Solicita ao servidor de estoque para terminar a execução
        response_estoque = self.estoque_stub.termina_execucao(estoque_pb2.termina_execucao_message())

        # Conta os pedidos ativos
        num_pedidos_ativos = len(self.pedidos)

        # Cria a resposta antes de fechar o canal
        response = pedidos_pb2.fim_da_execucao_response(
            estoque_quantidade=response_estoque.quantidade_produtos,
            pedidos_ativos=num_pedidos_ativos,
        )

        # Fecha o canal do estoque de maneira ordenada
        self.estoque_channel.close()

        # Para o servidor local de pedidos
        self.server.stop(0)

        return response


def serve():

    if len(sys.argv) != 3:
        print("Usage: python svc_perdidos.py <porto> <endereco_estoque>")
        sys.exit(1)

    porto = sys.argv[1] # Primeiro argumento
    endereco_estoque = sys.argv[2] # Segundo argumento

    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    pedidos_pb2_grpc.add_ServidorPedidosServicer_to_server(ServidorPedidos(server, endereco_estoque), server)
    server.add_insecure_port(f"[::]:{porto}")
    server.start()
    server.wait_for_termination()


if __name__ == "__main__": 
    serve()