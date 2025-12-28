"""
Checkpoint management.

Tracks which CSV rows have been processed to avoid reprocessing data.
"""
import json
from datetime import datetime
from pathlib import Path
from src.utils.logger import get_logger
from src.utils.config import Config


def get_checkpoint_file_path() -> Path:
    """Get the checkpoint file path."""
    config = Config()
    checkpoint_path = config.get_checkpoint_file_path()
    return Path(checkpoint_path)


def read_checkpoint() -> int:
    """Read the last processed line number from checkpoint file."""
    logger = get_logger('ingestion.checkpoint', log_file_path=Config().get_log_file_path())
    checkpoint_path = get_checkpoint_file_path()
    
    if not checkpoint_path.exists():
        logger.info(f"Checkpoint file not found. Starting from beginning")
        return 0
    
    try:
        with open(checkpoint_path, 'r', encoding='utf-8') as f:
            checkpoint_data = json.load(f)
        
        last_processed_line = checkpoint_data.get('last_processed_line', 0)
        
        # Validate the line number
        if not isinstance(last_processed_line, int) or last_processed_line < 0:
            logger.warning(f"Invalid checkpoint data. Resetting to 0")
            return 0
        
        logger.info(f"Read checkpoint: line {last_processed_line}")
        return last_processed_line
    
    except json.JSONDecodeError as e:
        logger.warning(f"Checkpoint file corrupted: {str(e)}. Resetting to 0")
        return 0
    except Exception as e:
        logger.error(f"Error reading checkpoint: {str(e)}. Resetting to 0")
        return 0


def write_checkpoint(last_processed_line: int) -> None:
    """Save the last processed line number to checkpoint file."""
    if last_processed_line < 0:
        raise ValueError(f"Line number must be non-negative, got {last_processed_line}")
    
    logger = get_logger('ingestion.checkpoint', log_file_path=Config().get_log_file_path())
    checkpoint_path = get_checkpoint_file_path()
    
    # Make sure directory exists
    checkpoint_path.parent.mkdir(parents=True, exist_ok=True)
    
    checkpoint_data = {
        'last_processed_line': last_processed_line,
        'last_updated': datetime.utcnow().isoformat() + 'Z'
    }
    
    try:
        # Write to temp file first, then rename (atomic operation)
        temp_path = checkpoint_path.with_suffix('.tmp')
        with open(temp_path, 'w', encoding='utf-8') as f:
            json.dump(checkpoint_data, f, indent=2)
        
        temp_path.replace(checkpoint_path)
        logger.info(f"Checkpoint updated: line {last_processed_line}")
    
    except Exception as e:
        logger.error(f"Error writing checkpoint: {str(e)}")
        raise


def reset_checkpoint() -> None:
    """Reset checkpoint to start from the beginning."""
    logger = get_logger('ingestion.checkpoint', log_file_path=Config().get_log_file_path())
    checkpoint_path = get_checkpoint_file_path()
    
    try:
        if checkpoint_path.exists():
            checkpoint_path.unlink()
            logger.info(f"Checkpoint reset: deleted {checkpoint_path}")
        else:
            logger.info("Checkpoint reset: file does not exist")
    except Exception as e:
        logger.error(f"Error resetting checkpoint: {str(e)}")
        raise

