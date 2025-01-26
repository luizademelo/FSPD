"""
------------------ Exercício de Programação 2 ------------------
Nome: Luiza de Melo Gomes
Matrícula: 2021040075
Disciplina: Fundamentos de Sistemas Paralelos Distribuídos
----------------------------------------------------------------
"""

import grpc
import sys
import estoque_pb2
import estoque_pb2_grpc

def run():
    if len(sys.argv) != 2:
        print("Usage: python3 cln_estoque.py <endereco_servidor_estoque>")
        return

    server_address = sys.argv[1]
    channel = grpc.insecure_channel(server_address)
    stub = estoque_pb2_grpc.ServidorStub(channel)

    for line in sys.stdin:
        line = line.strip()

        # Ignora linhas vazias
        if not line:
            continue

        command = line.split(" ", 1)
        cmd_type = command[0]

        if cmd_type == "P":
            _, rest = line.split(" ", 1)
            quantity, description = rest.split(" ", 1)
            response = stub.adiciona_produto(estoque_pb2.adiciona_produto_message(
                descricao=description, quantidade=int(quantity)))
            print(response.prod_id)

        elif cmd_type == "Q":
            _, prodid, value = line.split()
            response = stub.altera_quantidade_produto(estoque_pb2.altera_produto_message(
                prod_id=int(prodid), valor=int(value)))
            print(response.status)

        elif cmd_type == "L":
            response = stub.lista_produtos(estoque_pb2.lista_produtos_message())
            for product in response.lista_produtos:
                print(f"{product.prod_id} {product.quantidade} {product.descricao}")

        elif cmd_type == "F":
            # Termina o cliente e o servidor de estoque
            response = stub.termina_execucao(estoque_pb2.termina_execucao_message())
            print(response.quantidade_produtos)
            break

if __name__ == '__main__':
    run()