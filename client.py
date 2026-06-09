import socket
import threading
import sys

HOST = '127.0.0.1'
PORT = 55555

nickname = input("Введіть ваш нікнейм для чату: ")
if not nickname.strip():
    nickname = "Anonymous"

# Створення сокета клієнта
client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
try:
    client.connect((HOST, PORT))
except ConnectionRefusedError:
    print("Помилка: Не вдалося підключитися до сервера. Перевірте, чи запущений server.py.")
    sys.exit()


def receive_messages():
    """Потік для постійного отримання повідомлень від сервера."""
    while True:
        try:
            message = client.recv(1024).decode('utf-8')
            if message == 'NICK':
                client.send(nickname.encode('utf-8'))
            else:
                print(message)
        except (ConnectionResetError, ConnectionAbortedError):
            print("Зв'язок із сервером втрачено!")
            client.close()
            break
        except Exception as e:
            print(f"Непередбачувана помилка: {e}")
            client.close()
            break


def send_messages():
    """Потік для зчитування введення з консолі та відправки на server."""
    while True:
        try:
            text = input("")
            if text.lower() == '/exit':
                client.close()
                break

            if text.strip():
                message = f"{nickname}: {text}"
                client.send(message.encode('utf-8'))
        except (OSError, ConnectionResetError):
            break

# Запускаємо потоки для одночасної роботи
receive_thread = threading.Thread(target=receive_messages)
receive_thread.start()

write_thread = threading.Thread(target=send_messages)
write_thread.start()