#!/usr/bin/env python3
"""
Test script to verify logging configuration
"""

import sys
import logging
from pathlib import Path

# Configure logging
Path("logs").mkdir(exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stderr),
        logging.FileHandler('logs/test_logging.log', mode='a')
    ],
    force=True
)

logger = logging.getLogger("TestLogger")

def test_logging():
    """Test all logging levels"""
    print("🧪 Testing logging configuration...")
    
    logger.debug("This is a DEBUG message")
    logger.info("This is an INFO message") 
    logger.warning("This is a WARNING message")
    logger.error("This is an ERROR message")
    
    print("✅ Logging test completed")
    print("📄 Check logs/test_logging.log for file output")
    print("🖥️ Terminal output should appear above")

if __name__ == "__main__":
    test_logging() 