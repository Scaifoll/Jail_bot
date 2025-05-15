from .delete_ads import register_delete_ads_handlers
from .admin_menu import register_admin_handlers
from .report import register_report_handlers
from .help import register_help_handler
from .rules import register_rules_handler

def register_all_handlers(dp):
    """Регистрация всех обработчиков бота"""
    register_admin_handlers(dp) 
    register_delete_ads_handlers(dp) 
    register_report_handlers(dp) 
    register_help_handler(dp)
    register_rules_handler(dp)
    