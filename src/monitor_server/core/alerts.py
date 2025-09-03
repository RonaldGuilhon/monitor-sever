"""Alert system for server monitoring"""

import platform
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime

from ..config import CONFIG
from ..utils import get_logger

logger = get_logger(__name__)

class AlertManager:
    """Manages alerts for server monitoring"""
    
    def __init__(self):
        self.alert_history = []
        self.max_history = 1000
    
    def play_sound_alert(self):
        """Play alert sound on Windows"""
        if not CONFIG['sound_alerts']:
            return
            
        if platform.system().lower() == 'windows':
            try:
                import winsound
                winsound.Beep(1000, 500)  # 1000Hz frequency for 500ms
                logger.info("Sound alert played")
            except ImportError:
                # Fallback for systems without winsound
                print('\a')  # Bell character
                logger.warning("winsound not available, using bell character")
        else:
            # Unix/Linux systems
            print('\a')  # Bell character
            logger.info("Bell alert played")
    
    def send_email_alert(self, subject, message, recipients=None):
        """Send email alert"""
        if not CONFIG['email_alerts'] or not CONFIG['email_user']:
            logger.debug("Email alerts disabled or no email user configured")
            return False
        
        if recipients is None:
            recipients = CONFIG['alert_recipients']
        
        if not recipients:
            logger.warning("No email recipients configured")
            return False
        
        try:
            msg = MIMEMultipart()
            msg['From'] = CONFIG['email_user']
            msg['To'] = ', '.join(recipients)
            msg['Subject'] = subject
            
            # Add timestamp to message
            timestamped_message = f"Alert Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n{message}"
            msg.attach(MIMEText(timestamped_message, 'plain', 'utf-8'))
            
            server = smtplib.SMTP(CONFIG['smtp_server'], CONFIG['smtp_port'])
            server.starttls()
            server.login(CONFIG['email_user'], CONFIG['email_password'])
            
            for recipient in recipients:
                server.sendmail(CONFIG['email_user'], recipient, msg.as_string())
            
            server.quit()
            logger.info(f"Alert email sent: {subject} to {len(recipients)} recipients")
            
            # Record alert in history
            self._record_alert('EMAIL', subject, message, recipients)
            return True
            
        except Exception as e:
            logger.error(f"Error sending email alert: {e}")
            return False
    
    def send_server_down_alert(self, server_name, host, status, details=None):
        """Send alert when server goes down"""
        subject = f"🚨 Server Alert: {server_name} is {status}"
        
        message_parts = [
            f"Server: {server_name}",
            f"Host: {host}",
            f"Status: {status}",
            f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
        ]
        
        if details:
            message_parts.append("\nDetails:")
            for key, value in details.items():
                message_parts.append(f"  {key}: {value}")
        
        message_parts.append("\nPlease check the server immediately.")
        message = "\n".join(message_parts)
        
        # Send both sound and email alerts
        self.play_sound_alert()
        self.send_email_alert(subject, message)
        
        logger.error(f"Server down alert sent for {server_name}: {status}")
    
    def send_server_recovery_alert(self, server_name, host, previous_status):
        """Send alert when server recovers"""
        subject = f"✅ Server Recovery: {server_name} is back online"
        
        message = "\n".join([
            f"Server: {server_name}",
            f"Host: {host}",
            f"Previous Status: {previous_status}",
            f"Current Status: ONLINE",
            f"Recovery Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            "\nServer has recovered and is functioning normally."
        ])
        
        self.send_email_alert(subject, message)
        logger.info(f"Server recovery alert sent for {server_name}")
    
    def send_port_alert(self, server_name, host, port, port_type, is_recovery=False):
        """Send alert for port-specific issues"""
        if is_recovery:
            subject = f"✅ Port Recovery: {server_name} - {port_type} port {port}"
            message = f"Port {port} ({port_type}) on {server_name} ({host}) is now accessible."
        else:
            subject = f"⚠️ Port Alert: {server_name} - {port_type} port {port} inaccessible"
            message = f"Port {port} ({port_type}) on {server_name} ({host}) is not responding."
        
        message += f"\nTime: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
        
        if not is_recovery:
            self.play_sound_alert()
        
        self.send_email_alert(subject, message)
        
        alert_type = "recovery" if is_recovery else "down"
        logger.info(f"Port {alert_type} alert sent for {server_name} port {port}")
    
    def send_http_alert(self, server_name, url, status_code, error, is_recovery=False):
        """Send alert for HTTP-specific issues"""
        if is_recovery:
            subject = f"✅ HTTP Recovery: {server_name} - Health check restored"
            message = f"HTTP health check for {server_name} is now responding normally.\nURL: {url}"
        else:
            subject = f"🌐 HTTP Alert: {server_name} - Health check failed"
            message_parts = [
                f"HTTP health check failed for {server_name}",
                f"URL: {url}",
                f"Status Code: {status_code}",
                f"Error: {error}"
            ]
            message = "\n".join(message_parts)
        
        message += f"\nTime: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
        
        if not is_recovery:
            self.play_sound_alert()
        
        self.send_email_alert(subject, message)
        
        alert_type = "recovery" if is_recovery else "failure"
        logger.info(f"HTTP {alert_type} alert sent for {server_name}")
    
    def _record_alert(self, alert_type, subject, message, recipients=None):
        """Record alert in history"""
        alert_record = {
            'timestamp': datetime.now().isoformat(),
            'type': alert_type,
            'subject': subject,
            'message': message,
            'recipients': recipients or []
        }
        
        self.alert_history.append(alert_record)
        
        # Keep only recent alerts
        if len(self.alert_history) > self.max_history:
            self.alert_history = self.alert_history[-self.max_history:]
    
    def get_alert_history(self, limit=50):
        """Get recent alert history"""
        return self.alert_history[-limit:] if limit else self.alert_history
    
    def clear_alert_history(self):
        """Clear alert history"""
        self.alert_history.clear()
        logger.info("Alert history cleared")

# Global alert manager instance
alert_manager = AlertManager()

# Convenience functions
def play_sound_alert():
    """Play sound alert"""
    alert_manager.play_sound_alert()

def send_email_alert(subject, message, recipients=None):
    """Send email alert"""
    return alert_manager.send_email_alert(subject, message, recipients)

def send_server_down_alert(server_name, host, status, details=None):
    """Send server down alert"""
    alert_manager.send_server_down_alert(server_name, host, status, details)

def send_server_recovery_alert(server_name, host, previous_status):
    """Send server recovery alert"""
    alert_manager.send_server_recovery_alert(server_name, host, previous_status)

def send_port_alert(server_name, host, port, port_type, is_recovery=False):
    """Send port alert"""
    alert_manager.send_port_alert(server_name, host, port, port_type, is_recovery)

def send_http_alert(server_name, url, status_code, error, is_recovery=False):
    """Send HTTP alert"""
    alert_manager.send_http_alert(server_name, url, status_code, error, is_recovery)