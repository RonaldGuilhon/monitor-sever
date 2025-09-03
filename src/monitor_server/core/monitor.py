"""Core server monitoring functionality"""

import os
import time
import socket
import platform
import subprocess
import threading
import logging
import csv
import smtplib
import json
from datetime import datetime
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

import requests
from requests.exceptions import RequestException, Timeout, ConnectionError

from ..config import CONFIG, SERVERS, LOGS_FILE
from ..utils import (
    extract_port_from_url, extract_hostname_from_url,
    setup_logging, get_logger, log_server_event as log_util,
    save_json_file, load_json_file, append_to_csv
)

class ServerMonitor:
    """Main server monitoring class"""
    
    def __init__(self):
        """Initialize the server monitor"""
        self.setup_logging()
        self.monitoring = False
        self.monitor_thread = None
        self.server_status = {}
        self.server_logs = {}  # Individual logs per server
        self.servers = SERVERS  # Use servers from global configuration
        
        # Initialize logs for each server
        for server in self.servers:
            self.server_logs[server['name']] = []
        
        # Load saved logs
        self.load_server_logs()
    
    def setup_logging(self):
        """Configure logging system"""
        self.logger = setup_logging(CONFIG['log_file'])
        
        # Create CSV file if it doesn't exist
        if not os.path.exists(CONFIG['csv_file']):
            with open(CONFIG['csv_file'], 'w', newline='', encoding='utf-8') as csvfile:
                writer = csv.writer(csvfile)
                writer.writerow(['Timestamp', 'Server', 'Host', 'Ping', 'App_Port', 'Admin_Port', 'HTTP', 'Status'])
    
    def check_ping(self, host):
        """Check if host responds to ping and return response time"""
        try:
            if platform.system().lower() == 'windows':
                cmd = ['ping', '-n', '1', '-w', str(CONFIG['ping_timeout'] * 1000), host]
            else:
                cmd = ['ping', '-c', '1', '-W', str(CONFIG['ping_timeout']), host]
            
            start_time = time.time()
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=CONFIG['ping_timeout'] + 2)
            response_time = (time.time() - start_time) * 1000  # in ms
            
            if result.returncode == 0:
                # Try to extract real ping time from output
                output = result.stdout.lower()
                if 'time=' in output:
                    try:
                        time_part = output.split('time=')[1].split('ms')[0]
                        response_time = float(time_part)
                    except:
                        pass  # use calculated time
                
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
            self.logger.error(f"Ping error for {host}: {e}")
            return {
                'success': False,
                'response_time': 0,
                'error': str(e)
            }
    
    def check_port(self, host, port):
        """Check if a specific port is open and return details"""
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(5)
            start_time = time.time()
            result = sock.connect_ex((host, port))
            response_time = (time.time() - start_time) * 1000  # in ms
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
            self.logger.error(f"Error checking port {port} on {host}: {e}")
            return {
                'success': False,
                'port': port,
                'response_time': 0,
                'status': 'ERROR',
                'error': str(e)
            }
    
    def check_http(self, url):
        """Check HTTP response from a URL"""
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
        """Log status to logs"""
        self.logger.info(message)
    
    def log_server_event(self, server_name, event_type, message, is_error=False):
        """Log server-specific event"""
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        log_entry = {
            'timestamp': timestamp,
            'event_type': event_type,
            'message': message,
            'is_error': is_error
        }
        
        # Add to server-specific log
        if server_name not in self.server_logs:
            self.server_logs[server_name] = []
        
        self.server_logs[server_name].append(log_entry)
        
        # Keep only last 1000 logs per server
        if len(self.server_logs[server_name]) > 1000:
            self.server_logs[server_name] = self.server_logs[server_name][-1000:]
        
        # General log as well
        log_level = 'ERROR' if is_error else 'INFO'
        full_message = f"[{server_name}] {event_type}: {message}"
        if is_error:
            self.logger.error(full_message)
        else:
            self.logger.info(full_message)
        
        # Auto-save logs (only for error events to avoid overhead)
        if is_error:
            self.save_server_logs()
    
    def get_server_logs(self, server_name, error_only=False):
        """Return logs for a specific server"""
        if server_name not in self.server_logs:
            return []
        
        logs = self.server_logs[server_name]
        if error_only:
            return [log for log in logs if log['is_error']]
        return logs
    
    def save_server_logs(self):
        """Save server logs to JSON file"""
        try:
            save_json_file(LOGS_FILE, self.server_logs)
        except Exception as e:
            self.logger.error(f"Error saving logs: {e}")
    
    def load_server_logs(self):
        """Load server logs from JSON file"""
        try:
            saved_logs = load_json_file(LOGS_FILE, {})
            
            # Merge saved logs with current logs
            for server_name, logs in saved_logs.items():
                if server_name in self.server_logs:
                    self.server_logs[server_name] = logs
                else:
                    self.server_logs[server_name] = logs
            
            self.logger.info(f"Logs loaded from {LOGS_FILE}")
        except Exception as e:
            self.logger.error(f"Error loading logs: {e}")
    
    def play_alert_sound(self):
        """Play alert sound on Windows"""
        if CONFIG['sound_alerts'] and platform.system().lower() == 'windows':
            try:
                import winsound
                winsound.Beep(1000, 500)  # 1000Hz frequency for 500ms
            except ImportError:
                # Fallback for systems without winsound
                print('\a')  # Bell character
    
    def send_email_alert(self, subject, message):
        """Send email alert"""
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
            self.logger.info(f"Alert email sent: {subject}")
        except Exception as e:
            self.logger.error(f"Error sending email: {e}")
    
    def monitor_server(self, server):
        """Monitor a specific server"""
        timestamp = datetime.now()
        name = server['name']
        host = server['host']
        
        # Checks
        ping_result = self.check_ping(host)
        app_port_result = self.check_port(host, server['app_port']) if ping_result['success'] else {'success': False, 'port': server['app_port'], 'status': 'IGNORED'}
        admin_port_result = self.check_port(host, server.get('admin_port', 4848)) if ping_result['success'] else {'success': False, 'port': server.get('admin_port', 4848), 'status': 'IGNORED'}
        
        http_result = None
        if ping_result['success'] and app_port_result['success'] and 'health_url' in server:
            http_result = self.check_http(server['health_url'])
        
        # Determine general status
        if not ping_result['success']:
            status = 'OFFLINE'
            status_icon = '❌'
        elif not app_port_result['success']:
            status = 'PORT_CLOSED'
            status_icon = '⚠️'
        elif http_result and not http_result['success']:
            status = 'HTTP_ERROR'
            status_icon = '⚠️'
        else:
            status = 'ONLINE'
            status_icon = '✅'
        
        # Create result
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
        
        # Console log
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
        
        # Log server-specific events
        self.log_server_event(name, 'STATUS_CHECK', log_message, is_error=(status != 'ONLINE'))
        
        # Log specific errors
        if not ping_result['success']:
            self.log_server_event(name, 'PING_ERROR', f"Ping failed: {ping_result.get('error', 'Timeout')}", is_error=True)
        
        if not app_port_result['success']:
            self.log_server_event(name, 'APP_PORT_ERROR', f"Port {server['app_port']} inaccessible: {app_port_result.get('status', 'Failed')}", is_error=True)
        
        if not admin_port_result['success']:
            admin_port = server.get('admin_port', 4848)
            self.log_server_event(name, 'ADMIN_PORT_ERROR', f"Port {admin_port} inaccessible: {admin_port_result.get('status', 'Failed')}", is_error=True)
        
        if http_result and not http_result['success']:
            error_msg = http_result.get('error', f"Status {http_result['status_code']}")
            self.log_server_event(name, 'HTTP_ERROR', f"HTTP check failed: {error_msg}", is_error=True)
        
        # Save to CSV
        self.save_to_csv(result)
        
        # Check if alert is needed
        previous_status = self.server_status.get(name, {}).get('status')
        if previous_status and previous_status not in ['OFFLINE', 'PORT_CLOSED', 'HTTP_ERROR'] and status in ['OFFLINE', 'PORT_CLOSED', 'HTTP_ERROR']:
            # Server became unavailable
            self.play_alert_sound()
            alert_message = f"ALERT: Server {name} ({host}) became unavailable!\nStatus: {status}"
            self.log_server_event(name, 'ALERT', f"Server became unavailable - Status: {status}", is_error=True)
            self.send_email_alert(f"Server {name} Unavailable", alert_message)
        elif previous_status in ['OFFLINE', 'PORT_CLOSED', 'HTTP_ERROR'] and status == 'ONLINE':
            # Server recovered
            recovery_message = f"RECOVERY: Server {name} ({host}) is back online!\nStatus: {status}"
            self.log_server_event(name, 'RECOVERY', f"Server recovered - Status: {status}", is_error=False)
            self.send_email_alert(f"Server {name} Recovered", recovery_message)
        
        self.server_status[name] = result
        return result
    
    def save_to_csv(self, result):
        """Save result to CSV file"""
        try:
            http_status = ''
            if result['http']:
                if result['http']['success']:
                    http_status = f"{result['http']['status_code']} ({result['http']['response_time']:.2f}s)"
                else:
                    http_status = result['http'].get('error', f"Error {result['http']['status_code']}")
            
            csv_data = {
                'Timestamp': result['timestamp'].strftime('%Y-%m-%d %H:%M:%S'),
                'Server': result['name'],
                'Host': result['host'],
                'Ping': result['ping'],
                'App_Port': result['app_port'],
                'Admin_Port': result['admin_port'],
                'HTTP': http_status,
                'Status': result['status']
            }
            
            append_to_csv(CONFIG['csv_file'], csv_data)
        except Exception as e:
            self.logger.error(f"Error saving CSV: {e}")
    
    def monitor_loop(self):
        """Main monitoring loop"""
        self.log_status("=== Starting GlassFish server monitoring ===")
        cycle_count = 0
        
        while self.monitoring:
            try:
                for server in self.servers:
                    if not self.monitoring:
                        break
                    self.monitor_server(server)
                
                cycle_count += 1
                
                if self.monitoring:
                    time.sleep(CONFIG['monitor_interval'])
                    
            except KeyboardInterrupt:
                self.log_status("Monitoring interrupted by user")
                break
            except Exception as e:
                self.logger.error(f"Error in monitoring loop: {e}")
                time.sleep(5)
        
        self.log_status("=== Monitoring finished ===")
    
    def start_monitoring(self):
        """Start monitoring in separate thread"""
        if not self.monitoring:
            self.monitoring = True
            self.monitor_thread = threading.Thread(target=self.monitor_loop, daemon=True)
            self.monitor_thread.start()
    
    def stop_monitoring(self):
        """Stop monitoring"""
        self.monitoring = False
        if self.monitor_thread and self.monitor_thread.is_alive():
            self.monitor_thread.join(timeout=5)
        
        # Save logs before stopping
        self.save_server_logs()
        self.log_status("Monitoring stopped")