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
import webbrowser
from monitor import ServerMonitor, SERVERS, CONFIG, extract_port_from_url, extract_hostname_from_url, detect_admin_port

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
        
        # Configurar colunas com larguras iniciais
        column_configs = {
            'Nome': {'width': 150, 'minwidth': 100},
            'Host': {'width': 180, 'minwidth': 120},
            'Ping': {'width': 100, 'minwidth': 80},
            'Porta App': {'width': 90, 'minwidth': 80},
            'Porta Admin': {'width': 100, 'minwidth': 80},
            'HTTP': {'width': 100, 'minwidth': 80},
            'Status': {'width': 120, 'minwidth': 100},
            'Última Verificação': {'width': 180, 'minwidth': 150}
        }
        
        for col in columns:
            self.servers_tree.heading(col, text=col, command=lambda c=col: self.sort_servers_tree(c))
            config = column_configs[col]
            self.servers_tree.column(col, width=config['width'], minwidth=config['minwidth'], stretch=True)
        
        # Bind eventos para ajuste automático e duplo clique
        self.servers_tree.bind('<Double-1>', self.on_server_double_click)
        self.servers_tree.bind('<Button-1>', self.on_server_click)
        
        # Scrollbars para treeview
        v_scrollbar = ttk.Scrollbar(servers_frame, orient=tk.VERTICAL, command=self.servers_tree.yview)
        h_scrollbar = ttk.Scrollbar(servers_frame, orient=tk.HORIZONTAL, command=self.servers_tree.xview)
        self.servers_tree.configure(yscrollcommand=v_scrollbar.set, xscrollcommand=h_scrollbar.set)
        
        # Grid layout para scrollbars
        self.servers_tree.grid(row=0, column=0, sticky='nsew')
        v_scrollbar.grid(row=0, column=1, sticky='ns')
        h_scrollbar.grid(row=1, column=0, sticky='ew')
        
        # Configurar grid weights
        servers_frame.grid_rowconfigure(0, weight=1)
        servers_frame.grid_columnconfigure(0, weight=1)
        
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
        
        # Frame superior para seleção de servidor
        logs_control_frame = ttk.Frame(logs_frame)
        logs_control_frame.pack(fill=tk.X, padx=5, pady=5)
        
        # Label e combobox para seleção de servidor
        ttk.Label(logs_control_frame, text="Servidor:").pack(side=tk.LEFT, padx=(0, 5))
        
        self.logs_server_var = tk.StringVar()
        self.logs_combo = ttk.Combobox(logs_control_frame, textvariable=self.logs_server_var, 
                                      state="readonly", width=20)
        self.logs_combo.pack(side=tk.LEFT, padx=(0, 10))
        self.logs_combo.bind('<<ComboboxSelected>>', self.on_logs_server_change)
        
        # Botão para limpar logs
        clear_logs_btn = ttk.Button(logs_control_frame, text="🗑️ Limpar Logs", 
                                   command=self.clear_logs)
        clear_logs_btn.pack(side=tk.LEFT, padx=5)
        
        # Frame para logs com scrollbar
        logs_tree_frame = ttk.Frame(logs_frame)
        logs_tree_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # TreeView para logs estruturados
        columns = ('timestamp', 'event_type', 'message')
        self.logs_tree = ttk.Treeview(logs_tree_frame, columns=columns, show='headings', height=20)
        
        # Configurar colunas com ajuste automático
        logs_column_configs = {
            'timestamp': {'width': 180, 'minwidth': 150, 'text': 'Timestamp'},
            'event_type': {'width': 120, 'minwidth': 100, 'text': 'Tipo'},
            'message': {'width': 500, 'minwidth': 200, 'text': 'Mensagem'}
        }
        
        for col in columns:
            config = logs_column_configs[col]
            self.logs_tree.heading(col, text=config['text'], command=lambda c=col: self.sort_logs_tree(c))
            self.logs_tree.column(col, width=config['width'], minwidth=config['minwidth'], stretch=True)
        
        # Bind eventos para logs
        self.logs_tree.bind('<Double-1>', self.on_logs_double_click)
        self.logs_tree.bind('<Button-1>', self.on_logs_click)
        
        # Scrollbars para logs
        logs_v_scrollbar = ttk.Scrollbar(logs_tree_frame, orient=tk.VERTICAL, command=self.logs_tree.yview)
        logs_h_scrollbar = ttk.Scrollbar(logs_tree_frame, orient=tk.HORIZONTAL, command=self.logs_tree.xview)
        self.logs_tree.configure(yscrollcommand=logs_v_scrollbar.set, xscrollcommand=logs_h_scrollbar.set)
        
        # Pack logs tree e scrollbars
        self.logs_tree.grid(row=0, column=0, sticky='nsew')
        logs_v_scrollbar.grid(row=0, column=1, sticky='ns')
        logs_h_scrollbar.grid(row=1, column=0, sticky='ew')
        
        # Configurar grid weights
        logs_tree_frame.grid_rowconfigure(0, weight=1)
        logs_tree_frame.grid_columnconfigure(0, weight=1)
    
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
        
        # Atualizar combos de telemetria e logs
        server_names = [server['name'] for server in self.servers]
        self.telemetry_combo['values'] = server_names
        self.logs_combo['values'] = server_names
        if server_names:
            self.telemetry_combo.set(server_names[0])
            self.logs_combo.set(server_names[0])
            # Atualizar exibição de logs inicial
            self.update_logs_display()
    
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
                self.root.after(0, self.update_logs_display)
                
                # Ajustar colunas automaticamente após atualização
                self.root.after(200, self.auto_adjust_columns)
                
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
                        app_port_status = f"❌ {app_port_number} ({app_port_data.get('status', 'Falhou')})"
                else:
                    app_port_status = f"{'✅' if app_port_data else '❌'} {app_port_number}"
                
                # Admin port status com número da porta e tempo de resposta
                admin_port_data = status_data.get('admin_port', {})
                admin_port_number = server.get('admin_port', 'N/A')
                if isinstance(admin_port_data, dict):
                    if admin_port_data.get('success'):
                        admin_port_status = f"✅ {admin_port_number} ({admin_port_data['response_time']}ms)"
                    else:
                        admin_port_status = f"❌ {admin_port_number} ({admin_port_data.get('status', 'Falhou')})"
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
                tag = 'online' if overall_status == 'ONLINE' else ('warning' if overall_status in ['ERRO_HTTP', 'PORTAS_FECHADAS'] else 'offline')
                
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
    
    def on_logs_server_change(self, event=None):
        """Chamado quando o servidor de logs é alterado"""
        self.update_logs_display()
    
    def update_logs_display(self):
        """Atualiza a exibição de logs para o servidor selecionado"""
        # Limpar logs atuais
        for item in self.logs_tree.get_children():
            self.logs_tree.delete(item)
        
        # Obter servidor selecionado
        selected_server = self.logs_combo.get()
        if not selected_server or not hasattr(self.monitor, 'get_server_logs'):
            return
        
        # Obter logs do servidor
        try:
            logs = self.monitor.get_server_logs(selected_server)
            
            # Adicionar logs à árvore (mais recentes primeiro)
            for log_entry in reversed(logs):
                timestamp = log_entry['timestamp']
                event_type = log_entry['event_type']
                message = log_entry['message']
                is_error = log_entry['is_error']
                
                # Definir cor baseada no tipo
                tag = 'error' if is_error else 'info'
                
                self.logs_tree.insert('', 0, values=(
                    timestamp,
                    event_type,
                    message
                ), tags=(tag,))
            
            # Configurar cores das tags
            self.logs_tree.tag_configure('error', foreground='red')
            self.logs_tree.tag_configure('info', foreground='black')
            
        except Exception as e:
            print(f"Erro ao atualizar logs: {e}")
    
    def clear_logs(self):
        """Limpa os logs do servidor selecionado"""
        selected_server = self.logs_combo.get()
        if not selected_server:
            messagebox.showwarning("Aviso", "Selecione um servidor primeiro.")
            return
        
        # Confirmar limpeza
        if messagebox.askyesno("Confirmar", f"Deseja limpar todos os logs do servidor '{selected_server}'?"):
            try:
                # Limpar logs no monitor
                if hasattr(self.monitor, 'server_logs') and selected_server in self.monitor.server_logs:
                    self.monitor.server_logs[selected_server] = []
                
                # Atualizar exibição
                self.update_logs_display()
                messagebox.showinfo("Sucesso", f"Logs do servidor '{selected_server}' foram limpos.")
            except Exception as e:
                messagebox.showerror("Erro", f"Erro ao limpar logs: {e}")
    
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
        
        # Adicionar ao logs_tree se existir
        if hasattr(self, 'logs_tree'):
            self.logs_tree.insert('', 0, values=(
                timestamp,
                'SYSTEM',
                message
            ), tags=('info',))
            
            # Configurar cor da tag
            self.logs_tree.tag_configure('info', foreground='blue')
    
    def clear_logs_old(self):
        """Função antiga removida - usar clear_logs da linha 540"""
        pass
    

    
    def on_server_double_click(self, event):
        """Manipula duplo clique em servidor - abre URL no navegador"""
        item = self.servers_tree.selection()[0] if self.servers_tree.selection() else None
        if not item:
            return
        
        # Obter dados do servidor
        values = self.servers_tree.item(item, 'values')
        if not values:
            return
        
        server_name = values[0]
        host = values[1]
        
        # Encontrar servidor na lista para obter URL de health check
        server_data = None
        for server in self.servers:
            if server['name'] == server_name:
                server_data = server
                break
        
        if server_data and server_data.get('health_url'):
            # Usar URL de health check se disponível
            url = server_data['health_url']
        else:
            # Construir URL básica com host e porta da aplicação
            app_port = server_data.get('app_port', 8080) if server_data else 8080
            protocol = 'https' if app_port == 443 else 'http'
            url = f"{protocol}://{host}:{app_port}"
        
        try:
            webbrowser.open(url)
            self.log_message(f"Abrindo URL no navegador: {url}")
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao abrir URL no navegador: {str(e)}")
    
    def on_server_click(self, event):
        """Manipula clique simples em servidor"""
        # Ajustar largura das colunas automaticamente após clique
        self.root.after(100, self.auto_adjust_columns)
    
    def auto_adjust_columns(self):
        """Ajusta automaticamente a largura das colunas baseado no conteúdo"""
        try:
            for col in self.servers_tree['columns']:
                # Calcular largura baseada no cabeçalho
                header_width = len(str(self.servers_tree.heading(col, 'text'))) * 8 + 20
                
                # Calcular largura baseada no conteúdo
                max_width = header_width
                for item in self.servers_tree.get_children():
                    values = self.servers_tree.item(item, 'values')
                    if values:
                        col_index = list(self.servers_tree['columns']).index(col)
                        if col_index < len(values):
                            content_width = len(str(values[col_index])) * 8 + 20
                            max_width = max(max_width, content_width)
                
                # Aplicar largura com limites mínimo e máximo
                min_width = 80
                max_allowed_width = 300
                final_width = max(min_width, min(max_width, max_allowed_width))
                
                self.servers_tree.column(col, width=final_width)
        except Exception as e:
            print(f"Erro ao ajustar colunas: {e}")
    
    def sort_servers_tree(self, col):
        """Ordena a árvore de servidores por coluna"""
        try:
            # Obter todos os itens
            items = [(self.servers_tree.set(item, col), item) for item in self.servers_tree.get_children('')]
            
            # Ordenar itens
            items.sort()
            
            # Reorganizar itens na árvore
            for index, (val, item) in enumerate(items):
                self.servers_tree.move(item, '', index)
                
        except Exception as e:
            print(f"Erro ao ordenar coluna {col}: {e}")
    
    def on_logs_double_click(self, event):
        """Manipula duplo clique em log - copia mensagem para clipboard"""
        item = self.logs_tree.selection()[0] if self.logs_tree.selection() else None
        if not item:
            return
        
        # Obter dados do log
        values = self.logs_tree.item(item, 'values')
        if not values or len(values) < 3:
            return
        
        # Copiar mensagem completa para clipboard
        message = values[2]  # Coluna de mensagem
        try:
            self.root.clipboard_clear()
            self.root.clipboard_append(message)
            self.root.update()  # Necessário para atualizar clipboard
            messagebox.showinfo("Copiado", "Mensagem copiada para a área de transferência!")
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao copiar mensagem: {str(e)}")
    
    def on_logs_click(self, event):
        """Manipula clique simples em log"""
        # Ajustar largura das colunas automaticamente após clique
        self.root.after(100, self.auto_adjust_logs_columns)
    
    def auto_adjust_logs_columns(self):
        """Ajusta automaticamente a largura das colunas de logs baseado no conteúdo"""
        try:
            for col in self.logs_tree['columns']:
                # Calcular largura baseada no cabeçalho
                header_width = len(str(self.logs_tree.heading(col, 'text'))) * 8 + 20
                
                # Calcular largura baseada no conteúdo
                max_width = header_width
                for item in self.logs_tree.get_children():
                    values = self.logs_tree.item(item, 'values')
                    if values:
                        col_index = list(self.logs_tree['columns']).index(col)
                        if col_index < len(values):
                            content_width = len(str(values[col_index])) * 8 + 10
                            max_width = max(max_width, content_width)
                
                # Aplicar largura com limites específicos para logs
                if col == 'timestamp':
                    min_width, max_allowed_width = 150, 200
                elif col == 'event_type':
                    min_width, max_allowed_width = 100, 150
                else:  # message
                    min_width, max_allowed_width = 200, 600
                
                final_width = max(min_width, min(max_width, max_allowed_width))
                self.logs_tree.column(col, width=final_width)
        except Exception as e:
            print(f"Erro ao ajustar colunas de logs: {e}")
    
    def sort_logs_tree(self, col):
        """Ordena a árvore de logs por coluna"""
        try:
            # Obter todos os itens
            items = [(self.logs_tree.set(item, col), item) for item in self.logs_tree.get_children('')]
            
            # Ordenar itens (reverso para timestamp para mostrar mais recentes primeiro)
            reverse_sort = (col == 'timestamp')
            items.sort(reverse=reverse_sort)
            
            # Reorganizar itens na árvore
            for index, (val, item) in enumerate(items):
                self.logs_tree.move(item, '', index)
                
        except Exception as e:
            print(f"Erro ao ordenar coluna de logs {col}: {e}")
    
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
        self.dialog.geometry("500x450")
        self.dialog.transient(parent)
        self.dialog.grab_set()
        self.dialog.resizable(False, False)
        
        # Centralizar janela
        self.dialog.geometry("+%d+%d" % (parent.winfo_rootx() + 50, parent.winfo_rooty() + 50))
        
        # Campos
        ttk.Label(self.dialog, text="Nome do Servidor:").pack(pady=5)
        self.name_entry = ttk.Entry(self.dialog, width=40)
        self.name_entry.pack(pady=5)
        
        # Frame para URL com botão de extração
        url_frame = ttk.Frame(self.dialog)
        url_frame.pack(pady=5, fill=tk.X, padx=20)
        
        ttk.Label(url_frame, text="URL (opcional - para extração automática):").pack(anchor=tk.W)
        url_input_frame = ttk.Frame(url_frame)
        url_input_frame.pack(fill=tk.X, pady=2)
        
        self.url_entry = ttk.Entry(url_input_frame, width=35)
        self.url_entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        extract_btn = ttk.Button(url_input_frame, text="📥 Extrair", command=self.extract_from_url, width=10)
        extract_btn.pack(side=tk.RIGHT, padx=(5, 0))
        
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
    
    def extract_from_url(self):
        """Extrai hostname, porta da aplicação e porta administrativa da URL fornecida"""
        url = self.url_entry.get().strip()
        if not url:
            messagebox.showwarning("Aviso", "Por favor, insira uma URL para extrair as informações.")
            return
        
        try:
            # Extrair hostname e porta
            hostname = extract_hostname_from_url(url)
            app_port = extract_port_from_url(url)
            admin_port = detect_admin_port(app_port)
            
            if hostname:
                # Preencher nome do servidor se estiver vazio
                if not self.name_entry.get().strip():
                    # Usar hostname como nome, removendo subdomínios se necessário
                    server_name = hostname
                    if hostname.startswith('www.'):
                        server_name = hostname[4:]  # Remove 'www.'
                    elif hostname.count('.') > 1:
                        # Para subdomínios como 'api.example.com', usar 'api-example'
                        parts = hostname.split('.')
                        if len(parts) >= 2:
                            server_name = f"{parts[0]}-{parts[1]}"
                    
                    self.name_entry.delete(0, tk.END)
                    self.name_entry.insert(0, server_name.title())
                
                # Limpar e preencher o campo host
                self.host_entry.delete(0, tk.END)
                self.host_entry.insert(0, hostname)
                
                # Preencher porta da aplicação
                self.app_port_entry.delete(0, tk.END)
                self.app_port_entry.insert(0, str(app_port))
                
                # Preencher porta administrativa
                self.admin_port_entry.delete(0, tk.END)
                self.admin_port_entry.insert(0, str(admin_port))
                
                # Preencher URL de health check
                self.health_url_entry.delete(0, tk.END)
                self.health_url_entry.insert(0, url)
                
                messagebox.showinfo("Sucesso", f"Formulário preenchido automaticamente:\nNome: {self.name_entry.get()}\nHost: {hostname}\nPorta App: {app_port}\nPorta Admin: {admin_port}")
            else:
                messagebox.showerror("Erro", "Não foi possível extrair o hostname da URL fornecida.")
                
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao processar URL: {str(e)}")
    
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