#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Monitorador de Servidores GlassFish
Sistema completo de monitoramento com interface gráfica
"""

import os
import sys
import time
import socket
import platform
import subprocess
import threading
import logging
import csv
import smtplib
from datetime import datetime
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
import requests
from requests.exceptions import RequestException, Timeout, ConnectionError

# Configurações globais
CONFIG = {
    'ping_timeout': 3,
    'http_timeout': 10,
    'monitor_interval': 30,
    'log_file': 'monitor.log',
    'csv_file': 'monitor_history.csv',
    'email_alerts': False,
    'sound_alerts': True,
    'smtp_server': 'smtp.gmail.com',
    'smtp_port': 587,
    'email_user': '',
    'email_password': '',
    'alert_recipients': []
}

# Lista de servidores para monitorar
SERVERS = [
    {
        'name': 'Servidor Local',
        'host': 'localhost',
        'app_port': 8080,
        'admin_port': 4848,
        'health_url': 'http://localhost:8080/health'
    },
    {
        'name': 'Servidor Produção',
        'host': '192.168.1.100',
        'app_port': 8080,
        'admin_port': 4848,
        'health_url': 'http://192.168.1.100:8080/health'
    }
]

class ServerMonitor:
    def __init__(self):
        self.setup_logging()
        self.monitoring = False
        self.monitor_thread = None
        self.server_status = {}
        self.servers = SERVERS.copy()  # Lista de servidores para monitorar
        
    def setup_logging(self):
        """Configura o sistema de logs"""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(CONFIG['log_file'], encoding='utf-8'),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)
        
        # Criar arquivo CSV se não existir
        if not os.path.exists(CONFIG['csv_file']):
            with open(CONFIG['csv_file'], 'w', newline='', encoding='utf-8') as csvfile:
                writer = csv.writer(csvfile)
                writer.writerow(['Timestamp', 'Server', 'Host', 'Ping', 'App_Port', 'Admin_Port', 'HTTP', 'Status'])
    
    def check_ping(self, host):
        """Verifica se o host responde ao ping e retorna tempo de resposta"""
        try:
            if platform.system().lower() == 'windows':
                cmd = ['ping', '-n', '1', '-w', str(CONFIG['ping_timeout'] * 1000), host]
            else:
                cmd = ['ping', '-c', '1', '-W', str(CONFIG['ping_timeout']), host]
            
            start_time = time.time()
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=CONFIG['ping_timeout'] + 2)
            response_time = (time.time() - start_time) * 1000  # em ms
            
            if result.returncode == 0:
                # Tentar extrair tempo real do ping do output
                output = result.stdout.lower()
                if 'time=' in output:
                    try:
                        time_part = output.split('time=')[1].split('ms')[0]
                        response_time = float(time_part)
                    except:
                        pass  # usar o tempo calculado
                
                return {
                    'success': True,
                    'response_time': round(response_time, 1)
                }
            else:
                return {
                    'success': False,
                    'response_time': 0,
                    'error': 'No response'
                }
        except (subprocess.TimeoutExpired, Exception) as e:
            self.logger.error(f"Erro no ping para {host}: {e}")
            return {
                'success': False,
                'response_time': 0,
                'error': str(e)
            }
    
    def check_port(self, host, port):
        """Verifica se uma porta específica está aberta e retorna detalhes"""
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(5)
            start_time = time.time()
            result = sock.connect_ex((host, port))
            response_time = (time.time() - start_time) * 1000  # em ms
            sock.close()
            
            if result == 0:
                return {
                    'success': True,
                    'port': port,
                    'response_time': round(response_time, 1),
                    'status': 'OPEN'
                }
            else:
                return {
                    'success': False,
                    'port': port,
                    'response_time': 0,
                    'status': 'CLOSED',
                    'error': f'Connection failed (code: {result})'
                }
        except Exception as e:
            self.logger.error(f"Erro ao verificar porta {port} em {host}: {e}")
            return {
                'success': False,
                'port': port,
                'response_time': 0,
                'status': 'ERROR',
                'error': str(e)
            }
    
    def check_http(self, url):
        """Verifica resposta HTTP de uma URL"""
        try:
            response = requests.get(url, timeout=CONFIG['http_timeout'])
            return {
                'status_code': response.status_code,
                'success': 200 <= response.status_code < 400,
                'response_time': response.elapsed.total_seconds()
            }
        except Timeout:
            return {'status_code': 0, 'success': False, 'response_time': CONFIG['http_timeout'], 'error': 'Timeout'}
        except ConnectionError:
            return {'status_code': 0, 'success': False, 'response_time': 0, 'error': 'Connection Error'}
        except RequestException as e:
            return {'status_code': 0, 'success': False, 'response_time': 0, 'error': str(e)}
    
    def log_status(self, message):
        """Registra status nos logs"""
        self.logger.info(message)
    
    def play_alert_sound(self):
        """Reproduz som de alerta no Windows"""
        if CONFIG['sound_alerts'] and platform.system().lower() == 'windows':
            try:
                import winsound
                winsound.Beep(1000, 500)  # Frequência 1000Hz por 500ms
            except ImportError:
                # Fallback para sistemas sem winsound
                print('\a')  # Bell character
    
    def send_email_alert(self, subject, message):
        """Envia alerta por email"""
        if not CONFIG['email_alerts'] or not CONFIG['email_user']:
            return
        
        try:
            msg = MIMEMultipart()
            msg['From'] = CONFIG['email_user']
            msg['To'] = ', '.join(CONFIG['alert_recipients'])
            msg['Subject'] = subject
            
            msg.attach(MIMEText(message, 'plain', 'utf-8'))
            
            server = smtplib.SMTP(CONFIG['smtp_server'], CONFIG['smtp_port'])
            server.starttls()
            server.login(CONFIG['email_user'], CONFIG['email_password'])
            
            for recipient in CONFIG['alert_recipients']:
                server.sendmail(CONFIG['email_user'], recipient, msg.as_string())
            
            server.quit()
            self.logger.info(f"Email de alerta enviado: {subject}")
        except Exception as e:
            self.logger.error(f"Erro ao enviar email: {e}")
    
    def monitor_server(self, server):
        """Monitora um servidor específico"""
        timestamp = datetime.now()
        name = server['name']
        host = server['host']
        
        # Verificações
        ping_result = self.check_ping(host)
        app_port_result = self.check_port(host, server['app_port']) if ping_result['success'] else {'success': False, 'port': server['app_port'], 'status': 'SKIPPED'}
        admin_port_result = self.check_port(host, server['admin_port']) if ping_result['success'] else {'success': False, 'port': server['admin_port'], 'status': 'SKIPPED'}
        
        http_result = None
        if ping_result['success'] and app_port_result['success'] and 'health_url' in server:
            http_result = self.check_http(server['health_url'])
        
        # Determinar status geral
        if not ping_result['success']:
            status = 'OFFLINE'
            status_icon = '❌'
        elif not app_port_result['success'] and not admin_port_result['success']:
            status = 'PORTS_CLOSED'
            status_icon = '⚠️'
        elif http_result and not http_result['success']:
            status = 'HTTP_ERROR'
            status_icon = '⚠️'
        else:
            status = 'ONLINE'
            status_icon = '✅'
        
        # Criar resultado
        result = {
            'timestamp': timestamp,
            'name': name,
            'host': host,
            'ping': ping_result,
            'app_port': app_port_result,
            'admin_port': admin_port_result,
            'http': http_result,
            'status': status,
            'status_icon': status_icon
        }
        
        # Log no console
        ping_info = f"{ping_result['response_time']}ms" if ping_result['success'] else ping_result.get('error', 'Failed')
        app_info = f"{app_port_result['response_time']}ms" if app_port_result['success'] else app_port_result.get('status', 'Failed')
        admin_info = f"{admin_port_result['response_time']}ms" if admin_port_result['success'] else admin_port_result.get('status', 'Failed')
        
        http_info = ''
        if http_result:
            if http_result['success']:
                http_info = f" | HTTP: {http_result['status_code']} ({http_result['response_time']:.2f}s)"
            else:
                error_msg = http_result.get('error', f"Status {http_result['status_code']}")
                http_info = f" | HTTP: {error_msg}"
        
        log_message = f"{status_icon} {name} ({host}) - Ping: {ping_info} | App: {app_info} | Admin: {admin_info}{http_info}"
        self.log_status(log_message)
        
        # Salvar no CSV
        self.save_to_csv(result)
        
        # Verificar se precisa de alerta
        previous_status = self.server_status.get(name, {}).get('status')
        if previous_status == 'ONLINE' and status != 'ONLINE':
            # Servidor ficou indisponível
            self.play_alert_sound()
            alert_message = f"ALERTA: Servidor {name} ({host}) ficou indisponível!\nStatus: {status}"
            self.send_email_alert(f"Servidor {name} Indisponível", alert_message)
        
        self.server_status[name] = result
        return result
    
    def save_to_csv(self, result):
        """Salva resultado no arquivo CSV"""
        try:
            with open(CONFIG['csv_file'], 'a', newline='', encoding='utf-8') as csvfile:
                writer = csv.writer(csvfile)
                http_status = ''
                if result['http']:
                    if result['http']['success']:
                        http_status = f"{result['http']['status_code']} ({result['http']['response_time']:.2f}s)"
                    else:
                        http_status = result['http'].get('error', f"Error {result['http']['status_code']}")
                
                writer.writerow([
                    result['timestamp'].strftime('%Y-%m-%d %H:%M:%S'),
                    result['name'],
                    result['host'],
                    result['ping'],
                    result['app_port'],
                    result['admin_port'],
                    http_status,
                    result['status']
                ])
        except Exception as e:
            self.logger.error(f"Erro ao salvar CSV: {e}")
    
    def monitor_loop(self):
        """Loop principal de monitoramento"""
        self.log_status("=== Iniciando monitoramento de servidores GlassFish ===")
        
        while self.monitoring:
            try:
                for server in self.servers:
                    if not self.monitoring:
                        break
                    self.monitor_server(server)
                
                if self.monitoring:
                    time.sleep(CONFIG['monitor_interval'])
                    
            except KeyboardInterrupt:
                self.log_status("Monitoramento interrompido pelo usuário")
                break
            except Exception as e:
                self.logger.error(f"Erro no loop de monitoramento: {e}")
                time.sleep(5)
        
        self.log_status("=== Monitoramento finalizado ===")
    
    def start_monitoring(self):
        """Inicia o monitoramento em thread separada"""
        if not self.monitoring:
            self.monitoring = True
            self.monitor_thread = threading.Thread(target=self.monitor_loop, daemon=True)
            self.monitor_thread.start()
    
    def stop_monitoring(self):
        """Para o monitoramento"""
        self.monitoring = False
        if self.monitor_thread and self.monitor_thread.is_alive():
            self.monitor_thread.join(timeout=5)

if __name__ == '__main__':
    # Executar apenas o monitorador em modo console
    monitor = ServerMonitor()
    try:
        monitor.start_monitoring()
        print("Monitoramento iniciado. Pressione Ctrl+C para parar.")
        while monitor.monitoring:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\nParando monitoramento...")
        monitor.stop_monitoring()
        print("Monitoramento finalizado.")