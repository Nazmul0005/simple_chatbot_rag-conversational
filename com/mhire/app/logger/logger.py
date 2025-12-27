from datetime import datetime
import logging
import logging.handlers
from pathlib import Path
from typing import Optional


class LoggerFactory:
    """Centralized logger factory to eliminate redundant code"""
    
    @staticmethod
    def setup_logger(
        logger_name: str,
        log_subdir: str,
        log_file_prefix: str,
        max_bytes: int = 10 * 1024 * 1024,
        backup_count: int = 5
    ) -> logging.Logger:
        """
        Configure and return a logger with file and console handlers
        
        Args:
            logger_name: Name of the logger (e.g., "ChatService")
            log_subdir: Subdirectory under logs/ (e.g., "chat")
            log_file_prefix: Prefix for log file (e.g., "chat")
            max_bytes: Maximum size of log file before rotation
            backup_count: Number of backup files to keep
            
        Returns:
            Configured logger instance
        """
        logs_dir = Path(f"logs/{log_subdir}")
        logs_dir.mkdir(parents=True, exist_ok=True)
        
        logger = logging.getLogger(logger_name)
        logger.setLevel(logging.DEBUG)
        
        # Return existing logger if already configured
        if logger.handlers:
            return logger
        
        # File handler (rotating)
        log_file = logs_dir / f"{log_file_prefix}_{datetime.now().strftime('%Y%m%d')}.log"
        file_handler = logging.handlers.RotatingFileHandler(
            log_file, 
            maxBytes=max_bytes, 
            backupCount=backup_count, 
            encoding='utf-8'
        )
        file_handler.setLevel(logging.DEBUG)
        
        # Console handler - only ERROR
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.ERROR)
        
        # Formatter
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - [%(funcName)s:%(lineno)d] - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        file_handler.setFormatter(formatter)
        console_handler.setFormatter(formatter)
        
        logger.addHandler(file_handler)
        logger.addHandler(console_handler)
        
        return logger


# Convenience classes for backward compatibility
class ChatEndpoint:
    @staticmethod
    def setup_chat_logger():
        return LoggerFactory.setup_logger("ChatService", "chat", "chat")
    
    @staticmethod
    def setup_schema_logger():
        return LoggerFactory.setup_logger("ChatSchema", "chat", "chat")
    
    @staticmethod
    def setup_router_logger():
        return LoggerFactory.setup_logger("ChatRouter", "chat", "chat")


class SessionTitleEndpoint:
    @staticmethod
    def setup_session_title_logger():
        return LoggerFactory.setup_logger("SessionTitleService", "session_title", "session_title")
    
    @staticmethod
    def setup_session_title_schema_logger():
        return LoggerFactory.setup_logger("SessionTitleSchema", "session_title", "session_title")
    
    @staticmethod
    def setup_session_title_router_logger():
        return LoggerFactory.setup_logger("SessionTitleRouter", "session_title", "session_title")


# class ChatStreamEndpoint:
#     @staticmethod
#     def setup_chat_stream_logger():
#         return LoggerFactory.setup_logger("ChatStreamService", "chat_stream", "chat_stream")
    
#     @staticmethod
#     def setup_stream_schema_logger():
#         return LoggerFactory.setup_logger("ChatStreamSchema", "chat_stream", "chat_stream")
    
#     @staticmethod
#     def setup_stream_router_logger():
#         return LoggerFactory.setup_logger("ChatStreamRouter", "chat_stream", "chat_stream")


# class ConversationEndpoint:
#     @staticmethod
#     def setup_conversation_logger():
#         return LoggerFactory.setup_logger("ConversationService", "conversation", "conversation")
    
#     @staticmethod
#     def setup_conversation_schema_logger():
#         return LoggerFactory.setup_logger("ConversationSchema", "conversation", "conversation")
    
#     @staticmethod
#     def setup_conversation_router_logger():
#         return LoggerFactory.setup_logger("ConversationRouter", "conversation", "conversation")


# class SessionEndpoint:
#     @staticmethod
#     def setup_session_logger():
#         return LoggerFactory.setup_logger("SessionService", "session", "session")
    
#     @staticmethod
#     def setup_session_schema_logger():
#         return LoggerFactory.setup_logger("SessionSchema", "session", "session")
    
#     @staticmethod
#     def setup_session_router_logger():
#         return LoggerFactory.setup_logger("SessionRouter", "session", "session")


# class HistoryDeleteEndpoint:
#     @staticmethod
#     def setup_history_delete_logger():
#         return LoggerFactory.setup_logger("HistoryDeleteService", "history_delete", "history_delete")
    
#     @staticmethod
#     def setup_history_delete_schema_logger():
#         return LoggerFactory.setup_logger("HistoryDeleteSchema", "history_delete", "history_delete")
    
#     @staticmethod
#     def setup_history_delete_router_logger():
#         return LoggerFactory.setup_logger("HistoryDeleteRouter", "history_delete", "history_delete")


# class HistoryGetEndpoint:
#     @staticmethod
#     def setup_history_get_logger():
#         return LoggerFactory.setup_logger("HistoryGetService", "history_get", "history_get")
    
#     @staticmethod
#     def setup_history_get_schema_logger():
#         return LoggerFactory.setup_logger("HistoryGetSchema", "history_get", "history_get")
    
#     @staticmethod
#     def setup_history_get_router_logger():
#         return LoggerFactory.setup_logger("HistoryGetRouter", "history_get", "history_get")
    
# class SessionRenameEndpoint:
#     @staticmethod
#     def setup_session_rename_logger():
#         return LoggerFactory.setup_logger("SessionRenameService", "session_rename", "session_rename")
    
#     @staticmethod
#     def setup_session_rename_schema_logger():
#         return LoggerFactory.setup_logger("SessionRenameSchema", "session_rename", "session_rename")
    
#     @staticmethod
#     def setup_session_rename_router_logger():
#         return LoggerFactory.setup_logger("SessionRenameRouter", "session_rename", "session_rename")


# class DatabaseManager:
#     @staticmethod
#     def setup_logger():
#         return LoggerFactory.setup_logger("DatabaseManager", "database", "database")