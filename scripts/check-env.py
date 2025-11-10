#!/usr/bin/env python3
"""
Environment Variable Checker for Production Deployment

This script verifies that all required environment variables are set
before deploying to production.

Usage:
    python scripts/check-env.py
"""

import os
import sys
from typing import Dict, List, Tuple

# ANSI color codes
GREEN = '\033[92m'
RED = '\033[91m'
YELLOW = '\033[93m'
BLUE = '\033[94m'
RESET = '\033[0m'

def check_env_var(var_name: str, required: bool = True) -> Tuple[bool, str]:
    """Check if an environment variable is set."""
    value = os.getenv(var_name)
    
    if value:
        # Mask sensitive values
        if any(keyword in var_name.upper() for keyword in ['KEY', 'SECRET', 'PASSWORD', 'TOKEN']):
            masked = value[:4] + '*' * (len(value) - 8) + value[-4:] if len(value) > 8 else '***'
            return True, masked
        return True, value
    else:
        return False, 'NOT SET'

def main():
    """Main function to check all environment variables."""
    
    print(f"\n{BLUE}╔════════════════════════════════════════════════════════╗{RESET}")
    print(f"{BLUE}║   Production Environment Variables Checker            ║{RESET}")
    print(f"{BLUE}╚════════════════════════════════════════════════════════╝{RESET}\n")
    
    # Define required and optional variables
    required_vars = {
        'Core Configuration': [
            'ENV_MODE',
            'PYTHONPATH',
        ],
        'Supabase': [
            'SUPABASE_URL',
            'SUPABASE_ANON_KEY',
            'SUPABASE_SERVICE_ROLE_KEY',
            'SUPABASE_JWT_SECRET',
        ],
        'Redis': [
            'REDIS_HOST',
            'REDIS_PORT',
            'REDIS_PASSWORD',
        ],
        'LLM Providers (at least one)': [
            'ANTHROPIC_API_KEY',
            'OPENAI_API_KEY',
            'GROQ_API_KEY',
            'GEMINI_API_KEY',
        ],
        'Stripe': [
            'STRIPE_SECRET_KEY',
            'STRIPE_WEBHOOK_SECRET',
        ],
        'Frontend': [
            'FRONTEND_URL',
        ],
    }
    
    optional_vars = {
        'Observability': [
            'LANGFUSE_PUBLIC_KEY',
            'LANGFUSE_SECRET_KEY',
            'SENTRY_DSN',
        ],
        'Search & Tools': [
            'TAVILY_API_KEY',
            'EXA_API_KEY',
            'SERPER_API_KEY',
            'FIRECRAWL_API_KEY',
            'SEMANTIC_SCHOLAR_API_KEY',
        ],
        'Sandbox': [
            'DAYTONA_API_KEY',
            'DAYTONA_SERVER_URL',
        ],
        'Email': [
            'MAILTRAP_API_KEY',
        ],
        'Integrations': [
            'COMPOSIO_API_KEY',
            'VAPI_PRIVATE_KEY',
        ],
    }
    
    all_passed = True
    warnings = []
    
    # Check required variables
    print(f"{BLUE}Required Environment Variables:{RESET}\n")
    
    for category, vars_list in required_vars.items():
        print(f"{YELLOW}{category}:{RESET}")
        
        if category == 'LLM Providers (at least one)':
            # Special handling - at least one LLM provider needed
            llm_set = False
            for var in vars_list:
                is_set, value = check_env_var(var, required=False)
                if is_set:
                    llm_set = True
                    print(f"  {GREEN}✓{RESET} {var}: {value}")
                else:
                    print(f"  {YELLOW}○{RESET} {var}: {value}")
            
            if not llm_set:
                print(f"  {RED}✗ ERROR: At least one LLM API key must be set{RESET}")
                all_passed = False
        else:
            # Regular required variables
            for var in vars_list:
                is_set, value = check_env_var(var)
                if is_set:
                    print(f"  {GREEN}✓{RESET} {var}: {value}")
                else:
                    print(f"  {RED}✗{RESET} {var}: {value}")
                    all_passed = False
        print()
    
    # Check optional variables
    print(f"{BLUE}Optional Environment Variables:{RESET}\n")
    
    for category, vars_list in optional_vars.items():
        print(f"{YELLOW}{category}:{RESET}")
        
        category_set = False
        for var in vars_list:
            is_set, value = check_env_var(var, required=False)
            if is_set:
                print(f"  {GREEN}✓{RESET} {var}: {value}")
                category_set = True
            else:
                print(f"  {YELLOW}○{RESET} {var}: {value}")
        
        if not category_set:
            warnings.append(f"{category} not configured")
        print()
    
    # Special checks
    print(f"{BLUE}Configuration Checks:{RESET}\n")
    
    # Check ENV_MODE
    env_mode = os.getenv('ENV_MODE', '')
    if env_mode == 'production':
        print(f"  {GREEN}✓{RESET} ENV_MODE is set to 'production'")
    else:
        print(f"  {RED}✗{RESET} ENV_MODE is not 'production' (current: {env_mode})")
        all_passed = False
    
    # Check Redis SSL
    redis_ssl = os.getenv('REDIS_SSL', '')
    if redis_ssl.lower() in ['true', '1', 'yes']:
        print(f"  {GREEN}✓{RESET} REDIS_SSL is enabled")
    else:
        print(f"  {YELLOW}⚠{RESET} REDIS_SSL is not enabled (recommended for production)")
        warnings.append("Redis SSL not enabled")
    
    # Check PYTHONPATH
    pythonpath = os.getenv('PYTHONPATH', '')
    if '/var/task/backend' in pythonpath or '/app' in pythonpath:
        print(f"  {GREEN}✓{RESET} PYTHONPATH is configured correctly")
    else:
        print(f"  {YELLOW}⚠{RESET} PYTHONPATH may not be configured correctly (current: {pythonpath})")
        warnings.append("PYTHONPATH not set to expected value")
    
    print()
    
    # Summary
    print(f"{BLUE}╔════════════════════════════════════════════════════════╗{RESET}")
    print(f"{BLUE}║   Summary                                              ║{RESET}")
    print(f"{BLUE}╚════════════════════════════════════════════════════════╝{RESET}\n")
    
    if all_passed and not warnings:
        print(f"{GREEN}✓ All required environment variables are set!{RESET}")
        print(f"{GREEN}✓ Ready for production deployment.{RESET}\n")
        return 0
    
    if not all_passed:
        print(f"{RED}✗ Some required environment variables are missing.{RESET}")
        print(f"{RED}  Please set them before deploying to production.{RESET}\n")
    
    if warnings:
        print(f"{YELLOW}⚠ Warnings:{RESET}")
        for warning in warnings:
            print(f"  - {warning}")
        print()
    
    if all_passed:
        print(f"{YELLOW}⚠ Ready for deployment with warnings.{RESET}")
        print(f"{YELLOW}  Consider adding optional services for better functionality.{RESET}\n")
        return 0
    
    print(f"{RED}Please fix the errors above before deploying.{RESET}\n")
    return 1

if __name__ == '__main__':
    sys.exit(main())

