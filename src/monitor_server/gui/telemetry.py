#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Painel de telemetria para monitoramento em tempo real
"""

import tkinter as tk
from tkinter import ttk
from datetime import datetime, timedelta
from collections import deque
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
import matplotlib.animation as animation


class TelemetryPanel:
    """Painel de telemetria com gráficos em tempo real"""
    
    def __init__(self, parent_frame, servers):
        self.parent_frame = parent_frame
        self.servers = servers
        
        # Dados para telemetria
        self.telemetry_data = {}
        self.max_data_points = 50
        
        # Variáveis de controle
        self.selected_server = None
        
        # Widgets
        self.server_combo = None
        self.canvas = None
        self.fig = None
        
        self._setup_ui()
        self._setup_telemetry()
        
        # Inicializar dados para todos os servidores
        self._initialize_telemetry_data()
    
    def _setup_ui(self):
        """Configura a interface do painel"""
        # Frame para seleção de servidor
        select_frame = ttk.Frame(self.parent_frame)
        select_frame.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Label(select_frame, text="Servidor:").pack(side=tk.LEFT)
        self.server_var = tk.StringVar()
        self.server_combo = ttk.Combobox(select_frame, textvariable=self.server_var, 
                                        state="readonly", width=30)
        self.server_combo.pack(side=tk.LEFT, padx=(5, 0))
        self.server_combo.bind('<<ComboboxSelected>>', self._on_server_change)
        
        # Frame para gráficos
        self.canvas_frame = ttk.Frame(self.parent_frame)
        self.canvas_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
    
    def _setup_telemetry(self):
        """Configura os gráficos de telemetria"""
        # Criar figura matplotlib
        self.fig = Figure(figsize=(12, 8), dpi=100, facecolor='#2b2b2b')
        self.fig.suptitle('Telemetria do Servidor', fontsize=14, fontweight='bold', color='white')
        
        # Subplots
        self.ax1 = self.fig.add_subplot(2, 2, 1, facecolor='#3c3c3c')
        self.ax2 = self.fig.add_subplot(2, 2, 2, facecolor='#3c3c3c')
        self.ax3 = self.fig.add_subplot(2, 2, 3, facecolor='#3c3c3c')
        self.ax4 = self.fig.add_subplot(2, 2, 4, facecolor='#3c3c3c')
        
        # Configurar eixos com tema escuro
        axes = [self.ax1, self.ax2, self.ax3, self.ax4]
        titles = ['Status de Conectividade', 'Tempo de Resposta HTTP (ms)', 
                 'Disponibilidade das Portas', 'Histórico de Status']
        ylabels = ['Status', 'Tempo (ms)', 'Status', 'Uptime %']
        
        for ax, title, ylabel in zip(axes, titles, ylabels):
            ax.set_title(title, color='white', fontsize=10)
            ax.set_ylabel(ylabel, color='white')
            ax.tick_params(colors='white')
            ax.spines['bottom'].set_color('white')
            ax.spines['top'].set_color('white')
            ax.spines['right'].set_color('white')
            ax.spines['left'].set_color('white')
        
        # Ajustar layout
        self.fig.tight_layout()
        
        # Canvas para matplotlib
        self.canvas = FigureCanvasTkAgg(self.fig, self.canvas_frame)
        self.canvas.draw()
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
    
    def _initialize_telemetry_data(self):
        """Inicializa estruturas de dados de telemetria"""
        for server in self.servers:
            server_name = server['name']
            self.telemetry_data[server_name] = {
                'timestamps': deque(maxlen=self.max_data_points),
                'ping_status': deque(maxlen=self.max_data_points),
                'http_response_time': deque(maxlen=self.max_data_points),
                'port_status': deque(maxlen=self.max_data_points),
                'uptime_percentage': deque(maxlen=self.max_data_points),
                'total_checks': 0,
                'successful_checks': 0
            }
    
    def update_servers(self, servers):
        """Atualiza a lista de servidores"""
        self.servers = servers
        
        # Atualizar combo
        server_names = [server['name'] for server in servers]
        self.server_combo['values'] = server_names
        
        if server_names and not self.server_var.get():
            self.server_var.set(server_names[0])
            self.selected_server = server_names[0]
        
        # Inicializar dados para novos servidores
        self._initialize_telemetry_data()
    
    def _on_server_change(self, event=None):
        """Manipula mudança de servidor selecionado"""
        self.selected_server = self.server_var.get()
        self._update_charts()
    
    def add_telemetry_data(self, server_name, status_data):
        """Adiciona dados de telemetria para um servidor"""
        if server_name not in self.telemetry_data:
            return
        
        data = self.telemetry_data[server_name]
        now = datetime.now()
        
        # Adicionar timestamp
        data['timestamps'].append(now)
        
        # Status de ping (1 para sucesso, 0 para falha)
        ping_status = 1 if status_data.get('ping', False) else 0
        data['ping_status'].append(ping_status)
        
        # Tempo de resposta HTTP
        http_time = status_data.get('http_response_time', 0)
        data['http_response_time'].append(http_time)
        
        # Status da porta (1 para aberta, 0 para fechada)
        port_status = 1 if status_data.get('port', False) else 0
        data['port_status'].append(port_status)
        
        # Calcular uptime
        data['total_checks'] += 1
        if ping_status:
            data['successful_checks'] += 1
        
        uptime = (data['successful_checks'] / data['total_checks']) * 100 if data['total_checks'] > 0 else 0
        data['uptime_percentage'].append(uptime)
    
    def update_display(self):
        """Atualiza a exibição dos gráficos"""
        if self.selected_server and self.selected_server in self.telemetry_data:
            self._update_charts()
    
    def _update_charts(self):
        """Atualiza os gráficos com dados do servidor selecionado"""
        if not self.selected_server or self.selected_server not in self.telemetry_data:
            return
        
        data = self.telemetry_data[self.selected_server]
        
        if not data['timestamps']:
            return
        
        # Limpar gráficos
        self.ax1.clear()
        self.ax2.clear()
        self.ax3.clear()
        self.ax4.clear()
        
        # Configurar tema escuro novamente
        axes = [self.ax1, self.ax2, self.ax3, self.ax4]
        titles = ['Status de Conectividade', 'Tempo de Resposta HTTP (ms)', 
                 'Disponibilidade das Portas', 'Histórico de Status']
        ylabels = ['Status', 'Tempo (ms)', 'Status', 'Uptime %']
        
        for ax, title, ylabel in zip(axes, titles, ylabels):
            ax.set_title(title, color='white', fontsize=10)
            ax.set_ylabel(ylabel, color='white')
            ax.tick_params(colors='white')
            ax.set_facecolor('#3c3c3c')
            for spine in ax.spines.values():
                spine.set_color('white')
        
        # Converter timestamps para formato adequado
        timestamps = list(data['timestamps'])
        
        # Gráfico 1: Status de Conectividade
        if data['ping_status']:
            ping_data = list(data['ping_status'])
            self.ax1.plot(timestamps, ping_data, 'g-', linewidth=2, label='Ping')
            self.ax1.fill_between(timestamps, ping_data, alpha=0.3, color='green')
            self.ax1.set_ylim(-0.1, 1.1)
            self.ax1.set_yticks([0, 1])
            self.ax1.set_yticklabels(['Offline', 'Online'])
        
        # Gráfico 2: Tempo de Resposta HTTP
        if data['http_response_time']:
            http_data = list(data['http_response_time'])
            self.ax2.plot(timestamps, http_data, 'b-', linewidth=2, label='HTTP')
            self.ax2.fill_between(timestamps, http_data, alpha=0.3, color='blue')
        
        # Gráfico 3: Disponibilidade das Portas
        if data['port_status']:
            port_data = list(data['port_status'])
            self.ax3.plot(timestamps, port_data, 'orange', linewidth=2, label='Porta')
            self.ax3.fill_between(timestamps, port_data, alpha=0.3, color='orange')
            self.ax3.set_ylim(-0.1, 1.1)
            self.ax3.set_yticks([0, 1])
            self.ax3.set_yticklabels(['Fechada', 'Aberta'])
        
        # Gráfico 4: Histórico de Uptime
        if data['uptime_percentage']:
            uptime_data = list(data['uptime_percentage'])
            self.ax4.plot(timestamps, uptime_data, 'r-', linewidth=2, label='Uptime')
            self.ax4.fill_between(timestamps, uptime_data, alpha=0.3, color='red')
            self.ax4.set_ylim(0, 100)
            self.ax4.set_ylabel('Uptime %', color='white')
        
        # Formatar eixo X para todos os gráficos
        for ax in axes:
            ax.tick_params(axis='x', rotation=45)
            if timestamps:
                # Mostrar apenas alguns labels no eixo X para evitar sobreposição
                if len(timestamps) > 10:
                    step = len(timestamps) // 5
                    ax.set_xticks(timestamps[::step])
        
        # Ajustar layout e redesenhar
        self.fig.tight_layout()
        self.canvas.draw()
    
    def clear_data(self, server_name=None):
        """Limpa dados de telemetria"""
        if server_name:
            if server_name in self.telemetry_data:
                data = self.telemetry_data[server_name]
                data['timestamps'].clear()
                data['ping_status'].clear()
                data['http_response_time'].clear()
                data['port_status'].clear()
                data['uptime_percentage'].clear()
                data['total_checks'] = 0
                data['successful_checks'] = 0
        else:
            # Limpar todos os dados
            for server_name in self.telemetry_data:
                self.clear_data(server_name)
        
        # Atualizar gráficos
        if self.selected_server:
            self._update_charts()
    
    def get_server_stats(self, server_name):
        """Retorna estatísticas do servidor"""
        if server_name not in self.telemetry_data:
            return None
        
        data = self.telemetry_data[server_name]
        
        if data['total_checks'] == 0:
            return {
                'uptime_percentage': 0,
                'total_checks': 0,
                'successful_checks': 0,
                'avg_response_time': 0,
                'last_check': None
            }
        
        # Calcular tempo médio de resposta
        response_times = [t for t in data['http_response_time'] if t > 0]
        avg_response_time = sum(response_times) / len(response_times) if response_times else 0
        
        return {
            'uptime_percentage': (data['successful_checks'] / data['total_checks']) * 100,
            'total_checks': data['total_checks'],
            'successful_checks': data['successful_checks'],
            'avg_response_time': avg_response_time,
            'last_check': data['timestamps'][-1] if data['timestamps'] else None
        }