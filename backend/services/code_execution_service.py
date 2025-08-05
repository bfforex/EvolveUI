from typing import Dict, Any, Optional, List
import subprocess
import tempfile
import os
import time
import signal
import asyncio
from concurrent.futures import ThreadPoolExecutor
import logging
import re

logger = logging.getLogger(__name__)

class CodeExecutionService:
    def __init__(self):
        """Initialize code execution service"""
        self.executor = ThreadPoolExecutor(max_workers=2)
        self.supported_languages = {
            'python': {
                'command': ['python3', '-c'],
                'file_extension': '.py',
                'timeout': 30
            },
            'javascript': {
                'command': ['node', '-e'],
                'file_extension': '.js',
                'timeout': 30
            },
            'bash': {
                'command': ['bash', '-c'],
                'file_extension': '.sh',
                'timeout': 30
            }
        }
        
        # Create temp directory for code execution
        self.temp_dir = tempfile.mkdtemp(prefix='evolveui_code_')
        
    def detect_language(self, code: str) -> Optional[str]:
        """Detect programming language from code"""
        code_lower = code.lower().strip()
        
        # Python indicators
        python_patterns = [
            r'\bimport\s+\w+',
            r'\bfrom\s+\w+\s+import',
            r'\bdef\s+\w+\s*\(',
            r'\bclass\s+\w+\s*\(',
            r'\bif\s+__name__\s*==\s*["\']__main__["\']',
            r'\bprint\s*\(',
            r'^\s*#.*python',
        ]
        
        # JavaScript indicators
        js_patterns = [
            r'\bconsole\.log\s*\(',
            r'\bfunction\s+\w+\s*\(',
            r'\bconst\s+\w+\s*=',
            r'\blet\s+\w+\s*=',
            r'\bvar\s+\w+\s*=',
            r'\brequire\s*\(',
            r'^\s*//.*js',
        ]
        
        # Bash indicators
        bash_patterns = [
            r'^\s*#!/bin/bash',
            r'^\s*#!/bin/sh',
            r'\becho\s+',
            r'\bexport\s+\w+',
            r'\$\w+',
            r'^\s*#.*bash',
        ]
        
        # Count matches for each language
        python_score = sum(1 for pattern in python_patterns if re.search(pattern, code, re.MULTILINE))
        js_score = sum(1 for pattern in js_patterns if re.search(pattern, code, re.MULTILINE))
        bash_score = sum(1 for pattern in bash_patterns if re.search(pattern, code, re.MULTILINE))
        
        # Return language with highest score
        scores = {'python': python_score, 'javascript': js_score, 'bash': bash_score}
        max_score = max(scores.values())
        
        if max_score > 0:
            return max(scores, key=scores.get)
        
        # Default to python if no clear indicators
        return 'python'
    
    async def execute_code(self, code: str, language: Optional[str] = None, timeout: int = 30) -> Dict[str, Any]:
        """Execute code safely with timeout"""
        
        # Detect language if not specified
        if not language:
            language = self.detect_language(code)
        
        if language not in self.supported_languages:
            return {
                "success": False,
                "error": f"Unsupported language: {language}",
                "supported_languages": list(self.supported_languages.keys())
            }
        
        lang_config = self.supported_languages[language]
        execution_timeout = min(timeout, lang_config['timeout'])
        
        try:
            # Run code execution in thread pool
            loop = asyncio.get_event_loop()
            result = await loop.run_in_executor(
                self.executor,
                self._execute_code_sync,
                code,
                language,
                execution_timeout
            )
            
            return result
            
        except Exception as e:
            logger.error(f"Code execution error: {e}")
            return {
                "success": False,
                "error": str(e),
                "language": language
            }
    
    def _execute_code_sync(self, code: str, language: str, timeout: int) -> Dict[str, Any]:
        """Synchronous code execution (runs in thread pool)"""
        lang_config = self.supported_languages[language]
        
        try:
            # Basic security checks
            security_check = self._check_code_security(code, language)
            if not security_check["safe"]:
                return {
                    "success": False,
                    "error": f"Security check failed: {security_check['reason']}",
                    "language": language
                }
            
            # Create temporary file for code
            file_ext = lang_config['file_extension']
            temp_file = os.path.join(self.temp_dir, f"code_{int(time.time())}{file_ext}")
            
            # Prepare execution command
            if language in ['python', 'javascript']:
                # For Python and JS, execute code directly
                cmd = lang_config['command'] + [code]
            else:
                # For bash, write to file first
                with open(temp_file, 'w') as f:
                    f.write(code)
                cmd = lang_config['command'] + [code]
            
            # Execute with timeout
            start_time = time.time()
            process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                cwd=self.temp_dir,
                preexec_fn=os.setsid  # Create new process group for easier termination
            )
            
            try:
                stdout, stderr = process.communicate(timeout=timeout)
                execution_time = time.time() - start_time
                
                # Clean up temp file
                if os.path.exists(temp_file):
                    os.remove(temp_file)
                
                return {
                    "success": True,
                    "language": language,
                    "stdout": stdout,
                    "stderr": stderr,
                    "return_code": process.returncode,
                    "execution_time": execution_time,
                    "timeout": timeout
                }
                
            except subprocess.TimeoutExpired:
                # Kill the process group
                os.killpg(os.getpgid(process.pid), signal.SIGTERM)
                process.communicate()  # Clean up
                
                return {
                    "success": False,
                    "error": f"Code execution timed out after {timeout} seconds",
                    "language": language,
                    "timeout": timeout
                }
                
        except Exception as e:
            return {
                "success": False,
                "error": f"Execution error: {str(e)}",
                "language": language
            }
        finally:
            # Clean up any remaining temp files
            if 'temp_file' in locals() and os.path.exists(temp_file):
                try:
                    os.remove(temp_file)
                except:
                    pass
    
    def _check_code_security(self, code: str, language: str) -> Dict[str, Any]:
        """Basic security checks for code execution"""
        
        # Common dangerous patterns
        dangerous_patterns = [
            r'\bexec\s*\(',
            r'\beval\s*\(',
            r'\b__import__\s*\(',
            r'\bopen\s*\(',
            r'\bfile\s*\(',
            r'\bos\.',
            r'\bsys\.',
            r'\bsubprocess\.',
            r'\bshutil\.',
            r'\bglob\.',
            r'\brm\s+-rf',
            r'\bdel\s+/',
            r'\bmkdir\s+/',
            r'\bchmod\s+',
            r'\bchown\s+',
            r'\bsu\s+',
            r'\bsudo\s+',
            r'\bcurl\s+',
            r'\bwget\s+',
            r'\bgit\s+clone',
            r'\bpip\s+install',
            r'\bnpm\s+install'
        ]
        
        code_lower = code.lower()
        
        for pattern in dangerous_patterns:
            if re.search(pattern, code_lower):
                return {
                    "safe": False,
                    "reason": f"Potentially dangerous pattern detected: {pattern}"
                }
        
        # Check for network operations
        network_patterns = [
            r'\bsocket\.',
            r'\brequests\.',
            r'\burllib\.',
            r'\bhttp\.',
            r'\bftp\.',
            r'fetch\s*\(',
            r'axios\.',
            r'XMLHttpRequest'
        ]
        
        for pattern in network_patterns:
            if re.search(pattern, code_lower):
                return {
                    "safe": False,
                    "reason": f"Network operation detected: {pattern}"
                }
        
        # Length check
        if len(code) > 10000:  # 10KB limit
            return {
                "safe": False,
                "reason": "Code too long (max 10KB)"
            }
        
        return {"safe": True}
    
    def get_language_info(self, language: str) -> Optional[Dict[str, Any]]:
        """Get information about a supported language"""
        if language not in self.supported_languages:
            return None
        
        config = self.supported_languages[language]
        return {
            "language": language,
            "command": config['command'],
            "file_extension": config['file_extension'],
            "timeout": config['timeout'],
            "available": self._check_language_availability(language)
        }
    
    def _check_language_availability(self, language: str) -> bool:
        """Check if a language runtime is available"""
        config = self.supported_languages[language]
        try:
            # Try to run a simple command to check availability
            subprocess.run(
                config['command'][:1] + ['--version'],
                capture_output=True,
                timeout=5
            )
            return True
        except:
            return False
    
    def get_service_status(self) -> Dict[str, Any]:
        """Get code execution service status"""
        languages_status = {}
        for lang in self.supported_languages:
            languages_status[lang] = self._check_language_availability(lang)
        
        return {
            "available": True,
            "supported_languages": list(self.supported_languages.keys()),
            "language_availability": languages_status,
            "temp_directory": self.temp_dir,
            "security_features": [
                "pattern_filtering",
                "timeout_protection",
                "process_isolation",
                "file_system_restrictions"
            ]
        }
    
    def cleanup(self):
        """Clean up temporary directory"""
        try:
            import shutil
            shutil.rmtree(self.temp_dir)
        except Exception as e:
            logger.warning(f"Could not clean up temp directory: {e}")
    
    def __del__(self):
        """Cleanup on destruction"""
        self.cleanup()