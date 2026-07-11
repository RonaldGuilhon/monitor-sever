"""Alert system implementations"""

import platform
import smtplib
import winsound
from datetime import datetime, timedelta
from typing import List, Optional, Protocol
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

from ..domain import AlertConfig, Server, ServerState


class AlertHandler(Protocol):
    """Protocol for alert handlers"""
    def send(self, subject: str, message: str, severity: str) -> bool: ...


class SoundAlertHandler:
    """Handles sound alerts"""
    
    def __init__(self, enabled: bool = True):
        self._enabled = enabled
    
    def send(self, subject: str, message: str, severity: str = "INFO") -> bool:
        if not self._enabled:
            return False
        
        try:
            if platform.system().lower() == 'windows':
                winsound.Beep(1000, 500)
            else:
                print('\a')
            return True
        except Exception:
            return False


class EmailAlertHandler:
    """Handles email alerts"""
    
    def __init__(self, config: AlertConfig):
        self._config = config
        self._last_alert_time: dict[str, datetime] = {}
    
    def send(self, subject: str, message: str, severity: str = "INFO") -> bool:
        if not self._config.email_enabled:
            return False
        
        if not self._config.username or not self._config.to_emails:
            return False
        
        # Check cooldown
        now = datetime.now()
        if subject in self._last_alert_time:
            elapsed = now - self._last_alert_time[subject]
            if elapsed < timedelta(seconds=self._config.email_cooldown_seconds):
                return False
        
        try:
            msg = MIMEMultipart()
            msg['From'] = self._config.from_email or self._config.username
            msg['To'] = ', '.join(self._config.to_emails)
            msg['Subject'] = f"[{severity}] {subject}"
            
            timestamped_message = f"Alert Time: {now.strftime('%Y-%m-%d %H:%M:%S')}\n\n{message}"
            msg.attach(MIMEText(timestamped_message, 'plain', 'utf-8'))
            
            with smtplib.SMTP(self._config.smtp_server, self._config.smtp_port) as server:
                if self._config.use_tls:
                    server.starttls()
                server.login(self._config.username, self._config.password)
                server.sendmail(
                    msg['From'], 
                    self._config.to_emails, 
                    msg.as_string()
                )
            
            self._last_alert_time[subject] = now
            return True
            
        except Exception as e:
            print(f"Error sending email: {e}")
            return False


class AlertManager:
    """Manages multiple alert handlers"""
    
    def __init__(self, config: AlertConfig):
        self._config = config
        self._handlers: List[AlertHandler] = []
        
        # Add handlers based on config
        self._handlers.append(SoundAlertHandler(enabled=config.sound_enabled))
        if config.email_enabled:
            self._handlers.append(EmailAlertHandler(config))
    
    def send_alert(self, subject: str, message: str, severity: str = "INFO") -> bool:
        """Send alert through all handlers"""
        results = []
        for handler in self._handlers:
            try:
                results.append(handler.send(subject, message, severity))
            except Exception as e:
                print(f"Alert handler error: {e}")
                results.append(False)
        
        return any(results)
    
    def notify_server_down(self, server: Server, state: ServerState) -> bool:
        """Notify when server goes down"""
        subject = f"Server Alert: {server.name} is {state.value}"
        message = f"""
Server: {server.name}
Host: {server.host}
Status: {state.value}
Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

Please check the server immediately.
"""
        return self.send_alert(subject, message, severity=state.value)
    
    def notify_server_recovery(self, server: Server, previous_state: ServerState) -> bool:
        """Notify when server recovers"""
        subject = f"Server Recovery: {server.name} is back online"
        message = f"""
Server: {server.name}
Host: {server.host}
Previous Status: {previous_state.value}
Current Status: ONLINE
Recovery Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

Server has recovered and is functioning normally.
"""
        return self.send_alert(subject, message, severity="INFO")
