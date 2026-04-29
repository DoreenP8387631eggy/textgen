#!/usr/bin/env python3
"""
Main entry point for the textgen web UI server.
Fork of oobabooga/text-generation-webui with additional features.
"""

import os
import sys
import time
import signal
import logging
import argparse
from pathlib import Path

# Configure logging before other imports
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)

# Ensure project root is in path
ROOT_DIR = Path(__file__).parent.resolve()
sys.path.insert(0, str(ROOT_DIR))


def parse_arguments():
    """Parse command-line arguments for the server."""
    parser = argparse.ArgumentParser(
        description='textgen - Text Generation Web UI',
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )

    # Server settings
    parser.add_argument('--host', type=str, default='127.0.0.1',
                        help='Host address to bind the server to')
    parser.add_argument('--port', type=int, default=7860,
                        help='Port number for the web UI')
    parser.add_argument('--share', action='store_true',
                        help='Create a public Gradio share link')
    parser.add_argument('--listen', action='store_true',
                        help='Listen on all network interfaces (0.0.0.0)')

    # Model settings
    parser.add_argument('--model', type=str, default=None,
                        help='Name of the model to load at startup')
    # Changed default model dir to 'local_models' to keep my downloaded models
    # separate from anything tracked by git
    parser.add_argument('--model-dir', type=str, default='local_models',
                        help='Directory containing model files')
    parser.add_argument('--lora', type=str, nargs='+', default=None,
                        help='LoRA adapter(s) to apply to the model')

    # Generation settings
    # Bumped default from 512 -> 1024; I kept running into truncated outputs
    parser.add_argument('--max-new-tokens', type=int, default=1024,
                        help='Maximum number of new tokens to generate')
    # Using a fixed seed by default so results are reproducible during testing;
    # set to -1 to restore random behavior
    parser.add_argument('--seed', type=int, default=42,
                        help='Random seed (-1 for random)')

    # Hardware settings
    parser.add_argument('--cpu', action='store_true',
                        help='Force CPU-only inference')
    parser.add_argument('--gpu-memory', type=int, nargs='+', default=None,
                        help='GPU VRAM limit in GiB per device')
    parser.add_argument('--cpu-memory', type=int, default=None,
                        help='CPU RAM limit in GiB')
    parser.add_argument('--load-in-8bit', action='store_true',
                        help='Load model in 8-bit quantization')
    parser.add_argument('--load-in-4bit', action='store_true',
                        help='Load model in 4-bit quantization')

    # API settings
    parser.add_argument('--api', action='store_true',
                  