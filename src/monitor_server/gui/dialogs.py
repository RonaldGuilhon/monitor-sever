#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Diálogos personalizados para a interface gráfica
"""

import tkinter as tk
from tkinter import ttk, messagebox
from ..utils.network_utils import validate_url, extract_hostname_from_url, extract_port_from_url


class DarkMessageBox:
    """Classe para messagebox com tema escuro"""
    
    @staticmethod
    def _create_dialog(parent, title, message, dialog_type="info", buttons=None):
        """Cria um diálogo personalizado com tema escuro"""
        dialog = tk.Toplevel(parent if parent else tk._default_root)
        dialog.title(title)
        dialog.configure(bg='#2b2b2b')
        dialog.resizable(False, False)
        dialog.transient(parent if parent else tk._default_root)
        dialog.grab_set()
        
        # Centralizar janela
        if parent:
            dialog.geometry("+%d+%d" % (parent.winfo_rootx() + 100, parent.winfo_rooty() + 100))
        
        # Frame principal
        main_frame = tk.Frame(dialog, bg='#2b2b2b', padx=20, pady=20)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Ícone e mensagem
        icon_text = {"info": "ℹ️", "warning": "⚠️", "error": "❌", "question": "❓"}.get(dialog_type, "ℹ️")
        
        # Frame para ícone e texto
        content_frame = tk.Frame(main_frame, bg='#2b2b2b')
        content_frame.pack(pady=(0, 20))
        
        # Ícone
        icon_label = tk.Label(content_frame, text=icon_text, font=('Arial', 24), bg='#2b2b2b', fg='#ffffff')
        icon_label.pack(side=tk.LEFT, padx=(0, 15))
        
        # Mensagem
        msg_label = tk.Label(content_frame, text=message, font=('Arial', 10), bg='#2b2b2b', fg='#ffffff', wraplength=300, justify=tk.LEFT)
        msg_label.pack(side=tk.LEFT)
        
        # Botões
        button_frame = tk.Frame(main_frame, bg='#2b2b2b')
        button_frame.pack()
        
        result = [None]
        
        def button_click(value):
            result[0] = value
            dialog.destroy()
        
        if buttons:
            for i, (text, value) in enumerate(buttons):
                btn = tk.Button(button_frame, text=text, command=lambda v=value: button_click(v),
                              bg='#404040', fg='#ffffff', font=('Arial', 9), padx=15, pady=5,
                              relief=tk.RAISED, borderwidth=1, cursor='hand2')
                btn.pack(side=tk.LEFT, padx=5)
                
                # Efeitos hover
                def on_enter(e, button=btn):
                    button.configure(bg='#505050')
                def on_leave(e, button=btn):
                    button.configure(bg='#404040')
                
                btn.bind('<Enter>', on_enter)
                btn.bind('<Leave>', on_leave)
        
        # Bind Escape para fechar
        dialog.bind('<Escape>', lambda e: dialog.destroy())
        
        # Aguardar resultado
        dialog.wait_window()
        return result[0]
    
    @staticmethod
    def showinfo(title, message, parent=None):
        """Mostra diálogo de informação"""
        DarkMessageBox._create_dialog(parent, title, message, "info", [("OK", True)])
    
    @staticmethod
    def showwarning(title, message, parent=None):
        """Mostra diálogo de aviso"""
        DarkMessageBox._create_dialog(parent, title, message, "warning", [("OK", True)])
    
    @staticmethod
    def showerror(title, message, parent=None):
        """Mostra diálogo de erro"""
        DarkMessageBox._create_dialog(parent, title, message, "error", [("OK", True)])
    
    @staticmethod
    def askyesno(title, message, parent=None):
        """Mostra diálogo de confirmação sim/não"""
        result = DarkMessageBox._create_dialog(parent, title, message, "question", [("Sim", True), ("Não", False)])
        return result if result is not None else False


class ServerDialog:
    """Diálogo para adicionar/editar servidores"""
    
    def __init__(self, parent, title, server_data=None):
        self.parent = parent
        self.title = title
        self.server_data = server_data or {}
        self.result = None
        
        self.dialog = None
        self.name_var = tk.StringVar()
        self.host_var = tk.StringVar()
        self.app_port_var = tk.StringVar()
        self.admin_port_var = tk.StringVar()
        self.url_var = tk.StringVar()
        self.description_var = tk.StringVar()
        
        # Preencher com dados existentes se fornecidos
        if self.server_data:
            self.name_var.set(self.server_data.get('name', ''))
            self.host_var.set(self.server_data.get('host', ''))
            self.app_port_var.set(str(self.server_data.get('app_port', '')))
            self.admin_port_var.set(str(self.server_data.get('admin_port', '')))
            self.url_var.set(self.server_data.get('url', ''))
            self.description_var.set(self.server_data.get('description', ''))
    
    def show(self):
        """Mostra o diálogo e retorna o resultado"""
        self.dialog = tk.Toplevel(self.parent)
        self.dialog.title(self.title)
        self.dialog.configure(bg='#2b2b2b')
        self.dialog.resizable(False, False)
        self.dialog.transient(self.parent)
        self.dialog.grab_set()
        
        # Centralizar janela
        self.dialog.geometry("+%d+%d" % (self.parent.winfo_rootx() + 50, self.parent.winfo_rooty() + 50))
        
        self._create_widgets()
        
        # Aguardar resultado
        self.dialog.wait_window()
        return self.result
    
    def _create_widgets(self):
        """Cria os widgets do diálogo"""
        # Frame principal
        main_frame = tk.Frame(self.dialog, bg='#2b2b2b', padx=20, pady=20)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Campos do formulário
        fields = [
            ('Nome do Servidor:', self.name_var, True),
            ('Host/IP:', self.host_var, True),
            ('Porta da Aplicação:', self.app_port_var, False),
            ('Porta de Admin:', self.admin_port_var, False),
            ('URL de Teste:', self.url_var, False),
            ('Descrição:', self.description_var, False)
        ]
        
        self.entries = {}
        
        for i, (label_text, var, required) in enumerate(fields):
            # Label
            label = tk.Label(main_frame, text=label_text, bg='#2b2b2b', fg='#ffffff', font=('Arial', 10))
            label.grid(row=i, column=0, sticky='w', pady=5, padx=(0, 10))
            
            # Entry
            entry = tk.Entry(main_frame, textvariable=var, bg='#3c3c3c', fg='#ffffff', 
                           font=('Arial', 10), width=30, insertbackground='#ffffff')
            entry.grid(row=i, column=1, sticky='ew', pady=5)
            
            # Marcar campos obrigatórios
            if required:
                req_label = tk.Label(main_frame, text='*', bg='#2b2b2b', fg='#ff6b6b', font=('Arial', 12, 'bold'))
                req_label.grid(row=i, column=2, sticky='w', padx=(5, 0))
            
            self.entries[var] = entry
        
        # Configurar grid weights
        main_frame.grid_columnconfigure(1, weight=1)
        
        # Frame para botões
        button_frame = tk.Frame(main_frame, bg='#2b2b2b')
        button_frame.grid(row=len(fields), column=0, columnspan=3, pady=(20, 0), sticky='ew')
        
        # Botões
        save_btn = tk.Button(button_frame, text="Salvar", command=self._save_server,
                           bg='#404040', fg='#ffffff', font=('Arial', 10), padx=20, pady=5,
                           relief=tk.RAISED, borderwidth=1, cursor='hand2')
        save_btn.pack(side=tk.RIGHT, padx=(5, 0))
        
        cancel_btn = tk.Button(button_frame, text="Cancelar", command=self._cancel,
                             bg='#404040', fg='#ffffff', font=('Arial', 10), padx=20, pady=5,
                             relief=tk.RAISED, borderwidth=1, cursor='hand2')
        cancel_btn.pack(side=tk.RIGHT)
        
        # Efeitos hover para botões
        def on_enter(e, button):
            button.configure(bg='#505050')
        def on_leave(e, button):
            button.configure(bg='#404040')
        
        for btn in [save_btn, cancel_btn]:
            btn.bind('<Enter>', lambda e, b=btn: on_enter(e, b))
            btn.bind('<Leave>', lambda e, b=btn: on_leave(e, b))
        
        # Bind Enter e Escape
        self.dialog.bind('<Return>', lambda e: self._save_server())
        self.dialog.bind('<Escape>', lambda e: self._cancel())
        
        # Focar no primeiro campo
        self.entries[self.name_var].focus_set()
    
    def _save_server(self):
        """Salva os dados do servidor"""
        # Validar campos obrigatórios
        if not self.name_var.get().strip():
            DarkMessageBox.showerror("Erro", "Nome do servidor é obrigatório.", self.dialog)
            return
        
        if not self.host_var.get().strip():
            DarkMessageBox.showerror("Erro", "Host/IP é obrigatório.", self.dialog)
            return
        
        # Validar portas se fornecidas
        app_port = self.app_port_var.get().strip()
        admin_port = self.admin_port_var.get().strip()
        
        if app_port:
            try:
                app_port = int(app_port)
                if not (1 <= app_port <= 65535):
                    raise ValueError()
            except ValueError:
                DarkMessageBox.showerror("Erro", "Porta da aplicação deve ser um número entre 1 e 65535.", self.dialog)
                return
        else:
            app_port = None
        
        if admin_port:
            try:
                admin_port = int(admin_port)
                if not (1 <= admin_port <= 65535):
                    raise ValueError()
            except ValueError:
                DarkMessageBox.showerror("Erro", "Porta de admin deve ser um número entre 1 e 65535.", self.dialog)
                return
        else:
            admin_port = None
        
        # Validar URL se fornecida
        url = self.url_var.get().strip()
        if url and not validate_url(url):
            DarkMessageBox.showerror("Erro", "URL de teste inválida.", self.dialog)
            return
        
        # Criar dados do servidor
        self.result = {
            'name': self.name_var.get().strip(),
            'host': self.host_var.get().strip(),
            'app_port': app_port,
            'admin_port': admin_port,
            'url': url,
            'description': self.description_var.get().strip()
        }
        
        self.dialog.destroy()
    
    def _cancel(self):
        """Cancela o diálogo"""
        self.result = None
        self.dialog.destroy()


class ConfigDialog:
    """Diálogo para configurações do sistema"""
    
    def __init__(self, parent, config_data):
        self.parent = parent
        self.config_data = config_data.copy()
        self.result = None
        
        self.dialog = None
        
        # Variáveis para configurações
        self.ping_timeout_var = tk.StringVar(value=str(config_data.get('ping_timeout', 5)))
        self.http_timeout_var = tk.StringVar(value=str(config_data.get('http_timeout', 10)))
        self.monitor_interval_var = tk.StringVar(value=str(config_data.get('monitor_interval', 30)))
        self.email_enabled_var = tk.BooleanVar(value=config_data.get('email_alerts', {}).get('enabled', False))
        self.sound_enabled_var = tk.BooleanVar(value=config_data.get('sound_alerts', {}).get('enabled', True))
    
    def show(self):
        """Mostra o diálogo e retorna o resultado"""
        self.dialog = tk.Toplevel(self.parent)
        self.dialog.title("Configurações")
        self.dialog.configure(bg='#2b2b2b')
        self.dialog.resizable(False, False)
        self.dialog.transient(self.parent)
        self.dialog.grab_set()
        
        # Centralizar janela
        self.dialog.geometry("+%d+%d" % (self.parent.winfo_rootx() + 50, self.parent.winfo_rooty() + 50))
        
        self._create_widgets()
        
        # Aguardar resultado
        self.dialog.wait_window()
        return self.result
    
    def _create_widgets(self):
        """Cria os widgets do diálogo"""
        # Frame principal
        main_frame = tk.Frame(self.dialog, bg='#2b2b2b', padx=20, pady=20)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Notebook para abas
        notebook = ttk.Notebook(main_frame)
        notebook.pack(fill=tk.BOTH, expand=True, pady=(0, 20))
        
        # Aba de Monitoramento
        monitor_frame = ttk.Frame(notebook)
        notebook.add(monitor_frame, text="Monitoramento")
        
        # Configurações de monitoramento
        monitor_fields = [
            ('Timeout de Ping (segundos):', self.ping_timeout_var),
            ('Timeout HTTP (segundos):', self.http_timeout_var),
            ('Intervalo de Monitoramento (segundos):', self.monitor_interval_var)
        ]
        
        for i, (label_text, var) in enumerate(monitor_fields):
            tk.Label(monitor_frame, text=label_text, bg='#2b2b2b', fg='#ffffff', font=('Arial', 10)).grid(
                row=i, column=0, sticky='w', pady=5, padx=10
            )
            tk.Entry(monitor_frame, textvariable=var, bg='#3c3c3c', fg='#ffffff', 
                   font=('Arial', 10), width=20, insertbackground='#ffffff').grid(
                row=i, column=1, sticky='ew', pady=5, padx=10
            )
        
        # Aba de Alertas
        alerts_frame = ttk.Frame(notebook)
        notebook.add(alerts_frame, text="Alertas")
        
        # Configurações de alertas
        tk.Checkbutton(alerts_frame, text="Habilitar alertas por e-mail", variable=self.email_enabled_var,
                      bg='#2b2b2b', fg='#ffffff', selectcolor='#404040', font=('Arial', 10)).pack(
            anchor='w', pady=5, padx=10
        )
        
        tk.Checkbutton(alerts_frame, text="Habilitar alertas sonoros", variable=self.sound_enabled_var,
                      bg='#2b2b2b', fg='#ffffff', selectcolor='#404040', font=('Arial', 10)).pack(
            anchor='w', pady=5, padx=10
        )
        
        # Frame para botões
        button_frame = tk.Frame(main_frame, bg='#2b2b2b')
        button_frame.pack(fill=tk.X)
        
        # Botões
        save_btn = tk.Button(button_frame, text="Salvar", command=self._save_config,
                           bg='#404040', fg='#ffffff', font=('Arial', 10), padx=20, pady=5,
                           relief=tk.RAISED, borderwidth=1, cursor='hand2')
        save_btn.pack(side=tk.RIGHT, padx=(5, 0))
        
        cancel_btn = tk.Button(button_frame, text="Cancelar", command=self._cancel,
                             bg='#404040', fg='#ffffff', font=('Arial', 10), padx=20, pady=5,
                             relief=tk.RAISED, borderwidth=1, cursor='hand2')
        cancel_btn.pack(side=tk.RIGHT)
        
        # Efeitos hover para botões
        def on_enter(e, button):
            button.configure(bg='#505050')
        def on_leave(e, button):
            button.configure(bg='#404040')
        
        for btn in [save_btn, cancel_btn]:
            btn.bind('<Enter>', lambda e, b=btn: on_enter(e, b))
            btn.bind('<Leave>', lambda e, b=btn: on_leave(e, b))
        
        # Bind Enter e Escape
        self.dialog.bind('<Return>', lambda e: self._save_config())
        self.dialog.bind('<Escape>', lambda e: self._cancel())
    
    def _save_config(self):
        """Salva as configurações"""
        try:
            # Validar valores numéricos
            ping_timeout = float(self.ping_timeout_var.get())
            http_timeout = float(self.http_timeout_var.get())
            monitor_interval = float(self.monitor_interval_var.get())
            
            if ping_timeout <= 0 or http_timeout <= 0 or monitor_interval <= 0:
                raise ValueError("Valores devem ser positivos")
            
            # Atualizar configurações
            self.config_data.update({
                'ping_timeout': ping_timeout,
                'http_timeout': http_timeout,
                'monitor_interval': monitor_interval,
                'email_alerts': {
                    **self.config_data.get('email_alerts', {}),
                    'enabled': self.email_enabled_var.get()
                },
                'sound_alerts': {
                    **self.config_data.get('sound_alerts', {}),
                    'enabled': self.sound_enabled_var.get()
                }
            })
            
            self.result = self.config_data
            self.dialog.destroy()
            
        except ValueError as e:
            DarkMessageBox.showerror("Erro", "Valores inválidos. Verifique os campos numéricos.", self.dialog)
    
    def _cancel(self):
        """Cancela o diálogo"""
        self.result = None
        self.dialog.destroy()