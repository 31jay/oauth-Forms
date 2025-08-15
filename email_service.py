import smtplib
import streamlit as st
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.utils import formataddr
import logging
from datetime import datetime

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def load_email_template(template_name="lead_mail.txt"):
    """Load email template from file"""
    try:
        with open(template_name, 'r', encoding='utf-8') as f:
            return f.read()
    except FileNotFoundError:
        logger.error(f"Email template file {template_name} not found")
        return None
    except Exception as e:
        logger.error(f"Error loading email template {template_name}: {str(e)}")
        return None

def get_smtp_config():
    """Get SMTP configuration from Streamlit secrets"""
    try:
        smtp_config = {
            'server': st.secrets["email"]["SMTP_SERVER"],
            'port': int(st.secrets["email"]["SMTP_PORT"]),
            'username': st.secrets["email"]["SMTP_USERNAME"],
            'password': st.secrets["email"]["SMTP_PASSWORD"],
            'sender_name': st.secrets["email"]["SENDER_NAME"],
            'sender_email': st.secrets["email"]["SENDER_EMAIL"]
        }
        return smtp_config
    except KeyError as e:
        logger.error(f"Missing email configuration: {str(e)}")
        return None
    except Exception as e:
        logger.error(f"Error getting SMTP configuration: {str(e)}")
        return None

def create_email_content(recipient_name, team_name, submission_type, team_details=None, email_type="general"):
    """Create personalized email content based on email type"""
    
    # Determine which template to use
    if email_type == "team_member":
        template = load_email_template("members_mail.txt")
    else:
        template = load_email_template("lead_mail.txt")
    
    if not template:
        return None
    
    # Get current timestamp
    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    # Replace common placeholders
    content = template.replace("{RECIPIENT_NAME}", recipient_name)
    content = content.replace("{TEAM_NAME}", team_name)
    content = content.replace("{SUBMISSION_TYPE}", submission_type)
    content = content.replace("{TIMESTAMP}", current_time)
    
    # Handle team-specific placeholders
    if team_details:
        if email_type == "team_member":
            # For team member template (template2)
            team_lead_name = team_details.get('team_lead_name', 'Team Lead')
            content = content.replace("{TEAM_LEAD_NAME}", team_lead_name)
            content = content.replace("{TEAM_NAME_DETAILS}", team_details.get('team_name', 'Your Team'))
            
            # Add member details section
            member_details = f"""
Your Details:
- Name: {recipient_name}
- Team: {team_details.get('team_name', 'N/A')}
- Selected Role: {team_name}
- Team Members: {team_details.get('member_count', 1)} members
            """
            content = content.replace("{MEMBER_DETAILS}", member_details)
        else:
            # For general template (template1) - team lead
            team_info = f"""
Team Name: {team_details['team_name']}
Team Members: {team_details['member_count']} members
            """
            content = content.replace("{TEAM_DETAILS}", team_info)
    else:
        # Remove team-specific placeholders for individual applications
        content = content.replace("{TEAM_DETAILS}", "")
        content = content.replace("{TEAM_LEAD_NAME}", "")
        content = content.replace("{TEAM_NAME_DETAILS}", "")
        content = content.replace("{MEMBER_DETAILS}", "")
    
    return content

def send_confirmation_email(recipient_email, recipient_name, team_name, submission_type, team_details=None, email_type="general"):
    """Send confirmation email to the recipient"""
    try:
        # Get SMTP configuration
        smtp_config = get_smtp_config()
        if not smtp_config:
            logger.error("Failed to get SMTP configuration")
            return False
        
        # Create email content
        email_content = create_email_content(
            recipient_name, team_name, submission_type, team_details, email_type
        )
        if not email_content:
            logger.error("Failed to create email content")
            return False
        
        # Create message
        msg = MIMEMultipart()
        msg['From'] = formataddr((smtp_config['sender_name'], smtp_config['sender_email']))
        msg['To'] = recipient_email
        
        # Subject line based on submission type and email type
        if submission_type == "Team":
            if email_type == "team_member":
                subject = f"Team Invitation - {team_name} | Knowledge Sharing Circle"
            else:
                subject = f"Team Application Confirmed - {team_name} | Knowledge Sharing Circle"
        else:
            subject = f"Application Confirmed - {team_name} | Knowledge Sharing Circle"
        
        msg['Subject'] = subject
        
        # Attach email body
        msg.attach(MIMEText(email_content, 'plain', 'utf-8'))
        
        # Send email
        with smtplib.SMTP(smtp_config['server'], smtp_config['port']) as server:
            server.starttls()
            server.login(smtp_config['username'], smtp_config['password'])
            
            text = msg.as_string()
            server.sendmail(smtp_config['sender_email'], recipient_email, text)
        
        logger.info(f"Confirmation email sent successfully to {recipient_email} (type: {email_type})")
        return True
        
    except smtplib.SMTPAuthenticationError:
        logger.error("SMTP Authentication failed - check username/password")
        return False
    except smtplib.SMTPRecipientsRefused:
        logger.error(f"Recipient email refused: {recipient_email}")
        return False
    except smtplib.SMTPServerDisconnected:
        logger.error("SMTP Server disconnected")
        return False
    except Exception as e:
        logger.error(f"Error sending email to {recipient_email}: {str(e)}")
        return False

def test_email_connection():
    """Test email connection and configuration"""
    try:
        smtp_config = get_smtp_config()
        if not smtp_config:
            return False, "Failed to get SMTP configuration"
        
        with smtplib.SMTP(smtp_config['server'], smtp_config['port']) as server:
            server.starttls()
            server.login(smtp_config['username'], smtp_config['password'])
        
        return True, "Email connection successful"
        
    except Exception as e:
        return False, f"Email connection failed: {str(e)}"