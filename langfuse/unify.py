# unify.py
# Main script that uses the various modules to perform operations with Langfuse.
import importlib
import sys
# del sys.modules['openai']
# sys.modules['openai'] = __import__('langfuse.openai', fromlist=[None]).openai

if importlib.util.find_spec('langfuse.openai') is not None:
    openai = __import__('langfuse.openai', fromlist=[None]).openai
    sys.modules['openai'] = openai

import unify
