"""
------------------ Exercício de Programação 2 ------------------
Nome: Luiza de Melo Gomes
Matrícula: 2021040075
Disciplina: Fundamentos de Sistemas Paralelos Distribuídos
----------------------------------------------------------------
"""


import grpc
import pedidos_pb2
import pedidos_pb2_grpc
import estoque_pb2
import estoque_pb2_grpc


def run():
    import sys

    if len(sys.argv) != 3:
        print("Uso: python3 cliente_pedidos.py <endereco_estoque> <endereco_pedidos>")
        sys.exit(1)

    endereco_estoque = sys.argv[1]
    endereco_pedidos = sys.argv[2]

    estoque_channel = grpc.insecure_channel(endereco_estoque)
    estoque_stub = estoque_pb2_grpc.ServidorStub(estoque_channel)

    pedidos_channel = grpc.insecure_channel(endereco_pedidos)
    pedidos_stub = pedidos_pb2_grpc.ServidorPedidosStub(pedidos_channel)

    # Lendo comandos da entrada padrão
    while True:
        linha = input().strip()

        if linha.startswith("P "):  # Cria pedido
            partes = linha.split()[1:]
            itens = [
                pedidos_pb2.item(prod_id=int(partes[i]), quantidade=int(partes[i + 1]))
                for i in range(0, len(partes), 2)
            ]
            response = pedidos_stub.cria_pedido(pedidos_pb2.cria_pedido_request(itens=itens))
            for item in response.resultado:
                print(item.prod_id, item.status)
                
        elif linha.startswith("X "):  # Cancela pedido
            pedido_id = int(linha.split()[1])
            response = pedidos_stub.cancela_pedido(pedidos_pb2.cancela_pedido_request(pedido_id=pedido_id))
            print(response.status)
            
        elif linha == "T":  # Termina a execução
            response = pedidos_stub.fim_da_execucao(pedidos_pb2.fim_da_execucao_request())
            print(response.estoque_quantidade, response.pedidos_ativos)
            break

if __name__ == "__main__": 
    run()