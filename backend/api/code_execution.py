from fastapi import APIRouter, HTTPException
from typing import Optional
from services.code_executor import CodeExecutor
import logging

router = APIRouter()
logger = logging.getLogger(__name__)

# Initialize code executor
code_executor = CodeExecutor()

@router.get("/languages")
async def get_supported_languages():
    """Get list of supported programming languages"""
    languages = code_executor.get_supported_languages()
    availability = {}
    
    for lang in languages:
        availability[lang] = {
            "available": code_executor.is_language_available(lang),
            "runtime_check": "passed" if code_executor.is_language_available(lang) else "failed"
        }
    
    return {
        "supported_languages": languages,
        "availability": availability,
        "executor_config": {
            "timeout_seconds": code_executor.timeout,
            "max_output_length": code_executor.max_output_length
        }
    }

@router.post("/execute")
async def execute_code(request: dict):
    """Execute code safely and return results"""
    try:
        code = request.get('code', '')
        language = request.get('language', 'python')
        stdin_input = request.get('stdin', None)
        
        if not code.strip():
            raise HTTPException(status_code=400, detail="No code provided")
        
        if language not in code_executor.get_supported_languages():
            raise HTTPException(
                status_code=400, 
                detail=f"Unsupported language: {language}. Supported: {code_executor.get_supported_languages()}"
            )
        
        # Execute the code
        result = code_executor.execute_code(code, language, stdin_input)
        
        return {
            "execution_result": result,
            "request_info": {
                "language": language,
                "code_length": len(code),
                "has_stdin": stdin_input is not None
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Code execution error: {e}")
        raise HTTPException(status_code=500, detail=f"Execution error: {str(e)}")

@router.post("/validate")
async def validate_code(request: dict):
    """Validate code without executing it"""
    try:
        code = request.get('code', '')
        language = request.get('language', 'python')
        
        if not code.strip():
            raise HTTPException(status_code=400, detail="No code provided")
        
        if language not in code_executor.get_supported_languages():
            raise HTTPException(
                status_code=400,
                detail=f"Unsupported language: {language}. Supported: {code_executor.get_supported_languages()}"
            )
        
        # Validate the code
        validation_result = code_executor.validate_code(code, language)
        
        return {
            "validation": validation_result,
            "request_info": {
                "language": language,
                "code_length": len(code)
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Code validation error: {e}")
        raise HTTPException(status_code=500, detail=f"Validation error: {str(e)}")

@router.get("/status")
async def get_executor_status():
    """Get status of code execution service"""
    languages = code_executor.get_supported_languages()
    status = {
        "service_available": True,
        "supported_languages": {},
        "configuration": {
            "timeout_seconds": code_executor.timeout,
            "max_output_length": code_executor.max_output_length,
            "temp_directory": str(code_executor.temp_dir)
        }
    }
    
    # Check availability of each language
    for lang in languages:
        try:
            available = code_executor.is_language_available(lang)
            status["supported_languages"][lang] = {
                "available": available,
                "status": "ready" if available else "runtime_not_found"
            }
        except Exception as e:
            status["supported_languages"][lang] = {
                "available": False,
                "status": f"error: {str(e)}"
            }
    
    return status