PROTO_FILES = estoque.proto pedidos.proto
STUB_FILES = estoque_pb2.py estoque_pb2_grpc.py pedidos_pb2.py pedidos_pb2_grpc.py

.PHONY: stubs run_serv_estoque run_cli_estoque run_serv_pedidos run_cli_pedidos clean

clean:
	rm -f $(STUB_FILES)

stubs: $(STUB_FILES)

$(STUB_FILES): $(PROTO_FILES)
	python3 -m grpc_tools.protoc -I. --python_out=. --grpc_python_out=. $^

run_serv_estoque: stubs
	python3 svc_estoque.py $(arg1)

run_cli_estoque: stubs
	python3 cln_estoque.py $(arg1)

run_serv_pedidos: stubs
	python3 svc_pedidos.py $(arg1) $(arg2)

run_cli_pedidos: stubs
	python3 cln_pedidos.py $(arg1) $(arg2)
