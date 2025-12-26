import mailbox
from bs4 import BeautifulSoup
import re

# ===== HTML to Text =====
def html_to_text(html_content):
    soup = BeautifulSoup(html_content, 'html.parser')
    return soup.get_text(separator='\n', strip=True)

# ===== Extract Email Body =====
def get_email_body(message):
    if message.is_multipart():
        for part in message.walk():
            content_type = part.get_content_type()
            
            if content_type == "text/plain":
                try:
                    return part.get_payload(decode=True).decode('utf-8', errors='ignore')
                except:
                    continue
            elif content_type == "text/html":
                try:
                    html = part.get_payload(decode=True).decode('utf-8', errors='ignore')
                    return html_to_text(html)
                except:
                    continue
        return ""
    else:
        try:
            payload = message.get_payload(decode=True).decode('utf-8', errors='ignore')
            if message.get_content_type() == "text/html":
                return html_to_text(payload)
            else:
                return payload
        except:
            return ""

# ===== FILTERS =====
def remove_forwarded_content(text):
    """Remove forwarded emails."""
    forward_patterns = [
        r'[-]{5,}\s*Forwarded message\s*[-]{5,}',
        r'Begin forwarded message:',
        r'_{5,}\s*Forwarded message\s*_{5,}',
        r'From:.*\nSent:.*\nTo:.*\nSubject:',
    ]
    
    earliest_pos = len(text)
    for pattern in forward_patterns:
        match = re.search(pattern, text, re.IGNORECASE | re.MULTILINE)
        if match:
            earliest_pos = min(earliest_pos, match.start())
    
    if earliest_pos < len(text):
        text = text[:earliest_pos]
    
    # Remove quoted lines (>)
    lines = text.split('\n')
    filtered_lines = [line for line in lines if not line.strip().startswith('>')]
    text = '\n'.join(filtered_lines)
    
    return text.strip()

def remove_reply_history(text):
    """Remove 'On [date] wrote:' style replies."""
    reply_pattern = r'\nOn .+? wrote:\s*$'
    match = re.search(reply_pattern, text, re.MULTILINE)
    if match:
        text = text[:match.start()]
    return text.strip()

def clean_email_body(text):
    """Apply all filters."""
    text = remove_forwarded_content(text)
    text = remove_reply_history(text)
    text = re.sub(r'\n{3,}', '\n\n', text)
    return text.strip()

# ===== Process Mbox with Filtering =====
def process_mbox_filtered(mbox_file, output_file, min_length=50):
    """
    Process mbox, keeping only original writing.
    
    Args:
        mbox_file: input .mbox file
        output_file: output text file
        min_length: skip emails shorter than this (default 50 chars)
    """
    mbox = mailbox.mbox(mbox_file)
    
    total = 0
    kept = 0
    
    with open(output_file, 'w', encoding='utf-8') as f:
        for i, message in enumerate(mbox):
            total += 1
            
            if i % 100 == 0:
                print(f"Processing email {i}... (kept {kept} so far)")
            
            # Extract and filter
            body = get_email_body(message)
            body = clean_email_body(body)
            
            # Keep if long enough
            if body and len(body) >= min_length:
                f.write(body)
                f.write("\n\n---\n\n")
                kept += 1
    
    print(f"\nDone!")
    print(f"Total emails: {total}")
    print(f"Kept: {kept}")
    print(f"Filtered out: {total - kept}")

# ===== Run It! =====
if __name__ == "__main__":
    process_mbox_filtered(
        mbox_file="email.mbox",
        output_file="input.txt",
        min_length=50  # Adjust this as needed
    )