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
    parser.add_argument('--model-dir', type=str, default='models',
                        help='Directory containing model files')
    parser.add_argument('--lora', type=str, nargs='+', default=None,
                        help='LoRA adapter(s) to apply to the model')

    # Generation settings
    parser.add_argument('--max-new-tokens', type=int, default=512,
                        help='Maximum number of new tokens to generate')
    parser.add_argument('--seed', type=int, default=-1,
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
                        help='Enable the REST API')
    parser.add_argument('--api-port', type=int, default=5000,
                        help='Port for the REST API server')
    parser.add_argument('--api-key', type=str, default='',
                        help='API key for authentication (empty = no auth)')

    # Debug / dev
    parser.add_argument('--debug', action='store_true',
                        help='Enable debug logging')
    parser.add_argument('--verbose', action='store_true',
                        help='Enable verbose output')

    return parser.parse_args()


def setup_environment(args):
    """Configure environment variables based on parsed arguments."""
    if args.cpu:
        os.environ['CUDA_VISIBLE_DEVICES'] = ''
        logger.info('CPU-only mode enabled — CUDA disabled')

    if args.debug:
        logging.getLogger().setLevel(logging.DEBUG)
        logger.debug('Debug logging enabled')

    # Ensure required directories exist
    for directory in ['models', 'loras', 'prompts', 'presets', 'logs']:
        Path(ROOT_DIR / directory).mkdir(parents=True, exist_ok=True)


def handle_shutdown(signum, frame):
    """Graceful shutdown handler for SIGINT / SIGTERM."""
    logger.info('Shutdown signal received — stopping server...')
    sys.exit(0)


def main():
    """Main entry point."""
    args = parse_arguments()
    setup_environment(args)

    signal.signal(signal.SIGINT, handle_shutdown)
    signal.signal(signal.SIGTERM, handle_shutdown)

    host = '0.0.0.0' if args.listen else args.host

    logger.info('Starting textgen server on %s:%d', host, args.port)
    logger.info('Model directory: %s', Path(ROOT_DIR / args.model_dir).resolve())

    if args.model:
        logger.info('Loading model at startup: %s', args.model)

    # Lazy import heavy dependencies so --help is fast
    try:
        import modules.ui as ui
        ui.launch(
            host=host,
            port=args.port,
            share=args.share,
            args=args,
        )
    except ImportError:
        logger.error(
            'UI modules not found. Please ensure all dependencies are installed.\n'
            'Run: pip install -r requirements.txt'
        )
        sys.exit(1)


if __name__ == '__main__':
    main()
