import socket as sock
import threading as th

#  receber dados do cliente
def receber_dados(sock_conn, ender):
    try:
        # Receber o nome do cliente
        nome = sock_conn.recv(50).decode().strip()
        cliente = {'nome': nome, 'socket': sock_conn}
        lista_cliente.append(cliente)
        print(f"Conexão com {nome} ({ender} estabelecida)")

        # Notificar clientes 
        lista_usuarios = [c['nome'] for c in lista_cliente]
        mensagem_bem_vindo = f"Conectado, {nome}!\nUsuários conectados: {', '.join(lista_usuarios)}"
        broadcast(lista_cliente, mensagem_bem_vindo)

        while True:
            mensagem = sock_conn.recv(1024).decode().strip()
            if not mensagem:
                raise Exception(f"Mensagem vazia de {nome}.")
            print(f"{nome} >> {mensagem}")

            # Verificar /remover
            if mensagem.startswith("/remover"):
                try:
                    # Extrair o nome do usuário a ser removido
                    _, nome_remover = mensagem.split(" ", 1)
                    if nome_remover:
                        remover_usuario_comando(sock_conn, lista_cliente, nome_remover)
                    else:
                        sock_conn.send("Uso incorreto do comando /remover. Formato: /remover <nome>".encode())
                except ValueError:
                    sock_conn.send("Uso incorreto do comando /remover. Formato: /remover <nome>".encode())
            
            # Verificar  /unicast
            elif mensagem.startswith("/privado"):
                try:
                    # Extrair destinatário e a mensagem
                    _, nome_destinatario, msg = mensagem.split(" ", 2)
                    unicast(lista_cliente, nome_destinatario, f"{nome} (Privado): {msg}")
                except ValueError:
                    sock_conn.send("Uso incorreto do comando /privado. Formato: /privado <nome> <mensagem>".encode())
            
            else:
                # envia a mensagem para todos os clientes
                broadcast(lista_cliente, f"{nome}: {mensagem}")

    except Exception as e:
        print(f"Erro com o cliente {ender}: {e}")
        remover(cliente, lista_cliente)

# enviar mensagem para todos os clientes
def broadcast(lista_cliente, mensagem):
    for cliente in lista_cliente:
        try:
            cliente['socket'].send(mensagem.encode())
        except:
            remover(cliente, lista_cliente)

#  remover um cliente da lista e fechar a conexão
def remover(cliente, lista_cliente):
    if cliente in lista_cliente:
        lista_cliente.remove(cliente)
        cliente['socket'].close()
        print(f"Cliente {cliente['nome']} removido.")
        broadcast(lista_cliente, f"{cliente['nome']} saiu do chat.")

#  remover um usuário específico com o comando /remover
def remover_usuario_comando(sock_conn, lista_cliente, nome_remover):
    # Verifica se o usuário está na lista de clientes
    for cliente in lista_cliente:
        if cliente['nome'] == nome_remover:
            try:
                # Enviar notificação  para todos os clientes
                mensagem_remocao = f"{nome_remover} foi removido do chat pelo administrador."
                broadcast(lista_cliente, mensagem_remocao)

                # Fechar a conexão e remover o cliente da lista
                remover(cliente, lista_cliente)
                sock_conn.send(f"{nome_remover} foi removido do chat.".encode())
                return
            except Exception as e:
                sock_conn.send(f"Erro ao tentar remover {nome_remover}: {e}".encode())
                return

    # Se o cliente não for encontrado
    sock_conn.send(f"Cliente {nome_remover} não encontrado.".encode())

# enviar mensagem para um cliente específico (unicast)
def unicast(lista_cliente, nome_destinatario, mensagem):
    for cliente in lista_cliente:
        if cliente['nome'] == nome_destinatario:
            try:
                cliente['socket'].send(mensagem.encode())
                print(f"Mensagem enviada para {nome_destinatario}: {mensagem}")
                return
            except Exception as e:
                print(f"Erro ao enviar mensagem para {nome_destinatario}: {e}")
                return
    print(f"Cliente {nome_destinatario} não encontrado para unicast.")


HOST = '127.0.0.1'  # Endereço IP do servidor
PORTA = 8888             # Porta do servidor
lista_cliente = []

# Criar o socket do servidor
socket_server = sock.socket(sock.AF_INET, sock.SOCK_STREAM)
socket_server.bind((HOST, PORTA))
socket_server.listen()
print(f"Servidor rodando em {HOST}:{PORTA}...")

# receber conexões de clientes
while True:
    try:
        sock_conn, ender = socket_server.accept()
        th_cliente = th.Thread(target=receber_dados, args=(sock_conn, ender))
        th_cliente.start()
    except KeyboardInterrupt:
        print("Servidor encerrado.")
        break
