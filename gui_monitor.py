#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Interface Gráfica do Monitorador de Servidores GlassFish
Painel de telemetria em tempo real com cadastro de servidores
"""

import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
import threading
import time
from datetime import datetime, timedelta
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
import matplotlib.animation as animation
from collections import deque
import json
from monitor import ServerMonitor, SERVERS, CONFIG

class ServerMonitorGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Monitor de Servidores GlassFish")
        self.root.geometry("1200x800")
        self.root.configure(bg='#f0f0f0')
        
        # Inicializar monitor
        self.monitor = ServerMonitor()
        self.servers = SERVERS.copy()
        
        # Dados para telemetria
        self.telemetry_data = {}
        self.max_data_points = 50
        
        # Variáveis de controle
        self.monitoring_active = False
        self.update_thread = None
        
        self.setup_ui()
        self.setup_telemetry()
        self.load_servers_config()  # Carregar servidores do arquivo JSON
        self.load_servers()  # Atualizar interface
        
    def setup_ui(self):
        """Configura a interface do usuário"""
        # Frame principal
        main_frame = ttk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Título
        title_label = tk.Label(main_frame, text="🖥️ Monitor de Servidores GlassFish", 
                              font=('Arial', 16, 'bold'), bg='#f0f0f0')
        title_label.pack(pady=(0, 10))
        
        # Frame de controles
        control_frame = ttk.Frame(main_frame)
        control_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Botões de controle
        self.start_btn = ttk.Button(control_frame, text="▶️ Iniciar Monitoramento", 
                                   command=self.start_monitoring)
        self.start_btn.pack(side=tk.LEFT, padx=(0, 5))
        
        self.stop_btn = ttk.Button(control_frame, text="⏹️ Parar Monitoramento", 
                                  command=self.stop_monitoring, state=tk.DISABLED)
        self.stop_btn.pack(side=tk.LEFT, padx=(0, 5))
        
        self.add_server_btn = ttk.Button(control_frame, text="➕ Adicionar Servidor", 
                                        command=self.add_server_dialog)
        self.add_server_btn.pack(side=tk.LEFT, padx=(0, 5))
        
        self.edit_server_btn = ttk.Button(control_frame, text="✏️ Editar Servidor", 
                                         command=self.edit_server_dialog)
        self.edit_server_btn.pack(side=tk.LEFT, padx=(0, 5))
        
        self.remove_server_btn = ttk.Button(control_frame, text="➖ Remover Servidor", 
                                           command=self.remove_server_dialog)
        self.remove_server_btn.pack(side=tk.LEFT, padx=(0, 5))
        
        self.config_btn = ttk.Button(control_frame, text="⚙️ Configurações", 
                                    command=self.show_config_dialog)
        self.config_btn.pack(side=tk.LEFT, padx=(0, 5))
        
        # Status do monitoramento
        self.status_label = tk.Label(control_frame, text="Status: Parado", 
                                    font=('Arial', 10), bg='#f0f0f0')
        self.status_label.pack(side=tk.RIGHT)
        
        # Notebook para abas
        self.notebook = ttk.Notebook(main_frame)
        self.notebook.pack(fill=tk.BOTH, expand=True)
        
        # Aba de Status dos Servidores
        self.setup_servers_tab()
        
        # Aba de Telemetria
        self.setup_telemetry_tab()
        
        # Aba de Logs
        self.setup_logs_tab()
    
    def setup_servers_tab(self):
        """Configura a aba de status dos servidores"""
        servers_frame = ttk.Frame(self.notebook)
        self.notebook.add(servers_frame, text="📊 Status dos Servidores")
        
        # Treeview para mostrar servidores
        columns = ('Nome', 'Host', 'Ping', 'Porta App', 'Porta Admin', 'HTTP', 'Status', 'Última Verificação')
        self.servers_tree = ttk.Treeview(servers_frame, columns=columns, show='headings', height=15)
        
        # Configurar colunas
        for col in columns:
            self.servers_tree.heading(col, text=col)
            if col == 'Nome':
                self.servers_tree.column(col, width=150)
            elif col == 'Host':
                self.servers_tree.column(col, width=120)
            elif col == 'Status':
                self.servers_tree.column(col, width=100)
            elif col == 'Última Verificação':
                self.servers_tree.column(col, width=150)
            else:
                self.servers_tree.column(col, width=80)
        
        # Scrollbar para treeview
        scrollbar = ttk.Scrollbar(servers_frame, orient=tk.VERTICAL, command=self.servers_tree.yview)
        self.servers_tree.configure(yscrollcommand=scrollbar.set)
        
        # Pack treeview e scrollbar
        self.servers_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Configurar tags para cores
        self.servers_tree.tag_configure('online', background='#d4edda')
        self.servers_tree.tag_configure('offline', background='#f8d7da')
        self.servers_tree.tag_configure('warning', background='#fff3cd')
    
    def setup_telemetry_tab(self):
        """Configura a aba de telemetria"""
        telemetry_frame = ttk.Frame(self.notebook)
        self.notebook.add(telemetry_frame, text="📈 Telemetria")
        
        # Frame para seleção de servidor
        select_frame = ttk.Frame(telemetry_frame)
        select_frame.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Label(select_frame, text="Servidor:").pack(side=tk.LEFT)
        self.telemetry_server_var = tk.StringVar()
        self.telemetry_combo = ttk.Combobox(select_frame, textvariable=self.telemetry_server_var, 
                                           state="readonly", width=30)
        self.telemetry_combo.pack(side=tk.LEFT, padx=(5, 0))
        self.telemetry_combo.bind('<<ComboboxSelected>>', self.on_telemetry_server_change)
        
        # Frame para gráficos
        self.telemetry_canvas_frame = ttk.Frame(telemetry_frame)
        self.telemetry_canvas_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
    
    def setup_telemetry(self):
        """Configura os gráficos de telemetria"""
        # Criar figura matplotlib
        self.fig = Figure(figsize=(12, 8), dpi=100)
        self.fig.suptitle('Telemetria do Servidor', fontsize=14, fontweight='bold')
        
        # Subplots
        self.ax1 = self.fig.add_subplot(2, 2, 1)
        self.ax2 = self.fig.add_subplot(2, 2, 2)
        self.ax3 = self.fig.add_subplot(2, 2, 3)
        self.ax4 = self.fig.add_subplot(2, 2, 4)
        
        # Configurar eixos
        self.ax1.set_title('Status de Conectividade')
        self.ax1.set_ylabel('Status')
        
        self.ax2.set_title('Tempo de Resposta HTTP (ms)')
        self.ax2.set_ylabel('Tempo (ms)')
        
        self.ax3.set_title('Disponibilidade das Portas')
        self.ax3.set_ylabel('Status')
        
        self.ax4.set_title('Histórico de Status')
        self.ax4.set_ylabel('Uptime %')
        
        # Canvas para matplotlib
        self.canvas = None
    
    def setup_logs_tab(self):
        """Configura a aba de logs"""
        logs_frame = ttk.Frame(self.notebook)
        self.notebook.add(logs_frame, text="📝 Logs")
        
        # Text widget para logs
        self.logs_text = tk.Text(logs_frame, wrap=tk.WORD, height=25)
        logs_scrollbar = ttk.Scrollbar(logs_frame, orient=tk.VERTICAL, command=self.logs_text.yview)
        self.logs_text.configure(yscrollcommand=logs_scrollbar.set)
        
        # Pack logs
        self.logs_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        logs_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Botão para limpar logs
        clear_logs_btn = ttk.Button(logs_frame, text="🗑️ Limpar Logs", 
                                   command=self.clear_logs)
        clear_logs_btn.pack(side=tk.BOTTOM, pady=5)
    
    def load_servers(self):
        """Carrega a lista de servidores na interface"""
        # Limpar treeview
        for item in self.servers_tree.get_children():
            self.servers_tree.delete(item)
        
        # Adicionar servidores
        for server in self.servers:
            self.servers_tree.insert('', tk.END, values=(
                server['name'], server['host'], '-', '-', '-', '-', 'Não verificado', '-'
            ))
        
        # Atualizar combo de telemetria
        server_names = [server['name'] for server in self.servers]
        self.telemetry_combo['values'] = server_names
        if server_names:
            self.telemetry_combo.set(server_names[0])
    
    def start_monitoring(self):
        """Inicia o monitoramento"""
        if not self.monitoring_active:
            self.monitoring_active = True
            self.monitor.servers = self.servers
            self.monitor.start_monitoring()
            
            # Iniciar thread de atualização da GUI
            self.update_thread = threading.Thread(target=self.update_gui_loop, daemon=True)
            self.update_thread.start()
            
            # Atualizar botões
            self.start_btn.config(state=tk.DISABLED)
            self.stop_btn.config(state=tk.NORMAL)
            self.status_label.config(text="Status: Monitorando", fg='green')
            
            self.log_message("Monitoramento iniciado")
    
    def stop_monitoring(self):
        """Para o monitoramento"""
        if self.monitoring_active:
            self.monitoring_active = False
            self.monitor.stop_monitoring()
            
            # Atualizar botões
            self.start_btn.config(state=tk.NORMAL)
            self.stop_btn.config(state=tk.DISABLED)
            self.status_label.config(text="Status: Parado", fg='red')
            
            self.log_message("Monitoramento parado")
    
    def update_gui_loop(self):
        """Loop de atualização da GUI"""
        while self.monitoring_active:
            try:
                self.root.after(0, self.update_servers_display)
                self.root.after(0, self.update_telemetry)
                time.sleep(2)  # Atualizar a cada 2 segundos
            except Exception as e:
                print(f"Erro na atualização da GUI: {e}")
                time.sleep(5)
    
    def update_servers_display(self):
        """Atualiza a exibição dos servidores"""
        # Salvar seleção atual
        selected_items = self.servers_tree.selection()
        selected_server_names = []
        for item in selected_items:
            values = self.servers_tree.item(item, 'values')
            if values:
                selected_server_names.append(values[0])  # Nome do servidor
        
        # Limpar treeview
        for item in self.servers_tree.get_children():
            self.servers_tree.delete(item)
        
        # Adicionar servidores com status atual
        for server in self.servers:
            name = server['name']
            status_data = self.monitor.server_status.get(name, {})
            
            if status_data:
                # Ping status com tempo de resposta
                ping_data = status_data.get('ping', {})
                if isinstance(ping_data, dict):
                    if ping_data.get('success'):
                        ping_status = f"✅ {ping_data['response_time']}ms"
                    else:
                        ping_status = f"❌ {ping_data.get('error', 'Failed')}"
                else:
                    ping_status = '✅' if ping_data else '❌'
                
                # App port status com número da porta e tempo de resposta
                app_port_data = status_data.get('app_port', {})
                app_port_number = server.get('app_port', 'N/A')
                if isinstance(app_port_data, dict):
                    if app_port_data.get('success'):
                        app_port_status = f"✅ {app_port_number} ({app_port_data['response_time']}ms)"
                    else:
                        app_port_status = f"❌ {app_port_number} ({app_port_data.get('status', 'Failed')})"
                else:
                    app_port_status = f"{'✅' if app_port_data else '❌'} {app_port_number}"
                
                # Admin port status com número da porta e tempo de resposta
                admin_port_data = status_data.get('admin_port', {})
                admin_port_number = server.get('admin_port', 'N/A')
                if isinstance(admin_port_data, dict):
                    if admin_port_data.get('success'):
                        admin_port_status = f"✅ {admin_port_number} ({admin_port_data['response_time']}ms)"
                    else:
                        admin_port_status = f"❌ {admin_port_number} ({admin_port_data.get('status', 'Failed')})"
                else:
                    admin_port_status = f"{'✅' if admin_port_data else '❌'} {admin_port_number}"
                
                # HTTP status (mantém formato atual)
                http_status = '-'
                if status_data.get('http'):
                    http_data = status_data['http']
                    if http_data['success']:
                        http_status = f"✅ {http_data['status_code']}"
                    else:
                        http_status = f"❌ {http_data.get('error', 'Error')}"
                
                overall_status = status_data.get('status', 'UNKNOWN')
                timestamp = status_data.get('timestamp', datetime.now())
                last_check = timestamp.strftime('%H:%M:%S')
                
                # Determinar tag para cor
                tag = 'online' if overall_status == 'ONLINE' else ('warning' if overall_status in ['HTTP_ERROR', 'PORTS_CLOSED'] else 'offline')
                
                item = self.servers_tree.insert('', tk.END, values=(
                    name, server['host'], ping_status, app_port_status, 
                    admin_port_status, http_status, overall_status, last_check
                ), tags=(tag,))
                
                # Restaurar seleção se este servidor estava selecionado
                if name in selected_server_names:
                    self.servers_tree.selection_add(item)
            else:
                item = self.servers_tree.insert('', tk.END, values=(
                    name, server['host'], '-', '-', '-', '-', 'Aguardando...', '-'
                ))
                
                # Restaurar seleção se este servidor estava selecionado
                if name in selected_server_names:
                    self.servers_tree.selection_add(item)
    
    def update_telemetry(self):
        """Atualiza os gráficos de telemetria"""
        selected_server = self.telemetry_server_var.get()
        if not selected_server or selected_server not in self.monitor.server_status:
            return
        
        # Obter dados do servidor
        status_data = self.monitor.server_status[selected_server]
        
        # Inicializar dados de telemetria se necessário
        if selected_server not in self.telemetry_data:
            self.telemetry_data[selected_server] = {
                'timestamps': deque(maxlen=self.max_data_points),
                'ping_status': deque(maxlen=self.max_data_points),
                'http_response_times': deque(maxlen=self.max_data_points),
                'app_port_status': deque(maxlen=self.max_data_points),
                'admin_port_status': deque(maxlen=self.max_data_points),
                'overall_status': deque(maxlen=self.max_data_points)
            }
        
        # Adicionar novos dados
        data = self.telemetry_data[selected_server]
        data['timestamps'].append(datetime.now())
        data['ping_status'].append(1 if status_data.get('ping') else 0)
        data['app_port_status'].append(1 if status_data.get('app_port') else 0)
        data['admin_port_status'].append(1 if status_data.get('admin_port') else 0)
        data['overall_status'].append(1 if status_data.get('status') == 'ONLINE' else 0)
        
        # Tempo de resposta HTTP
        http_time = 0
        if status_data.get('http') and 'response_time' in status_data['http']:
            http_time = status_data['http']['response_time'] * 1000  # Converter para ms
        data['http_response_times'].append(http_time)
        
        # Atualizar gráficos
        self.plot_telemetry_data(selected_server)
    
    def plot_telemetry_data(self, server_name):
        """Plota os dados de telemetria"""
        if server_name not in self.telemetry_data:
            return
        
        data = self.telemetry_data[server_name]
        
        if len(data['timestamps']) < 2:
            return
        
        # Limpar eixos
        self.ax1.clear()
        self.ax2.clear()
        self.ax3.clear()
        self.ax4.clear()
        
        timestamps = list(data['timestamps'])
        
        # Gráfico 1: Status de Ping
        self.ax1.plot(timestamps, list(data['ping_status']), 'b-', label='Ping', linewidth=2)
        self.ax1.set_title('Status de Conectividade (Ping)')
        self.ax1.set_ylabel('Status (0=Offline, 1=Online)')
        self.ax1.set_ylim(-0.1, 1.1)
        self.ax1.grid(True, alpha=0.3)
        
        # Gráfico 2: Tempo de resposta HTTP
        self.ax2.plot(timestamps, list(data['http_response_times']), 'g-', label='HTTP Response', linewidth=2)
        self.ax2.set_title('Tempo de Resposta HTTP')
        self.ax2.set_ylabel('Tempo (ms)')
        self.ax2.grid(True, alpha=0.3)
        
        # Gráfico 3: Status das portas
        self.ax3.plot(timestamps, list(data['app_port_status']), 'r-', label='Porta App', linewidth=2)
        self.ax3.plot(timestamps, list(data['admin_port_status']), 'orange', label='Porta Admin', linewidth=2)
        self.ax3.set_title('Status das Portas')
        self.ax3.set_ylabel('Status (0=Fechada, 1=Aberta)')
        self.ax3.set_ylim(-0.1, 1.1)
        self.ax3.legend()
        self.ax3.grid(True, alpha=0.3)
        
        # Gráfico 4: Uptime geral
        uptime_data = list(data['overall_status'])
        if len(uptime_data) > 0:
            uptime_percentage = [sum(uptime_data[:i+1])/(i+1)*100 for i in range(len(uptime_data))]
            self.ax4.plot(timestamps, uptime_percentage, 'purple', linewidth=2)
        self.ax4.set_title('Disponibilidade Geral (%)')
        self.ax4.set_ylabel('Uptime (%)')
        self.ax4.set_ylim(0, 105)
        self.ax4.grid(True, alpha=0.3)
        
        # Formatar eixos X
        for ax in [self.ax1, self.ax2, self.ax3, self.ax4]:
            ax.tick_params(axis='x', rotation=45)
        
        # Ajustar layout
        self.fig.tight_layout()
        
        # Atualizar canvas
        if self.canvas is None:
            self.canvas = FigureCanvasTkAgg(self.fig, self.telemetry_canvas_frame)
            self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
        
        self.canvas.draw()
    
    def on_telemetry_server_change(self, event=None):
        """Callback quando servidor de telemetria é alterado"""
        selected_server = self.telemetry_server_var.get()
        if selected_server:
            self.plot_telemetry_data(selected_server)
    
    def add_server_dialog(self):
        """Diálogo para adicionar servidor"""
        dialog = ServerDialog(self.root, "Adicionar Servidor")
        if dialog.result:
            self.servers.append(dialog.result)
            self.save_servers_config()
            self.load_servers()
            self.log_message(f"Servidor '{dialog.result['name']}' adicionado")
    
    def edit_server_dialog(self):
        """Diálogo para editar servidor"""
        if not self.servers:
            messagebox.showwarning("Aviso", "Não há servidores para editar")
            return
        
        # Verificar se há um servidor selecionado na treeview
        selected_item = self.servers_tree.selection()
        if not selected_item:
            messagebox.showinfo("Seleção Necessária", "Por favor, selecione um servidor na tabela para editar")
            return
        
        # Obter dados do servidor selecionado
        item_values = self.servers_tree.item(selected_item[0], 'values')
        server_name = item_values[0]
        
        # Encontrar o servidor na lista
        server_to_edit = None
        server_index = -1
        for i, server in enumerate(self.servers):
            if server['name'] == server_name:
                server_to_edit = server
                server_index = i
                break
        
        if server_to_edit:
            # Abrir diálogo de edição com dados pré-carregados
            dialog = ServerDialog(self.root, "Editar Servidor", server_to_edit)
            if dialog.result:
                # Atualizar servidor na lista
                self.servers[server_index] = dialog.result
                self.save_servers_config()
                self.load_servers()
                self.log_message(f"Servidor '{dialog.result['name']}' editado")
        else:
            messagebox.showerror("Erro", f"Servidor '{server_name}' não encontrado na lista")
    
    def remove_server_dialog(self):
        """Diálogo para remover servidor"""
        if not self.servers:
            messagebox.showwarning("Aviso", "Não há servidores para remover")
            return
        
        # Verificar se há um servidor selecionado na treeview
        selected_item = self.servers_tree.selection()
        if not selected_item:
            messagebox.showinfo("Seleção Necessária", "Por favor, selecione um servidor na tabela para remover")
            return
        
        # Obter dados do servidor selecionado
        item_values = self.servers_tree.item(selected_item[0], 'values')
        server_name = item_values[0]
        
        # Confirmar remoção
        if messagebox.askyesno("Confirmar Remoção", f"Tem certeza que deseja remover o servidor '{server_name}'?"):
            # Encontrar e remover o servidor da lista
            for i, server in enumerate(self.servers):
                if server['name'] == server_name:
                    del self.servers[i]
                    self.save_servers_config()
                    self.load_servers()
                    self.log_message(f"Servidor '{server_name}' removido")
                    return
            messagebox.showerror("Erro", f"Servidor '{server_name}' não encontrado na lista")
    
    def show_config_dialog(self):
        """Mostra diálogo de configurações"""
        ConfigDialog(self.root, CONFIG)
    
    def save_servers_config(self):
        """Salva configuração dos servidores"""
        try:
            with open('servers_config.json', 'w', encoding='utf-8') as f:
                json.dump(self.servers, f, indent=2, ensure_ascii=False)
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao salvar configuração: {e}")
    
    def load_servers_config(self):
        """Carrega configuração dos servidores"""
        try:
            with open('servers_config.json', 'r', encoding='utf-8') as f:
                loaded_servers = json.load(f)
                if loaded_servers:  # Se há servidores no arquivo
                    self.servers = loaded_servers
                    self.log_message(f"Carregados {len(self.servers)} servidores do arquivo de configuração")
                else:
                    self.log_message("Arquivo de configuração vazio, usando servidores padrão")
        except FileNotFoundError:
            self.log_message("Arquivo servers_config.json não encontrado, usando servidores padrão")
        except Exception as e:
            self.log_message(f"Erro ao carregar configuração: {e}")
            messagebox.showerror("Erro", f"Erro ao carregar configuração: {e}")
    
    def log_message(self, message):
        """Adiciona mensagem aos logs da GUI"""
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        log_entry = f"[{timestamp}] {message}\n"
        
        self.logs_text.insert(tk.END, log_entry)
        self.logs_text.see(tk.END)
    
    def clear_logs(self):
        """Limpa os logs da GUI"""
        self.logs_text.delete(1.0, tk.END)
    
    def on_closing(self):
        """Callback para fechamento da janela"""
        if self.monitoring_active:
            self.stop_monitoring()
        self.root.destroy()

class ServerDialog:
    def __init__(self, parent, title, server_data=None):
        self.result = None
        
        # Criar janela
        self.dialog = tk.Toplevel(parent)
        self.dialog.title(title)
        self.dialog.geometry("450x400")
        self.dialog.transient(parent)
        self.dialog.grab_set()
        self.dialog.resizable(False, False)
        
        # Centralizar janela
        self.dialog.geometry("+%d+%d" % (parent.winfo_rootx() + 50, parent.winfo_rooty() + 50))
        
        # Campos
        ttk.Label(self.dialog, text="Nome do Servidor:").pack(pady=5)
        self.name_entry = ttk.Entry(self.dialog, width=40)
        self.name_entry.pack(pady=5)
        
        ttk.Label(self.dialog, text="Host/IP:").pack(pady=5)
        self.host_entry = ttk.Entry(self.dialog, width=40)
        self.host_entry.pack(pady=5)
        
        ttk.Label(self.dialog, text="Porta da Aplicação:").pack(pady=5)
        self.app_port_entry = ttk.Entry(self.dialog, width=40)
        self.app_port_entry.insert(0, "8080")
        self.app_port_entry.pack(pady=5)
        
        ttk.Label(self.dialog, text="Porta de Administração:").pack(pady=5)
        self.admin_port_entry = ttk.Entry(self.dialog, width=40)
        self.admin_port_entry.insert(0, "4848")
        self.admin_port_entry.pack(pady=5)
        
        ttk.Label(self.dialog, text="URL de Health Check (opcional):").pack(pady=5)
        self.health_url_entry = ttk.Entry(self.dialog, width=40)
        self.health_url_entry.pack(pady=5)
        
        # Se dados do servidor foram fornecidos, pré-carregar os campos
        if server_data:
            self.name_entry.insert(0, server_data.get('name', ''))
            self.host_entry.insert(0, server_data.get('host', ''))
            
            # Limpar e inserir porta da aplicação
            self.app_port_entry.delete(0, tk.END)
            self.app_port_entry.insert(0, str(server_data.get('app_port', 8080)))
            
            # Limpar e inserir porta de administração
            self.admin_port_entry.delete(0, tk.END)
            self.admin_port_entry.insert(0, str(server_data.get('admin_port', 4848)))
            
            self.health_url_entry.insert(0, server_data.get('health_url', ''))
        
        # Botões
        button_frame = ttk.Frame(self.dialog)
        button_frame.pack(pady=20, fill=tk.X)
        
        # Centralizar os botões
        inner_frame = ttk.Frame(button_frame)
        inner_frame.pack()
        
        ok_button = ttk.Button(inner_frame, text="Salvar", command=self.ok_clicked, width=12)
        ok_button.pack(side=tk.LEFT, padx=10)
        
        cancel_button = ttk.Button(inner_frame, text="Cancelar", command=self.cancel_clicked, width=12)
        cancel_button.pack(side=tk.LEFT, padx=10)
        
        # Bind Enter para OK e Escape para Cancelar
        self.dialog.bind('<Return>', lambda e: self.ok_clicked())
        self.dialog.bind('<Escape>', lambda e: self.cancel_clicked())
        
        # Focar no primeiro campo
        self.name_entry.focus()
        
        # Aguardar resultado
        self.dialog.wait_window()
    
    def ok_clicked(self):
        name = self.name_entry.get().strip()
        host = self.host_entry.get().strip()
        
        if not name or not host:
            messagebox.showerror("Erro", "Nome e Host são obrigatórios")
            return
        
        try:
            app_port = int(self.app_port_entry.get())
            admin_port = int(self.admin_port_entry.get())
        except ValueError:
            messagebox.showerror("Erro", "Portas devem ser números")
            return
        
        health_url = self.health_url_entry.get().strip()
        if not health_url:
            health_url = f"http://{host}:{app_port}/"
        
        self.result = {
            'name': name,
            'host': host,
            'app_port': app_port,
            'admin_port': admin_port,
            'health_url': health_url
        }
        
        self.dialog.destroy()
    
    def cancel_clicked(self):
        self.dialog.destroy()

class ConfigDialog:
    def __init__(self, parent, config):
        self.config = config
        
        # Criar janela
        self.dialog = tk.Toplevel(parent)
        self.dialog.title("Configurações")
        self.dialog.geometry("500x400")
        self.dialog.transient(parent)
        self.dialog.grab_set()
        
        # Centralizar janela
        self.dialog.geometry("+%d+%d" % (parent.winfo_rootx() + 50, parent.winfo_rooty() + 50))
        
        # Notebook para abas
        notebook = ttk.Notebook(self.dialog)
        notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Aba Geral
        general_frame = ttk.Frame(notebook)
        notebook.add(general_frame, text="Geral")
        
        ttk.Label(general_frame, text="Intervalo de Monitoramento (segundos):").pack(pady=5)
        self.interval_var = tk.StringVar(value=str(config['monitor_interval']))
        ttk.Entry(general_frame, textvariable=self.interval_var, width=20).pack(pady=5)
        
        ttk.Label(general_frame, text="Timeout de Ping (segundos):").pack(pady=5)
        self.ping_timeout_var = tk.StringVar(value=str(config['ping_timeout']))
        ttk.Entry(general_frame, textvariable=self.ping_timeout_var, width=20).pack(pady=5)
        
        ttk.Label(general_frame, text="Timeout HTTP (segundos):").pack(pady=5)
        self.http_timeout_var = tk.StringVar(value=str(config['http_timeout']))
        ttk.Entry(general_frame, textvariable=self.http_timeout_var, width=20).pack(pady=5)
        
        # Checkboxes
        self.sound_alerts_var = tk.BooleanVar(value=config['sound_alerts'])
        ttk.Checkbutton(general_frame, text="Alertas Sonoros", variable=self.sound_alerts_var).pack(pady=5)
        
        self.email_alerts_var = tk.BooleanVar(value=config['email_alerts'])
        ttk.Checkbutton(general_frame, text="Alertas por Email", variable=self.email_alerts_var).pack(pady=5)
        
        # Aba Email
        email_frame = ttk.Frame(notebook)
        notebook.add(email_frame, text="Email")
        
        ttk.Label(email_frame, text="Servidor SMTP:").pack(pady=5)
        self.smtp_server_var = tk.StringVar(value=config['smtp_server'])
        ttk.Entry(email_frame, textvariable=self.smtp_server_var, width=40).pack(pady=5)
        
        ttk.Label(email_frame, text="Porta SMTP:").pack(pady=5)
        self.smtp_port_var = tk.StringVar(value=str(config['smtp_port']))
        ttk.Entry(email_frame, textvariable=self.smtp_port_var, width=20).pack(pady=5)
        
        ttk.Label(email_frame, text="Usuário Email:").pack(pady=5)
        self.email_user_var = tk.StringVar(value=config['email_user'])
        ttk.Entry(email_frame, textvariable=self.email_user_var, width=40).pack(pady=5)
        
        ttk.Label(email_frame, text="Senha Email:").pack(pady=5)
        self.email_password_var = tk.StringVar(value=config['email_password'])
        ttk.Entry(email_frame, textvariable=self.email_password_var, width=40, show="*").pack(pady=5)
        
        # Botões
        button_frame = ttk.Frame(self.dialog)
        button_frame.pack(pady=10)
        
        ttk.Button(button_frame, text="Salvar", command=self.save_config).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Cancelar", command=self.dialog.destroy).pack(side=tk.LEFT, padx=5)
    
    def save_config(self):
        try:
            self.config['monitor_interval'] = int(self.interval_var.get())
            self.config['ping_timeout'] = int(self.ping_timeout_var.get())
            self.config['http_timeout'] = int(self.http_timeout_var.get())
            self.config['sound_alerts'] = self.sound_alerts_var.get()
            self.config['email_alerts'] = self.email_alerts_var.get()
            self.config['smtp_server'] = self.smtp_server_var.get()
            self.config['smtp_port'] = int(self.smtp_port_var.get())
            self.config['email_user'] = self.email_user_var.get()
            self.config['email_password'] = self.email_password_var.get()
            
            messagebox.showinfo("Sucesso", "Configurações salvas com sucesso!")
            self.dialog.destroy()
        except ValueError as e:
            messagebox.showerror("Erro", f"Erro nos valores: {e}")

def main():
    root = tk.Tk()
    app = ServerMonitorGUI(root)
    
    # Configurar fechamento
    root.protocol("WM_DELETE_WINDOW", app.on_closing)
    
    # Carregar configuração de servidores
    app.load_servers_config()
    app.load_servers()
    
    root.mainloop()

if __name__ == '__main__':
    main()