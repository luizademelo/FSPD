## Comandos de exemplo:
make run_serv_estoque arg1=5555
make run_cli_estoque arg1=localhost:5555
make run_serv_pedidos arg1=6666 arg2=localhost:5555
make run_cli_pedidos arg1=localhost:5555 arg2=localhost:6666


## Decisões de implementação
- Pedidos inválidos são armazenados na lista de pedidos também
- Os identificadores de produtos e pedidos começam a partir do número 1
