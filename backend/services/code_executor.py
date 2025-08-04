import subprocess
import tempfile
import os
import sys
import logging
import time
from typing import Dict, Any, Optional
from pathlib import Path
import uuid

logger = logging.getLogger(__name__)

class CodeExecutor:
    def __init__(self, timeout: int = 30, max_output_length: int = 10000):
        """Initialize code executor with safety constraints"""
        self.timeout = timeout
        self.max_output_length = max_output_length
        self.temp_dir = Path("/tmp/code_execution")
        self.temp_dir.mkdir(exist_ok=True)
        
        # Supported languages and their configurations
        self.supported_languages = {
            'python': {
                'extension': '.py',
                'command': [sys.executable, '-c'],
                'security_imports': [
                    'import sys',
                    'sys.dont_write_bytecode = True',
                ]
            },
            'javascript': {
                'extension': '.js',
                'command': ['node'],
                'security_imports': []
            },
            'bash': {
                'extension': '.sh',
                'command': ['bash'],
                'security_imports': []
            }
        }

    def get_supported_languages(self) -> list:
        """Get list of supported programming languages"""
        return list(self.supported_languages.keys())

    def is_language_available(self, language: str) -> bool:
        """Check if a programming language runtime is available"""
        if language not in self.supported_languages:
            return False
        
        try:
            if language == 'python':
                return True  # Python is available since we're running in Python
            elif language == 'javascript':
                result = subprocess.run(['node', '--version'], 
                                      capture_output=True, text=True, timeout=5)
                return result.returncode == 0
            elif language == 'bash':
                result = subprocess.run(['bash', '--version'], 
                                      capture_output=True, text=True, timeout=5)
                return result.returncode == 0
            return False
        except Exception:
            return False

    def execute_code(self, code: str, language: str = 'python', 
                    stdin_input: str = None) -> Dict[str, Any]:
        """Execute code safely and return results"""
        try:
            if language not in self.supported_languages:
                return {
                    "success": False,
                    "error": f"Unsupported language: {language}. Supported: {list(self.supported_languages.keys())}",
                    "output": "",
                    "stderr": "",
                    "execution_time": 0
                }
            
            if not self.is_language_available(language):
                return {
                    "success": False,
                    "error": f"Runtime for {language} is not available on this system",
                    "output": "",
                    "stderr": "",
                    "execution_time": 0
                }
            
            # Security check for dangerous operations
            security_violations = self._check_security_violations(code, language)
            if security_violations:
                return {
                    "success": False,
                    "error": f"Security violation detected: {', '.join(security_violations)}",
                    "output": "",
                    "stderr": "",
                    "execution_time": 0
                }
            
            start_time = time.time()
            
            if language == 'python':
                result = self._execute_python(code, stdin_input)
            elif language == 'javascript':
                result = self._execute_javascript(code, stdin_input)
            elif language == 'bash':
                result = self._execute_bash(code, stdin_input)
            else:
                result = {
                    "success": False,
                    "error": f"Execution not implemented for {language}",
                    "output": "",
                    "stderr": ""
                }
            
            execution_time = time.time() - start_time
            result["execution_time"] = round(execution_time, 3)
            
            # Truncate output if too long
            if len(result.get("output", "")) > self.max_output_length:
                result["output"] = result["output"][:self.max_output_length] + "\n... (output truncated)"
            
            if len(result.get("stderr", "")) > self.max_output_length:
                result["stderr"] = result["stderr"][:self.max_output_length] + "\n... (stderr truncated)"
            
            return result
            
        except Exception as e:
            logger.error(f"Code execution error: {e}")
            return {
                "success": False,
                "error": f"Execution error: {str(e)}",
                "output": "",
                "stderr": "",
                "execution_time": 0
            }

    def _check_security_violations(self, code: str, language: str) -> list:
        """Check for potentially dangerous operations"""
        violations = []
        code_lower = code.lower()
        
        # Common dangerous patterns
        dangerous_patterns = {
            'file_operations': ['open(', 'file(', 'with open'],
            'system_calls': ['os.system', 'subprocess', 'exec(', 'eval(', '__import__'],
            'network': ['urllib', 'requests', 'socket', 'http'],
            'dangerous_modules': ['os.remove', 'os.rmdir', 'shutil.rmtree', 'os.unlink']
        }
        
        if language == 'python':
            # Python-specific checks
            for category, patterns in dangerous_patterns.items():
                for pattern in patterns:
                    if pattern in code_lower:
                        violations.append(f"{category}: {pattern}")
        
        elif language == 'bash':
            # Bash-specific checks
            bash_dangerous = ['rm ', 'sudo', 'chmod', 'chown', '>/dev/', 'dd ', 'format']
            for pattern in bash_dangerous:
                if pattern in code_lower:
                    violations.append(f"dangerous_command: {pattern}")
        
        return violations

    def _execute_python(self, code: str, stdin_input: str = None) -> Dict[str, Any]:
        """Execute Python code"""
        try:
            # Add security imports
            lang_config = self.supported_languages['python']
            full_code = '\n'.join(lang_config['security_imports']) + '\n' + code
            
            # Execute using subprocess for better isolation
            process = subprocess.Popen(
                [sys.executable, '-c', full_code],
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                cwd=self.temp_dir
            )
            
            stdout, stderr = process.communicate(
                input=stdin_input,
                timeout=self.timeout
            )
            
            return {
                "success": process.returncode == 0,
                "output": stdout,
                "stderr": stderr,
                "return_code": process.returncode,
                "error": stderr if process.returncode != 0 else None
            }
            
        except subprocess.TimeoutExpired:
            process.kill()
            return {
                "success": False,
                "error": f"Code execution timed out after {self.timeout} seconds",
                "output": "",
                "stderr": "",
                "return_code": -1
            }
        except Exception as e:
            return {
                "success": False,
                "error": f"Python execution error: {str(e)}",
                "output": "",
                "stderr": "",
                "return_code": -1
            }

    def _execute_javascript(self, code: str, stdin_input: str = None) -> Dict[str, Any]:
        """Execute JavaScript code using Node.js"""
        try:
            # Create temporary file
            exec_id = str(uuid.uuid4())
            temp_file = self.temp_dir / f"temp_{exec_id}.js"
            
            with open(temp_file, 'w') as f:
                f.write(code)
            
            process = subprocess.Popen(
                ['node', str(temp_file)],
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                cwd=self.temp_dir
            )
            
            stdout, stderr = process.communicate(
                input=stdin_input,
                timeout=self.timeout
            )
            
            # Cleanup
            temp_file.unlink(missing_ok=True)
            
            return {
                "success": process.returncode == 0,
                "output": stdout,
                "stderr": stderr,
                "return_code": process.returncode,
                "error": stderr if process.returncode != 0 else None
            }
            
        except subprocess.TimeoutExpired:
            process.kill()
            temp_file.unlink(missing_ok=True)
            return {
                "success": False,
                "error": f"JavaScript execution timed out after {self.timeout} seconds",
                "output": "",
                "stderr": "",
                "return_code": -1
            }
        except Exception as e:
            return {
                "success": False,
                "error": f"JavaScript execution error: {str(e)}",
                "output": "",
                "stderr": "",
                "return_code": -1
            }

    def _execute_bash(self, code: str, stdin_input: str = None) -> Dict[str, Any]:
        """Execute Bash code (limited and safe commands only)"""
        try:
            # Create temporary script file
            exec_id = str(uuid.uuid4())
            temp_file = self.temp_dir / f"temp_{exec_id}.sh"
            
            with open(temp_file, 'w') as f:
                f.write('#!/bin/bash\nset -e\n')  # Exit on error
                f.write(code)
            
            # Make executable
            os.chmod(temp_file, 0o755)
            
            process = subprocess.Popen(
                ['bash', str(temp_file)],
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                cwd=self.temp_dir
            )
            
            stdout, stderr = process.communicate(
                input=stdin_input,
                timeout=self.timeout
            )
            
            # Cleanup
            temp_file.unlink(missing_ok=True)
            
            return {
                "success": process.returncode == 0,
                "output": stdout,
                "stderr": stderr,
                "return_code": process.returncode,
                "error": stderr if process.returncode != 0 else None
            }
            
        except subprocess.TimeoutExpired:
            process.kill()
            temp_file.unlink(missing_ok=True)
            return {
                "success": False,
                "error": f"Bash execution timed out after {self.timeout} seconds",
                "output": "",
                "stderr": "",
                "return_code": -1
            }
        except Exception as e:
            return {
                "success": False,
                "error": f"Bash execution error: {str(e)}",
                "output": "",
                "stderr": "",
                "return_code": -1
            }

    def validate_code(self, code: str, language: str) -> Dict[str, Any]:
        """Validate code without executing it"""
        result = {
            "valid": True,
            "warnings": [],
            "errors": [],
            "security_issues": []
        }
        
        # Check security violations
        security_violations = self._check_security_violations(code, language)
        if security_violations:
            result["security_issues"] = security_violations
            result["valid"] = False
        
        # Language-specific validation
        if language == 'python':
            try:
                compile(code, '<string>', 'exec')
            except SyntaxError as e:
                result["valid"] = False
                result["errors"].append(f"Syntax error: {str(e)}")
        
        # Check code length
        if len(code) > 50000:  # 50KB limit
            result["warnings"].append("Code is very long and may hit execution limits")
        
        return result