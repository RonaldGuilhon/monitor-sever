#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Interface Gráfica Principal do Monitorador de Servidores
Painel de telemetria em tempo real com cadastro de servidores
"""

import tkinter as tk
from tkinter import ttk
import threading
import time
from datetime import datetime
from collections import deque

from ..core import ServerMonitor
from ..config import CONFIG, SERVERS, load_config, save_config
from .dialogs import DarkMessageBox, ServerDialog
from .telemetry import TelemetryPanel
from .logs import LogsPanel


class ServerMonitorGUI:
    """Interface gráfica principal do monitorador de servidores"""
    
    def __init__(self, root):
        self.root = root
        self.root.title("Monitor de Servidores GlassFish")
        self.root.geometry("1200x800")
        
        # Configurar tema escuro
        self.setup_dark_theme()
        self.root.configure(bg='#2b2b2b')
        
        # Inicializar monitor
        self.monitor = ServerMonitor()
        self.servers = SERVERS.copy()
        
        # Variáveis de controle
        self.monitoring_active = False
        self.update_thread = None
        
        # Componentes da GUI
        self.telemetry_panel = None
        self.logs_panel = None
        
        self.setup_ui()
        self.load_servers_config()
        self.load_servers()
        
    def setup_dark_theme(self):
        """Configura o tema escuro para a aplicação"""
        style = ttk.Style()
        
        # Configurar tema escuro para ttk widgets
        style.theme_use('clam')
        
        # Cores do tema escuro
        dark_bg = '#2b2b2b'
        dark_fg = '#ffffff'
        dark_select_bg = '#404040'
        dark_select_fg = '#ffffff'
        button_bg = '#404040'
        button_fg = '#ffffff'
        
        # Configurar estilos
        style.configure('TFrame', background=dark_bg)
        style.configure('TLabel', background=dark_bg, foreground=dark_fg)
        style.configure('TButton', background=button_bg, foreground=button_fg)
        style.map('TButton', background=[('active', '#505050')])
        
        # Configurar Treeview (servidores - tema escuro)
        style.configure('Treeview', background='#3c3c3c', foreground=dark_fg, 
                       fieldbackground='#3c3c3c', borderwidth=0)
        style.configure('Treeview.Heading', background='#404040', foreground=dark_fg,
                       relief='flat')
        style.map('Treeview.Heading', background=[('active', '#505050')])
        style.map('Treeview', background=[('selected', dark_select_bg)],
                 foreground=[('selected', dark_select_fg)])
        
        # Configurar Treeview para logs (fundo branco)
        style.configure('Logs.Treeview', background='#ffffff', foreground='#000000', 
                       fieldbackground='#ffffff', borderwidth=1)
        style.configure('Logs.Treeview.Heading', background='#f0f0f0', foreground='#000000',
                       relief='flat')
        style.map('Logs.Treeview.Heading', background=[('active', '#e0e0e0')])
        style.map('Logs.Treeview', background=[('selected', '#0078d4')],
                 foreground=[('selected', '#ffffff')])
        
        # Configurar Notebook
        style.configure('TNotebook', background=dark_bg, borderwidth=0)
        style.configure('TNotebook.Tab', background='#404040', foreground=dark_fg,
                       padding=[20, 8])
        style.map('TNotebook.Tab', background=[('selected', '#505050'),
                                             ('active', '#4a4a4a')],
                 padding=[('selected', [25, 12]), ('active', [22, 10])])
        
        # Configurar Scrollbar
        style.configure('TScrollbar', background='#404040', troughcolor='#2b2b2b',
                       borderwidth=0, arrowcolor=dark_fg)
        style.map('TScrollbar', background=[('active', '#505050')])
        
        # Configurar Combobox
        style.configure('TCombobox', fieldbackground='#3c3c3c', background='#404040',
                       foreground=dark_fg, borderwidth=1)
        style.map('TCombobox', fieldbackground=[('readonly', '#3c3c3c')],
                 selectbackground=[('readonly', '#3c3c3c')])
        
    def setup_ui(self):
        """Configura a interface do usuário"""
        # Frame principal
        main_frame = ttk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Título
        title_label = tk.Label(main_frame, text="🖥️ Monitor de Servidores GlassFish", 
                              font=('Arial', 16, 'bold'), bg='#2b2b2b', fg='#ffffff')
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
                                    font=('Arial', 10), bg='#2b2b2b', fg='#ffffff')
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
            'Porta Admin': {'width': 90, 'minwidth': 80},
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
        
        # Configurar tags para cores (tema escuro)
        self.servers_tree.tag_configure('online', background='#1e4d2b', foreground='#ffffff')
        self.servers_tree.tag_configure('offline', background='#4d1e1e', foreground='#ffffff')
        self.servers_tree.tag_configure('warning', background='#4d3d1e', foreground='#ffffff')
        
        # Configurar cursor para indicar clicabilidade na coluna Admin
        self.servers_tree.bind('<Motion>', self.on_tree_motion)
    
    def setup_telemetry_tab(self):
        """Configura a aba de telemetria"""
        telemetry_frame = ttk.Frame(self.notebook)
        self.notebook.add(telemetry_frame, text="📈 Telemetria")
        
        # Criar painel de telemetria
        self.telemetry_panel = TelemetryPanel(telemetry_frame, self.servers)
    
    def setup_logs_tab(self):
        """Configura a aba de logs"""
        logs_frame = ttk.Frame(self.notebook)
        self.notebook.add(logs_frame, text="📝 Logs")
        
        # Criar painel de logs
        self.logs_panel = LogsPanel(logs_frame, self.servers, self.monitor)
    
    def load_servers_config(self):
        """Carrega configuração dos servidores"""
        try:
            config_data = load_config()
            if 'servers' in config_data:
                self.servers = config_data['servers']
        except Exception as e:
            print(f"Erro ao carregar configuração: {e}")
    
    def save_servers_config(self):
        """Salva configuração dos servidores"""
        try:
            config_data = load_config()
            config_data['servers'] = self.servers
            save_config(config_data)
        except Exception as e:
            print(f"Erro ao salvar configuração: {e}")
    
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
        
        # Atualizar painéis
        if self.telemetry_panel:
            self.telemetry_panel.update_servers(self.servers)
        if self.logs_panel:
            self.logs_panel.update_servers(self.servers)
    
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
            
            print("Monitoramento iniciado")
    
    def stop_monitoring(self):
        """Para o monitoramento"""
        if self.monitoring_active:
            self.monitoring_active = False
            self.monitor.stop_monitoring()
            
            # Atualizar botões
            self.start_btn.config(state=tk.NORMAL)
            self.stop_btn.config(state=tk.DISABLED)
            self.status_label.config(text="Status: Parado", fg='red')
            
            print("Monitoramento parado")
    
    def update_gui_loop(self):
        """Loop de atualização da GUI"""
        while self.monitoring_active:
            try:
                self.root.after(0, self.update_servers_display)
                if self.telemetry_panel:
                    self.root.after(0, self.telemetry_panel.update_display)
                if self.logs_panel:
                    self.root.after(0, self.logs_panel.update_display)
                
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
                # Determinar status geral
                ping_ok = status_data.get('ping', False)
                port_ok = status_data.get('port', False)
                http_ok = status_data.get('http', False)
                
                if ping_ok and port_ok and http_ok:
                    status = 'Online'
                    tag = 'online'
                elif ping_ok:
                    status = 'Parcial'
                    tag = 'warning'
                else:
                    status = 'Offline'
                    tag = 'offline'
                
                # Formatar valores
                ping_text = '✓' if ping_ok else '✗'
                port_text = '✓' if port_ok else '✗'
                http_text = '✓' if http_ok else '✗'
                last_check = status_data.get('timestamp', '-')
                
                item = self.servers_tree.insert('', tk.END, values=(
                    name, server['host'], ping_text, port_text, '-', http_text, status, last_check
                ), tags=(tag,))
                
                # Restaurar seleção se necessário
                if name in selected_server_names:
                    self.servers_tree.selection_add(item)
            else:
                self.servers_tree.insert('', tk.END, values=(
                    name, server['host'], '-', '-', '-', '-', 'Não verificado', '-'
                ))
    
    def add_server_dialog(self):
        """Abre diálogo para adicionar servidor"""
        dialog = ServerDialog(self.root, "Adicionar Servidor")
        result = dialog.show()
        
        if result:
            self.servers.append(result)
            self.save_servers_config()
            self.load_servers()
    
    def edit_server_dialog(self):
        """Abre diálogo para editar servidor"""
        selected = self.servers_tree.selection()
        if not selected:
            DarkMessageBox.showwarning("Aviso", "Selecione um servidor para editar.", self.root)
            return
        
        # Obter dados do servidor selecionado
        item = selected[0]
        values = self.servers_tree.item(item, 'values')
        server_name = values[0]
        
        # Encontrar servidor na lista
        server_data = None
        server_index = None
        for i, server in enumerate(self.servers):
            if server['name'] == server_name:
                server_data = server
                server_index = i
                break
        
        if server_data:
            dialog = ServerDialog(self.root, "Editar Servidor", server_data)
            result = dialog.show()
            
            if result:
                self.servers[server_index] = result
                self.save_servers_config()
                self.load_servers()
    
    def remove_server_dialog(self):
        """Remove servidor selecionado"""
        selected = self.servers_tree.selection()
        if not selected:
            DarkMessageBox.showwarning("Aviso", "Selecione um servidor para remover.", self.root)
            return
        
        # Obter nome do servidor
        item = selected[0]
        values = self.servers_tree.item(item, 'values')
        server_name = values[0]
        
        # Confirmar remoção
        if DarkMessageBox.askyesno("Confirmar", f"Deseja remover o servidor '{server_name}'?", self.root):
            # Remover da lista
            self.servers = [s for s in self.servers if s['name'] != server_name]
            self.save_servers_config()
            self.load_servers()
    
    def show_config_dialog(self):
        """Mostra diálogo de configurações"""
        # TODO: Implementar diálogo de configurações
        DarkMessageBox.showinfo("Configurações", "Diálogo de configurações em desenvolvimento.", self.root)
    
    def sort_servers_tree(self, col):
        """Ordena a árvore de servidores por coluna"""
        # TODO: Implementar ordenação
        pass
    
    def on_server_double_click(self, event):
        """Manipula duplo clique em servidor"""
        self.edit_server_dialog()
    
    def on_server_click(self, event):
        """Manipula clique simples em servidor"""
        pass
    
    def on_tree_motion(self, event):
        """Manipula movimento do mouse sobre a árvore"""
        pass


def main():
    """Função principal para executar a GUI"""
    root = tk.Tk()
    app = ServerMonitorGUI(root)
    root.mainloop()


if __name__ == '__main__':
    main()