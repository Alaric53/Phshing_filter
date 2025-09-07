import os
import re
from pathlib import Path
from typing import Optional, Dict
import PyPDF2
import pdfplumber
from bs4 import BeautifulSoup
from datetime import datetime
import email
import extract_msg


class EmailInputHandler:
    """
    Clean email input handler for phishing detection.
    Supports: TXT, PDF (Outlook print-to-PDF), EML, MSG
    
    Output: Clean plain text with subject and body content only.
    """
    
    SUPPORTED_EXTENSIONS = {'.txt', '.pdf', '.eml', '.msg'}
    
    def __init__(self):
        """Initialize the handler silently."""
        pass
    
    def process_input(self, file_path: str = None, text_content: str = None, 
                      debug: bool = False, log_path: str = None) -> str:
        """
        Main method: process file or text and return clean plain text.
        
        Args:
            file_path: Path to email file (.txt, .pdf, .eml, .msg)
            text_content: Plain text content
            debug: Show processing details
            log_path: Log file for text inputs
            
        Returns:
            Clean plain text: "subject-content sender-name sender@email.com body-content"
        """
        if file_path is None and text_content is None:
            raise ValueError("Provide either file_path or text_content")
        
        if file_path is not None and text_content is not None:
            raise ValueError("Provide only one: file_path OR text_content")
        
        # Process file
        if file_path is not None:
            if not os.path.exists(file_path):
                raise FileNotFoundError(f"File not found: {file_path}")
            
            if debug:
                print(f"Processing: {file_path}")
            
            return self._process_file(file_path, debug)
        
        # Process text
        if text_content is not None:
            if debug:
                print(f"Processing text ({len(text_content)} chars)")
            
            if log_path:
                self._log_input(text_content, log_path)
            
            email_data = self._parse_text_content(text_content)
            return self._format_clean_output(email_data, debug)
        
        return ""
    
    def _detect_file_type(self, file_path: str) -> Optional[str]:
        """Detect supported file type."""
        extension = Path(file_path).suffix.lower()
        
        if extension == '.txt':
            return 'txt'
        elif extension == '.pdf':
            return 'pdf'
        elif extension == '.eml':
            return 'eml'
        elif extension == '.msg':
            return 'msg'
        else:
            print(f"Unsupported file type: {extension}")
            return None
    
    def _process_file(self, file_path: str, debug: bool = False) -> str:
        """Process any supported file type."""
        file_type = self._detect_file_type(file_path)
        
        if not file_type:
            return ""
        
        if debug:
            print(f"File type: {file_type}")
        
        # Extract email data based on type
        if file_type == 'txt':
            email_data = self._extract_from_txt(file_path, debug)
        elif file_type == 'pdf':
            email_data = self._extract_from_pdf(file_path, debug)
        elif file_type == 'eml':
            email_data = self._extract_from_eml(file_path, debug)
        elif file_type == 'msg':
            email_data = self._extract_from_msg(file_path, debug)
        else:
            return ""
        
        return self._format_clean_output(email_data, debug)
    
    def _extract_from_txt(self, file_path: str, debug: bool = False) -> Dict[str, str]:
        """Extract from plain text file."""
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
            
            if debug:
                print(f"TXT: Read {len(content)} characters")
            
            return self._parse_text_content(content)
            
        except Exception as e:
            print(f"Error reading TXT: {e}")
            return {'subject': '', 'from': '', 'body': ''}
    
    def _extract_from_pdf(self, file_path: str, debug: bool = False) -> Dict[str, str]:
        """Extract from PDF (Outlook print-to-PDF)."""
        try:
            text = ""
            
            # Try pdfplumber first
            try:
                with pdfplumber.open(file_path) as pdf:
                    if debug:
                        print(f"PDF: {len(pdf.pages)} pages")
                    
                    for i, page in enumerate(pdf.pages):
                        page_text = page.extract_text()
                        if page_text:
                            text += page_text + "\n"
                            if debug:
                                print(f"Page {i+1}: {len(page_text)} chars")
            
            except Exception as e1:
                if debug:
                    print(f"pdfplumber failed: {e1}, trying PyPDF2")
                
                # Fallback to PyPDF2
                with open(file_path, 'rb') as f:
                    reader = PyPDF2.PdfReader(f, strict=False)
                    for i, page in enumerate(reader.pages):
                        page_text = page.extract_text()
                        if page_text:
                            text += page_text + "\n"
                            if debug:
                                print(f"Page {i+1}: {len(page_text)} chars")
            
            if not text.strip():
                if debug:
                    print("No text extracted from PDF")
                return {'subject': '', 'from': '', 'body': 'PDF_EXTRACTION_FAILED'}
            
            if debug:
                print(f"PDF: Total {len(text)} characters extracted")
            
            return self._parse_text_content(text)
            
        except Exception as e:
            print(f"Error extracting PDF: {e}")
            return {'subject': '', 'from': '', 'body': ''}
    
    def _extract_from_eml(self, file_path: str, debug: bool = False) -> Dict[str, str]:
        """Extract from EML file."""
        try:
            # Try different encodings
            content = None
            for encoding in ['utf-8', 'latin-1', 'cp1252']:
                try:
                    with open(file_path, 'r', encoding=encoding) as f:
                        content = f.read()
                    if debug:
                        print(f"EML: Read with {encoding}")
                    break
                except UnicodeDecodeError:
                    continue
            
            if not content:
                # Binary fallback
                with open(file_path, 'rb') as f:
                    content = f.read().decode('utf-8', errors='ignore')
                if debug:
                    print("EML: Used binary fallback")
            
            # Parse email
            msg = email.message_from_string(content)
            
            subject = msg.get('Subject', '').strip()
            sender = msg.get('From', '').strip()
            body = self._extract_email_body(msg, debug)
            
            if debug:
                print(f"EML: Subject='{subject[:50]}...', From='{sender[:50]}...', Body={len(body)} chars")
            
            return {
                'subject': subject,
                'from': sender,
                'body': body
            }
            
        except Exception as e:
            print(f"Error extracting EML: {e}")
            return {'subject': '', 'from': '', 'body': ''}
    
    def _extract_from_msg(self, file_path: str, debug: bool = False) -> Dict[str, str]:
        """Extract from MSG file with enhanced body extraction."""
        try:
            msg = extract_msg.Message(file_path)
            
            subject = msg.subject or ''
            sender = msg.sender or ''
            
            # Try multiple methods to get the body content
            body = ''
            
            # Method 1: Standard body property
            if msg.body:
                body = msg.body
                if debug:
                    print(f"MSG: Got body from .body property ({len(body)} chars)")
            
            # Method 2: Try HTML body and convert to text
            elif hasattr(msg, 'htmlBody') and msg.htmlBody:
                try:
                    from bs4 import BeautifulSoup
                    soup = BeautifulSoup(msg.htmlBody, 'html.parser')
                    body = soup.get_text(separator=' ')
                    if debug:
                        print(f"MSG: Got body from HTML conversion ({len(body)} chars)")
                except Exception as e:
                    if debug:
                        print(f"MSG: HTML conversion failed: {e}")
            
            # Method 3: Try RTF body (if available)
            elif hasattr(msg, 'rtfBody') and msg.rtfBody:
                try:
                    # Simple RTF text extraction (remove RTF codes)
                    rtf_body = str(msg.rtfBody)
                    # Remove RTF control codes (basic cleaning)
                    body = re.sub(r'\\[a-zA-Z]+\d*\s?', '', rtf_body)
                    body = re.sub(r'[{}]', '', body)
                    if debug:
                        print(f"MSG: Got body from RTF conversion ({len(body)} chars)")
                except Exception as e:
                    if debug:
                        print(f"MSG: RTF conversion failed: {e}")
            
            # Method 4: Try to access raw message properties
            else:
                try:
                    # Try different property approaches
                    if hasattr(msg, '_getStringStream'):
                        # Try to get the message body through different property IDs
                        body_props = [
                            '0x1000001F',  # PR_BODY
                            '0x1013001F',  # PR_HTML  
                            '0x10090102',  # PR_RTF_COMPRESSED
                        ]
                        
                        for prop in body_props:
                            try:
                                body_content = msg._getStringStream(prop)
                                if body_content:
                                    body = body_content
                                    if debug:
                                        print(f"MSG: Got body from property {prop} ({len(body)} chars)")
                                    break
                            except:
                                continue
                                
                except Exception as e:
                    if debug:
                        print(f"MSG: Property access failed: {e}")
            
            # Method 5: Fallback - try to read the MSG file as binary and extract text
            if not body:
                try:
                    if debug:
                        print("MSG: Trying binary fallback extraction")
                    
                    with open(file_path, 'rb') as f:
                        raw_data = f.read()
                    
                    # Look for text patterns in the binary data
                    # Convert to string and extract readable parts
                    text_data = raw_data.decode('utf-8', errors='ignore')
                    
                    # Extract potential email content (basic heuristic)
                    # Look for common email patterns
                    patterns = [
                        r'Dear [^,\n]+[,\n](.+?)(?=From:|Sent:|Subject:|$)',
                        r'Hi [^,\n]+[,\n](.+?)(?=From:|Sent:|Subject:|$)',
                        r'Hello[^,\n]*[,\n](.+?)(?=From:|Sent:|Subject:|$)',
                    ]
                    
                    for pattern in patterns:
                        matches = re.findall(pattern, text_data, re.DOTALL | re.IGNORECASE)
                        if matches:
                            body = ' '.join(matches)
                            break
                    
                    # If no pattern match, try to extract all readable text
                    if not body:
                        # Extract sequences of printable characters
                        readable_parts = re.findall(r'[^\x00-\x1F\x7F-\xFF]{20,}', text_data)
                        if readable_parts:
                            body = ' '.join(readable_parts)
                    
                    if body and debug:
                        print(f"MSG: Got body from binary fallback ({len(body)} chars)")
                        
                except Exception as e:
                    if debug:
                        print(f"MSG: Binary fallback failed: {e}")
            
            if debug:
                print(f"MSG: Final result - Subject='{subject[:50]}...', From='{sender[:50]}...', Body={len(body)} chars")
                if body:
                    print(f"MSG: Body preview: {body[:100]}...")
            
            msg.close()
            
            return {
                'subject': subject,
                'from': sender,
                'body': body
            }
            
        except Exception as e:
            print(f"Error extracting MSG: {e}")
            if debug:
                import traceback
                traceback.print_exc()
            return {'subject': '', 'from': '', 'body': ''}
    
    def _extract_email_body(self, msg, debug: bool = False) -> str:
        """Extract body from email message (for EML)."""
        body = ""
        
        try:
            if msg.is_multipart():
                for part in msg.walk():
                    content_type = part.get_content_type()
                    disposition = str(part.get("Content-Disposition", ""))
                    
                    # Skip attachments
                    if "attachment" in disposition:
                        continue
                    
                    if content_type == "text/plain":
                        charset = part.get_content_charset() or 'utf-8'
                        payload = part.get_payload(decode=True)
                        if payload:
                            try:
                                body += payload.decode(charset, errors='ignore') + "\n"
                            except:
                                body += str(payload) + "\n"
                    
                    elif content_type == "text/html" and not body:
                        # If no plain text, convert HTML
                        charset = part.get_content_charset() or 'utf-8'
                        html_payload = part.get_payload(decode=True)
                        if html_payload:
                            try:
                                html_text = html_payload.decode(charset, errors='ignore')
                                soup = BeautifulSoup(html_text, 'html.parser')
                                body += soup.get_text(separator=' ') + "\n"
                            except:
                                pass
            else:
                # Single part message
                content_type = msg.get_content_type()
                
                if content_type == "text/plain":
                    charset = msg.get_content_charset() or 'utf-8'
                    payload = msg.get_payload(decode=True)
                    if payload:
                        try:
                            body = payload.decode(charset, errors='ignore')
                        except:
                            body = str(payload)
                
                elif content_type == "text/html":
                    charset = msg.get_content_charset() or 'utf-8'
                    html_payload = msg.get_payload(decode=True)
                    if html_payload:
                        try:
                            html_text = html_payload.decode(charset, errors='ignore')
                            soup = BeautifulSoup(html_text, 'html.parser')
                            body = soup.get_text(separator=' ')
                        except:
                            pass
        
        except Exception as e:
            if debug:
                print(f"Body extraction error: {e}")
        
        return body.strip()
    
    def _parse_text_content(self, text: str) -> Dict[str, str]:
        """Parse any text content to extract subject, sender, body."""
        subject = ''
        sender = ''
        body = text
        
        # Extract subject
        subject_patterns = [
            r'Subject:\s*(.+?)(?:\n|$)',
            r'RE:\s*(.+?)(?:\n|$)',
            r'FW:\s*(.+?)(?:\n|$)',
            r'Fwd:\s*(.+?)(?:\n|$)'
        ]
        
        for pattern in subject_patterns:
            match = re.search(pattern, text, re.IGNORECASE | re.MULTILINE)
            if match:
                subject = match.group(1).strip()
                body = body.replace(match.group(0), '')
                break
        
        # Extract sender
        sender_patterns = [
            r'From:\s*(.+?)(?:\n|$)',
            r'Sender:\s*(.+?)(?:\n|$)',
        ]
        
        for pattern in sender_patterns:
            match = re.search(pattern, text, re.IGNORECASE | re.MULTILINE)
            if match:
                sender = match.group(1).strip()
                body = body.replace(match.group(0), '')
                break
        
        # If no sender found, look for email addresses
        if not sender:
            email_match = re.search(r'[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}', text)
            if email_match:
                sender = email_match.group(0)
        
        return {
            'subject': subject,
            'from': sender,
            'body': body
        }
    
    def _format_clean_output(self, email_data: Dict[str, str], debug: bool = False) -> str:
        """Format into clean plain text output."""
        # Clean each component
        subject = self._clean_subject(email_data.get('subject', ''))
        sender = self._clean_sender(email_data.get('from', ''))
        body = self._clean_body(email_data.get('body', ''))
        
        if debug:
            print(f"Cleaned - Subject: '{subject[:50]}...', Sender: '{sender}', Body: {len(body)} chars")
        
        # Combine into final output
        parts = []
        
        if subject:
            parts.append(subject)
        
        if sender:
            parts.append(sender)
        
        if body:
            parts.append(body)
        
        # Join and final clean
        result = ' '.join(parts)
        result = re.sub(r'\s+', ' ', result).strip()
        
        return result
    
    def _clean_subject(self, subject: str) -> str:
        """Clean subject line."""
        if not subject:
            return ""
        
        # Remove RE:, FW:, Fwd: prefixes
        subject = re.sub(r'^\s*(?:RE|FW|FWD|Fwd|Re|Fw):\s*', '', subject, flags=re.IGNORECASE)
        
        # Remove MIME encoding
        subject = re.sub(r'=\?.*?\?=', '', subject)
        
        # Remove null characters and clean
        subject = re.sub(r'\x00', '', subject)
        subject = re.sub(r'[^\x20-\x7E]', ' ', subject)
        subject = re.sub(r'\s+', ' ', subject).strip()
        
        return subject
    
    def _clean_sender(self, sender: str) -> str:
        """Clean sender: keep name and email, remove < > brackets."""
        if not sender:
            return ""
        
        # Handle "Name <email@domain.com>" format
        match = re.match(r'^(.*?)\s*<([^>]+)>\s*$', sender)
        if match:
            name = match.group(1).strip()
            email = match.group(2).strip()
            
            # Remove quotes around name
            name = re.sub(r'^["\'](.*)["\']$', r'\1', name)
            
            # Clean name
            name = re.sub(r'\x00', '', name)
            name = re.sub(r'[^\x20-\x7E]', ' ', name)
            name = re.sub(r'\s+', ' ', name).strip()
            
            # Combine name and email
            if name and email:
                return f"{name} {email}"
            elif email:
                return email
            elif name:
                return name
        
        # No angle brackets, clean as-is
        sender = re.sub(r'[<>]', '', sender)
        sender = re.sub(r'^["\'](.*)["\']$', r'\1', sender)
        sender = re.sub(r'\x00', '', sender)
        sender = re.sub(r'[^\x20-\x7E]', ' ', sender)
        sender = re.sub(r'\s+', ' ', sender).strip()
        
        return sender
    
    def _clean_body(self, body: str) -> str:
        """Aggressively clean body text."""
        if not body:
            return ""
        
        # Remove all email headers
        headers = [
            r'To:\s*.*?(?:\n|$)', r'From:\s*.*?(?:\n|$)', r'Cc:\s*.*?(?:\n|$)',
            r'Bcc:\s*.*?(?:\n|$)', r'Date:\s*.*?(?:\n|$)', r'Sent:\s*.*?(?:\n|$)',
            r'Subject:\s*.*?(?:\n|$)', r'Message-ID:\s*.*?(?:\n|$)',
            r'Content-Type:\s*.*?(?:\n|$)', r'MIME-Version:\s*.*?(?:\n|$)',
            r'X-.*?:\s*.*?(?:\n|$)', r'Return-Path:\s*.*?(?:\n|$)',
            r'Received:\s*.*?(?:\n|$)', r'Reply-To:\s*.*?(?:\n|$)',
        ]
        
        for header in headers:
            body = re.sub(header, '', body, flags=re.IGNORECASE | re.MULTILINE)
        
        # Remove timestamps and dates
        timestamps = [
            r'\b\d{1,2}[\/\-\.]\d{1,2}[\/\-\.]\d{2,4}\b',
            r'\b\d{1,2}:\d{2}(?::\d{2})?\s*(?:AM|PM|am|pm)?\b',
            r'\b(?:Monday|Tuesday|Wednesday|Thursday|Friday|Saturday|Sunday),?\s*\d{1,2}\s+(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)\s+\d{2,4}\b',
            r'\bSent:\s*.*?(?:\n|$)',
            r'\bOn\s+.*?\s+wrote:.*?(?:\n|$)',
        ]
        
        for pattern in timestamps:
            body = re.sub(pattern, '', body, flags=re.IGNORECASE)
        
        # Remove email addresses in angle brackets
        body = re.sub(r'<[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}>', '', body)
        
        # Remove RE:, FW: anywhere in text
        body = re.sub(r'\b(?:RE|FW|FWD|Fwd|Re|Fw):\s*', '', body, flags=re.IGNORECASE)
        
        # Remove \r\n and normalize line endings
        body = re.sub(r'\r\n', ' ', body)
        body = re.sub(r'\r', ' ', body)
        body = re.sub(r'\n', ' ', body)
        
        # Remove quote markers
        body = re.sub(r'^>\s*', '', body, flags=re.MULTILINE)
        
        # Remove signatures
        body = re.sub(r'--\s*.*$', '', body, flags=re.MULTILINE | re.DOTALL)
        body = re.sub(r'Sent from my.*?(?:\n|$)', '', body, flags=re.IGNORECASE)
        
        # Remove URLs
        body = re.sub(r'https?://[^\s]+', '', body)
        body = re.sub(r'www\.[^\s]+', '', body)
        
        # Remove separators and artifacts
        body = re.sub(r'_{3,}', '', body)
        body = re.sub(r'=\d{2}', '', body)
        body = re.sub(r'\x00', '', body)
        
        # Remove non-printable characters
        body = re.sub(r'[^\x20-\x7E]', ' ', body)
        
        # Final whitespace cleanup
        body = re.sub(r'\s+', ' ', body).strip()
        
        return body
    
    def _log_input(self, text: str, log_path: str) -> None:
        """Log text input with timestamp."""
        try:
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            log_entry = f"[{timestamp}] Input:\n{text}\n\n"
            
            mode = 'a' if os.path.exists(log_path) else 'w'
            with open(log_path, mode, encoding='utf-8') as f:
                f.write(log_entry)
        except Exception as e:
            print(f"Logging error: {e}")


# Test when run directly
if __name__ == "__main__":
    print("=== EmailInputHandler Test ===")
    
    handler = EmailInputHandler()
    
    # Test with sample text
    test_text = """
    Subject: RE: Urgent Business Proposal
    From: "John Doe" <john@scammer.com>
    Sent: Monday, January 15, 2024 3:45 PM
    
    Dear friend,
    
    I have an urgent business proposal for you.
    Please contact me at <john@scammer.com>.
    
    Best regards,
    John Doe
    """
    
    result = handler.process_input(text_content=test_text, debug=True)
    print(f"\nResult: {result}")
    
    print("\n=== Test Complete ===")