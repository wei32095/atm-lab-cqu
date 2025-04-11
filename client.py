import tkinter as tk
from tkinter import messagebox
import socket


class ATMClient:
    def __init__(self, master):
        self.master = master
        self.master.title("ATM Client")
        self.connected = False
        self.client_socket = None

        # 命令输入框
        self.command_label = tk.Label(master, text="Enter Command:")
        self.command_label.pack()
        self.command_entry = tk.Entry(master)
        self.command_entry.pack()

        # 发送命令按钮
        self.send_button = tk.Button(master, text="Send Command", command=self.send_command)
        self.send_button.pack()

        # 连接按钮
        self.connect_button = tk.Button(master, text="Connect", command=self.connect_server)
        self.connect_button.pack()

        # 断开连接按钮
        self.disconnect_button = tk.Button(master, text="Disconnect", command=self.disconnect_server, state=tk.DISABLED)
        self.disconnect_button.pack()

    def connect_server(self):
        try:
            self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.client_socket.connect(('192.168.43.12', 8080))
            self.connected = True
            self.connect_button.config(state=tk.DISABLED)
            self.disconnect_button.config(state=tk.NORMAL)
            messagebox.showinfo("Info", "Connected to server successfully!")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to connect: {e}")

    def disconnect_server(self):
        try:
            if self.connected:
                self.client_socket.sendall(b'BYE')
                response = self.client_socket.recv(1024).decode()
                if response == 'BYE':
                    messagebox.showinfo("Info", "Disconnected successfully")
                self.client_socket.close()
        except Exception as e:
            messagebox.showerror("Error", f"Error while disconnecting: {e}")
        finally:
            self.connected = False
            self.connect_button.config(state=tk.NORMAL)
            self.disconnect_button.config(state=tk.DISABLED)
            self.client_socket = None

    def send_command(self):
        if not self.connected:
            messagebox.showwarning("Warning", "Not connected to server!")
            return

        command = self.command_entry.get().strip()
        if not command:
            messagebox.showwarning("Warning", "Command cannot be empty!")
            return

        try:
            self.client_socket.sendall(command.encode())
            response = self.client_socket.recv(1024).decode()

            if command.startswith("BALA"):
                if response.startswith("AMNT:"):
                    balance = response.split(":")[1]
                    messagebox.showinfo("Balance", f"Your balance is: {balance}")
                else:
                    messagebox.showerror("Error", "Failed to retrieve balance.")
            elif command.startswith("WDRA"):
                if response == "525 OK!":
                    messagebox.showinfo("Withdrawal", "Withdrawal successful!")
                else:
                    messagebox.showerror("Withdrawal", "Withdrawal failed!")
            elif command.startswith("HELO") or command.startswith("PASS"):
                if response == "500 AUTH REQUIRE":
                    messagebox.showinfo("Login", "Authentication required. Please enter PASS command.")
                elif response == "525 OK!":
                    messagebox.showinfo("Login", "Login successful!")
                else:
                    messagebox.showerror("Login", "Login failed!")
            elif command.startswith("BYE"):
                if response == "BYE":
                    messagebox.showinfo("Disconnect", "Session ended.")
                    self.disconnect_server()
                else:
                    messagebox.showerror("Error", "Failed to disconnect.")
            else:
                messagebox.showinfo("Response", response)

        except ConnectionAbortedError:
            messagebox.showerror("Error", "Connection was aborted. Please reconnect.")
            self.disconnect_server()
        except Exception as e:
            messagebox.showerror("Error", f"An error occurred: {e}")
            self.disconnect_server()


root = tk.Tk()
app = ATMClient(root)
root.mainloop()