import socket
import json
import logging

# 配置日志
logging.basicConfig(filename='atm_server.log', level=logging.INFO)

def load_users():
    try:
        with open('users.json') as f:
            return json.load(f)
    except FileNotFoundError:
        return {}

def save_users(users):
    with open('users.json', 'w') as f:
        json.dump(users, f, indent=4)

def handle_client(client_socket):
    users = load_users()
    current_user = None  # 存储当前登录的用户

    try:
        while True:
            try:
                data = client_socket.recv(1024).decode().strip()
                if not data:
                    break

                logging.info(f'Received: {data}')
                command, *args = data.split()

                if command == 'HELO':
                    user_id = args[0]
                    current_user = user_id
                    response = '500 AUTH REQUIRE'
                    client_socket.sendall(response.encode())

                elif command == 'PASS':
                    password = args[0]
                    if current_user and users.get(current_user) and users[current_user]['password'] == password:
                        response = '525 OK!'
                    else:
                        response = '401 ERROR!'
                        current_user = None  # 登录失败，清空当前用户
                    client_socket.sendall(response.encode())

                elif command == 'BALA':
                    if current_user:
                        balance = users[current_user]['balance']
                        response = f'AMNT:{balance}'
                    else:
                        response = '401 ERROR!'
                    client_socket.sendall(response.encode())

                elif command == 'WDRA':
                    if not current_user:
                        client_socket.sendall(b'401 ERROR!')
                        continue

                    amount = int(args[0])
                    if users[current_user]['balance'] >= amount:
                        users[current_user]['balance'] -= amount
                        save_users(users)
                        response = '525 OK!'
                    else:
                        response = '401 ERROR!'
                    client_socket.sendall(response.encode())

                elif command == 'BYE':
                    client_socket.sendall(b'BYE')
                    break

                logging.info(f'Sent: {response}')

            except (ValueError, IndexError):
                client_socket.sendall(b'400 INVALID COMMAND')
    finally:
        client_socket.close()

def start_server():
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind(('192.168.43.12',8080 ))
    server.listen(5)
    print("Server is listening...")
    try:
        while True:
            client_socket, addr = server.accept()
            print(f"Connection from {addr}")
            handle_client(client_socket)
    finally:
        server.close()

if __name__ == "__main__":
    start_server()