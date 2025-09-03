#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Painel de logs para visualização de eventos do sistema
"""

import tkinter as tk
from tkinter import ttk
from datetime import datetime
import json


class LogsPanel:
    """Painel para visualização e gerenciamento de logs"""
    
    def __init__(self, parent_frame, servers, monitor):
        self.parent_frame = parent_frame
        self.servers = servers
        self.monitor = monitor
        
        # Variáveis de controle
        self.selected_server = None
        self.sort_column = None
        self.sort_reverse = False
        
        # Widgets
        self.server_combo = None
        self.logs_tree = None
        
        self._setup_ui()
    
    def _setup_ui(self):
        """Configura a interface do painel"""
        # Frame superior para controles
        control_frame = ttk.Frame(self.parent_frame)
        control_frame.pack(fill=tk.X, padx=5, pady=5)
        
        # Label e combobox para seleção de servidor
        ttk.Label(control_frame, text="Servidor:").pack(side=tk.LEFT, padx=(0, 5))
        
        self.server_var = tk.StringVar()
        self.server_combo = ttk.Combobox(control_frame, textvariable=self.server_var, 
                                        state="readonly", width=20)
        self.server_combo.pack(side=tk.LEFT, padx=(0, 10))
        self.server_combo.bind('<<ComboboxSelected>>', self._on_server_change)
        
        # Botão para limpar logs
        clear_logs_btn = ttk.Button(control_frame, text="🗑️ Limpar Logs", 
                                   command=self._clear_logs)
        clear_logs_btn.pack(side=tk.LEFT, padx=5)
        
        # Botão para exportar logs
        export_logs_btn = ttk.Button(control_frame, text="📤 Exportar Logs", 
                                    command=self._export_logs)
        export_logs_btn.pack(side=tk.LEFT, padx=5)
        
        # Botão para atualizar
        refresh_btn = ttk.Button(control_frame, text="🔄 Atualizar", 
                                command=self._refresh_logs)
        refresh_btn.pack(side=tk.LEFT, padx=5)
        
        # Frame para logs com scrollbar
        logs_tree_frame = ttk.Frame(self.parent_frame)
        logs_tree_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # TreeView para logs estruturados (com fundo branco)
        columns = ('timestamp', 'event_type', 'message', 'details')
        self.logs_tree = ttk.Treeview(logs_tree_frame, columns=columns, show='headings', 
                                     height=20, style='Logs.Treeview')
        
        # Configurar colunas
        column_configs = {
            'timestamp': {'width': 180, 'minwidth': 150, 'text': 'Timestamp'},
            'event_type': {'width': 120, 'minwidth': 100, 'text': 'Tipo'},
            'message': {'width': 400, 'minwidth': 200, 'text': 'Mensagem'},
            'details': {'width': 200, 'minwidth': 150, 'text': 'Detalhes'}
        }
        
        for col in columns:
            config = column_configs[col]
            self.logs_tree.heading(col, text=config['text'], 
                                  command=lambda c=col: self._sort_logs(c))
            self.logs_tree.column(col, width=config['width'], 
                                 minwidth=config['minwidth'], stretch=True)
        
        # Bind eventos para logs
        self.logs_tree.bind('<Double-1>', self._on_log_double_click)
        self.logs_tree.bind('<Button-1>', self._on_log_click)
        
        # Scrollbars para logs
        v_scrollbar = ttk.Scrollbar(logs_tree_frame, orient=tk.VERTICAL, 
                                   command=self.logs_tree.yview)
        h_scrollbar = ttk.Scrollbar(logs_tree_frame, orient=tk.HORIZONTAL, 
                                   command=self.logs_tree.xview)
        self.logs_tree.configure(yscrollcommand=v_scrollbar.set, 
                                xscrollcommand=h_scrollbar.set)
        
        # Grid layout
        self.logs_tree.grid(row=0, column=0, sticky='nsew')
        v_scrollbar.grid(row=0, column=1, sticky='ns')
        h_scrollbar.grid(row=1, column=0, sticky='ew')
        
        # Configurar grid weights
        logs_tree_frame.grid_rowconfigure(0, weight=1)
        logs_tree_frame.grid_columnconfigure(0, weight=1)
        
        # Configurar tags para diferentes tipos de eventos
        self.logs_tree.tag_configure('info', background='#e8f4fd', foreground='#0066cc')
        self.logs_tree.tag_configure('warning', background='#fff3cd', foreground='#856404')
        self.logs_tree.tag_configure('error', background='#f8d7da', foreground='#721c24')
        self.logs_tree.tag_configure('success', background='#d4edda', foreground='#155724')
        self.logs_tree.tag_configure('server_down', background='#f8d7da', foreground='#721c24')
        self.logs_tree.tag_configure('server_up', background='#d4edda', foreground='#155724')
    
    def update_servers(self, servers):
        """Atualiza a lista de servidores"""
        self.servers = servers
        
        # Atualizar combo
        server_names = [server['name'] for server in servers]
        self.server_combo['values'] = server_names
        
        if server_names and not self.server_var.get():
            self.server_var.set(server_names[0])
            self.selected_server = server_names[0]
            self._refresh_logs()
    
    def _on_server_change(self, event=None):
        """Manipula mudança de servidor selecionado"""
        self.selected_server = self.server_var.get()
        self._refresh_logs()
    
    def _refresh_logs(self):
        """Atualiza a exibição dos logs"""
        if not self.selected_server:
            return
        
        # Limpar árvore
        for item in self.logs_tree.get_children():
            self.logs_tree.delete(item)
        
        # Obter logs do servidor selecionado
        logs = self._get_server_logs(self.selected_server)
        
        # Adicionar logs à árvore
        for log_entry in logs:
            self._add_log_to_tree(log_entry)
    
    def _get_server_logs(self, server_name):
        """Obtém logs de um servidor específico"""
        if not self.monitor or not hasattr(self.monitor, 'get_server_logs'):
            return []
        
        try:
            return self.monitor.get_server_logs(server_name)
        except Exception as e:
            print(f"Erro ao obter logs do servidor {server_name}: {e}")
            return []
    
    def _add_log_to_tree(self, log_entry):
        """Adiciona uma entrada de log à árvore"""
        try:
            # Extrair informações do log
            timestamp = log_entry.get('timestamp', '')
            event_type = log_entry.get('event_type', 'info')
            message = log_entry.get('message', '')
            details = log_entry.get('details', '')
            
            # Formatar timestamp se necessário
            if isinstance(timestamp, datetime):
                timestamp = timestamp.strftime('%Y-%m-%d %H:%M:%S')
            
            # Determinar tag baseada no tipo de evento
            tag = self._get_log_tag(event_type, message)
            
            # Adicionar à árvore
            self.logs_tree.insert('', tk.END, values=(
                timestamp, event_type, message, details
            ), tags=(tag,))
            
        except Exception as e:
            print(f"Erro ao adicionar log à árvore: {e}")
    
    def _get_log_tag(self, event_type, message):
        """Determina a tag apropriada para um log"""
        event_type = event_type.lower()
        message = message.lower()
        
        if 'error' in event_type or 'erro' in message:
            return 'error'
        elif 'warning' in event_type or 'aviso' in message:
            return 'warning'
        elif 'server_down' in event_type or 'servidor inativo' in message:
            return 'server_down'
        elif 'server_up' in event_type or 'servidor ativo' in message:
            return 'server_up'
        elif 'success' in event_type or 'sucesso' in message:
            return 'success'
        else:
            return 'info'
    
    def _sort_logs(self, column):
        """Ordena os logs por coluna"""
        # Alternar direção da ordenação se a mesma coluna for clicada
        if self.sort_column == column:
            self.sort_reverse = not self.sort_reverse
        else:
            self.sort_reverse = False
        
        self.sort_column = column
        
        # Obter todos os itens
        items = [(self.logs_tree.item(item, 'values'), item) 
                for item in self.logs_tree.get_children()]
        
        # Determinar índice da coluna
        columns = ('timestamp', 'event_type', 'message', 'details')
        col_index = columns.index(column)
        
        # Ordenar itens
        if column == 'timestamp':
            # Ordenação especial para timestamps
            items.sort(key=lambda x: x[0][col_index], reverse=self.sort_reverse)
        else:
            items.sort(key=lambda x: x[0][col_index].lower(), reverse=self.sort_reverse)
        
        # Reorganizar itens na árvore
        for index, (values, item) in enumerate(items):
            self.logs_tree.move(item, '', index)
    
    def _clear_logs(self):
        """Limpa os logs do servidor selecionado"""
        if not self.selected_server:
            from .dialogs import DarkMessageBox
            DarkMessageBox.showwarning("Aviso", "Selecione um servidor primeiro.", self.parent_frame)
            return
        
        from .dialogs import DarkMessageBox
        if DarkMessageBox.askyesno("Confirmar", 
                                  f"Deseja limpar todos os logs do servidor '{self.selected_server}'?", 
                                  self.parent_frame):
            try:
                # Limpar logs no monitor
                if self.monitor and hasattr(self.monitor, 'clear_server_logs'):
                    self.monitor.clear_server_logs(self.selected_server)
                
                # Atualizar exibição
                self._refresh_logs()
                
                DarkMessageBox.showinfo("Sucesso", "Logs limpos com sucesso.", self.parent_frame)
                
            except Exception as e:
                DarkMessageBox.showerror("Erro", f"Erro ao limpar logs: {e}", self.parent_frame)
    
    def _export_logs(self):
        """Exporta os logs para um arquivo"""
        if not self.selected_server:
            from .dialogs import DarkMessageBox
            DarkMessageBox.showwarning("Aviso", "Selecione um servidor primeiro.", self.parent_frame)
            return
        
        try:
            from tkinter import filedialog
            
            # Solicitar local para salvar
            filename = filedialog.asksaveasfilename(
                title="Exportar Logs",
                defaultextension=".json",
                filetypes=[("JSON files", "*.json"), ("Text files", "*.txt"), ("All files", "*.*")]
            )
            
            if filename:
                # Obter logs
                logs = self._get_server_logs(self.selected_server)
                
                if filename.endswith('.json'):
                    # Exportar como JSON
                    with open(filename, 'w', encoding='utf-8') as f:
                        json.dump(logs, f, indent=2, ensure_ascii=False, default=str)
                else:
                    # Exportar como texto
                    with open(filename, 'w', encoding='utf-8') as f:
                        f.write(f"Logs do Servidor: {self.selected_server}\n")
                        f.write(f"Exportado em: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                        f.write("=" * 80 + "\n\n")
                        
                        for log_entry in logs:
                            timestamp = log_entry.get('timestamp', '')
                            event_type = log_entry.get('event_type', '')
                            message = log_entry.get('message', '')
                            details = log_entry.get('details', '')
                            
                            f.write(f"[{timestamp}] {event_type.upper()}: {message}\n")
                            if details:
                                f.write(f"  Detalhes: {details}\n")
                            f.write("\n")
                
                from .dialogs import DarkMessageBox
                DarkMessageBox.showinfo("Sucesso", f"Logs exportados para: {filename}", self.parent_frame)
                
        except Exception as e:
            from .dialogs import DarkMessageBox
            DarkMessageBox.showerror("Erro", f"Erro ao exportar logs: {e}", self.parent_frame)
    
    def _on_log_double_click(self, event):
        """Manipula duplo clique em um log"""
        selected = self.logs_tree.selection()
        if not selected:
            return
        
        item = selected[0]
        values = self.logs_tree.item(item, 'values')
        
        if values:
            # Mostrar detalhes do log em uma janela
            self._show_log_details(values)
    
    def _show_log_details(self, log_values):
        """Mostra detalhes completos de um log"""
        timestamp, event_type, message, details = log_values
        
        # Criar janela de detalhes
        details_window = tk.Toplevel(self.parent_frame)
        details_window.title("Detalhes do Log")
        details_window.configure(bg='#2b2b2b')
        details_window.geometry("600x400")
        details_window.transient(self.parent_frame)
        
        # Frame principal
        main_frame = tk.Frame(details_window, bg='#2b2b2b', padx=20, pady=20)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Título
        title_label = tk.Label(main_frame, text="Detalhes do Log", 
                              font=('Arial', 14, 'bold'), bg='#2b2b2b', fg='#ffffff')
        title_label.pack(pady=(0, 20))
        
        # Informações do log
        info_frame = tk.Frame(main_frame, bg='#2b2b2b')
        info_frame.pack(fill=tk.BOTH, expand=True)
        
        # Labels e valores
        fields = [
            ('Timestamp:', timestamp),
            ('Tipo:', event_type),
            ('Mensagem:', message),
            ('Detalhes:', details)
        ]
        
        for i, (label_text, value) in enumerate(fields):
            # Label
            label = tk.Label(info_frame, text=label_text, font=('Arial', 10, 'bold'),
                           bg='#2b2b2b', fg='#ffffff')
            label.grid(row=i, column=0, sticky='nw', pady=5, padx=(0, 10))
            
            # Valor
            if label_text == 'Detalhes:' and len(value) > 50:
                # Usar Text widget para detalhes longos
                text_widget = tk.Text(info_frame, height=8, width=50, 
                                     bg='#3c3c3c', fg='#ffffff', 
                                     font=('Arial', 9), wrap=tk.WORD)
                text_widget.insert('1.0', value)
                text_widget.config(state=tk.DISABLED)
                text_widget.grid(row=i, column=1, sticky='ew', pady=5)
            else:
                value_label = tk.Label(info_frame, text=value, font=('Arial', 10),
                                     bg='#2b2b2b', fg='#ffffff', wraplength=400, justify=tk.LEFT)
                value_label.grid(row=i, column=1, sticky='w', pady=5)
        
        # Configurar grid weights
        info_frame.grid_columnconfigure(1, weight=1)
        
        # Botão fechar
        close_btn = tk.Button(main_frame, text="Fechar", command=details_window.destroy,
                            bg='#404040', fg='#ffffff', font=('Arial', 10), padx=20, pady=5,
                            relief=tk.RAISED, borderwidth=1, cursor='hand2')
        close_btn.pack(pady=(20, 0))
        
        # Efeito hover
        def on_enter(e):
            close_btn.configure(bg='#505050')
        def on_leave(e):
            close_btn.configure(bg='#404040')
        
        close_btn.bind('<Enter>', on_enter)
        close_btn.bind('<Leave>', on_leave)
    
    def _on_log_click(self, event):
        """Manipula clique simples em um log"""
        pass
    
    def update_display(self):
        """Atualiza a exibição dos logs"""
        if self.selected_server:
            self._refresh_logs()
    
    def add_log_entry(self, server_name, event_type, message, details=""):
        """Adiciona uma nova entrada de log"""
        if server_name == self.selected_server:
            log_entry = {
                'timestamp': datetime.now(),
                'event_type': event_type,
                'message': message,
                'details': details
            }
            self._add_log_to_tree(log_entry)