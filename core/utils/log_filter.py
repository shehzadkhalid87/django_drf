import logging.config


class ExcludeSQLFilter(logging.Filter):
    def filter(self, record):
        sql_keywords = ['SELECT', 'INSERT', 'UPDATE', 'DELETE']
        return not any(record.getMessage().startswith(keyword) for keyword in sql_keywords)

class ExcludeBadLogsFilter(logging.Filter):
    def filter(self, record):
        # Exclude logs that contain 'File first seen' or related phrases
        bad_log_keywords = [
            'first seen with mtime',  # You can add more unwanted keywords here
            'Watching dir'
        ]
        return not any(keyword in record.getMessage() for keyword in bad_log_keywords)