import socket
import threading


def cliente_chat():
    HOST = '127.0.0.1'  # IP do servidor
    PORTA = 8888             # Porta do servidor

    nome = input("digite seu nome: ")
    cliente = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    cliente.connect((HOST, PORTA))

    # Enviar nome para o servidor
    cliente.send(nome.encode())

    # receber mensagens do servidor
    def receber_mensagens():
        while True:
            try:
                mensagem = cliente.recv(1024).decode()
                if mensagem:
                    print(mensagem)
            except:
                print("chat encerrado.")
                break

    th_receber = threading.Thread(target=receber_mensagens)
    th_receber.start()

    # enviar mensagens para o servidor
    while True:
        mensagem = input()
        if mensagem.lower() == "/sair":
            cliente.close()
            break
        cliente.send(mensagem.encode())


cliente_chat()
