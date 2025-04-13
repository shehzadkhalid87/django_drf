from core.utils.log_filter import ExcludeBadLogsFilter, ExcludeSQLFilter

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'filters': {
        'exclude_sql': {
            '()': ExcludeSQLFilter,
        },
        'exclude_bad_logs': {
            '()': ExcludeBadLogsFilter,  # New filter for bad logs
        },
    },
    'formatters': {
        'verbose': {
            'format': '{levelname} {asctime} {module} {message}',
            'style': '{',
        },
        'simple': {
            'format': '{levelname} {message}',
            'style': '{',
        },
    },
    'handlers': {
        'console': {
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',
            'formatter': 'simple',
            'filters': ['exclude_sql', 'exclude_bad_logs'],
        },
        'file': {
            'level': 'DEBUG',
            'class': 'logging.FileHandler',
            'filename': 'django_debug.log',
            'formatter': 'verbose',
            'filters': ['exclude_sql', 'exclude_bad_logs'],  # Apply both filters here too
        },
        'file_sql': {
            'level': 'DEBUG',
            'class': 'logging.FileHandler',
            'filename': 'sql_queries.log',
            'formatter': 'verbose',
        },
    },
    'root': {
        'handlers': ['console'],  # Default to console only
        'level': 'DEBUG',
    },
    'loggers': {
        'django': {
            'handlers': ['console'],  # Default to console only
            'level': 'DEBUG',
            'propagate': True,
        },
        'django.db.backends': {
            'handlers': [],  # No SQL logging by default
            'level': 'DEBUG',
            'propagate': False,
        },
    },
}
