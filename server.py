import socket
import threading

# Налаштування сервера
HOST = '127.0.0.1'  # Localhost
PORT = 55555  # Порт для підключення

# Запуск сокета сервера
server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind((HOST, PORT))
server.listen()

# clients — це список об'єктів сокетів, nicknames — список рядків.
clients: list[socket.socket] = []
nicknames: list[str] = []


def broadcast(message: bytes, _sender_client: socket.socket | None = None) -> None:
    """Надсилає повідомлення всім підключеним клієнтам крім відправника"""
    for client in clients:
        if client != _sender_client:
            try:
                client.send(message)
            except (ConnectionResetError, BrokenPipeError):
                # Перехоплюємо конкретні помилки відправки якщо клієнт відключився
                remove_client(client)

def remove_client(client: socket.socket) -> None:
    """Видаляє клієнта з чату у разі відключення."""
    if client in clients:
        index = clients.index(client)
        clients.remove(client)
        client.close()
        nickname = nicknames[index]
        nicknames.remove(nickname)
        broadcast(f"📢 {nickname} покинув чат.".encode('utf-8'))
        print(f"[-] Клієнт {nickname} відключився.")


def handle_client(client: socket.socket) -> None:
    """Обробка повідомлень від конкретного клієнта в окремому потоці"""
    while True:
        try:
            message = client.recv(1024)
            if not message:
                break
            broadcast(message, _sender_client=client)
        except (ConnectionResetError, ConnectionAbortedError):
            # Перехоплюємо помилку розриву з'єднання під час recv()
            break

    remove_client(client)


def receive() -> None:
    """Основний цикл сервера, приймає нові з'єднання."""
    print(f"[+] Сервер запущено і він очікує на підключення (Порт: {PORT})...")

    while True:
        try:
            client, address = server.accept()
            print(f"[+] Встановлено з'єднання з {str(address)}")

            client.send('NICK'.encode('utf-8'))
            nickname = client.recv(1024).decode('utf-8')

            nicknames.append(nickname)
            clients.append(client)

            print(f"[+] Нікнейм клієнта: {nickname}")

            broadcast(f"🎉 {nickname} приєднався до чату!".encode('utf-8'))
            client.send("Успішно підключено до сервера!\n".encode('utf-8'))

            thread = threading.Thread(target=handle_client, args=(client,))
            thread.start()
        except OSError:
            print("[-] Роботу сервера завершено через помилку сокета.")
            break
        except KeyboardInterrupt:
            print("\n[-] Сервер зупиняється користувачем.")
            break


if __name__ == "__main__":
    receive()