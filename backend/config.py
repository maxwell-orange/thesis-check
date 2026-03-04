"""
Configuration file for Thesis Check System
"""
import os
from dotenv import load_dotenv

load_dotenv()


class Config:
    """Base configuration"""
    # Flask
    SECRET_KEY = os.environ.get('SECRET_KEY', 'dev-secret-key')

    # Upload settings
    UPLOAD_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'uploads')
    MAX_CONTENT_LENGTH = 10 * 1024 * 1024  # 10MB max file size
    ALLOWED_EXTENSIONS = {'docx'}

    # CORS
    CORS_ORIGINS = ['http://localhost:5173', 'http://127.0.0.1:5173']

    # LLM Provider configurations
    LLM_PROVIDERS = {
        'zhipu': {
            'name': '智谱AI',
            'base_url': 'https://open.bigmodel.cn/api/paas/v4/',
            'models': ['glm-4', 'glm-4-flash', 'glm-4-plus'],
            'default_model': 'glm-4-flash'
        },
        'kimi': {
            'name': 'Kimi',
            'base_url': 'https://api.moonshot.cn/v1',
            'models': ['moonshot-v1-8k', 'moonshot-v1-32k', 'moonshot-v1-128k'],
            'default_model': 'moonshot-v1-8k'
        },
        'deepseek': {
            'name': 'DeepSeek',
            'base_url': 'https://api.deepseek.com/v1',
            'models': ['deepseek-chat', 'deepseek-reasoner'],
            'default_model': 'deepseek-chat'
        },
        'doubao': {
            'name': '豆包',
            'base_url': 'https://ark.cn-beijing.volces.com/api/v3',
            'models': ['doubao-pro-32k', 'doubao-lite-32k'],
            'default_model': 'doubao-lite-32k'
        }
    }

    # Format check rules for Shandong University of Finance and Economics
    FORMAT_RULES = {
        'page': {
            'paper_size': 'A4',
            'orientation': 'portrait',
            'margin_top': 2.5,  # cm
            'margin_bottom': 2.0,  # cm
            'margin_inner': 2.5,  # cm
            'margin_outer': 2.0,  # cm
        },
        'chapter_title': {
            'font_name': '黑体',
            'font_size': 16,  # 三号 ≈ 16pt
            'bold': True,
            'alignment': 'center',
            'space_before': 0.5,  # lines
            'space_after': 0.5,  # lines
        },
        'section_title': {
            'font_name': '黑体',
            'font_size': 14,  # 四号 ≈ 14pt
            'bold': True,
            'alignment': 'left',
            'space_before': 0.5,
            'space_after': 0.5,
        },
        'subsection_title': {
            'font_name': '黑体',
            'font_size': 12,  # 小四 ≈ 12pt
            'bold': True,
            'alignment': 'left',
            'first_line_indent': 2,  # characters
            'space_before': 0.5,
            'space_after': 0.5,
        },
        'body_text': {
            'font_name_cn': '宋体',
            'font_name_en': 'Times New Roman',
            'font_size': 12,  # 小四
            'bold': False,
            'alignment': 'justify',
            'first_line_indent': 2,  # characters
            'line_spacing': 1.5,
        },
        'figure_title': {
            'font_name': '宋体',
            'font_size': 10.5,  # 五号
            'bold': True,
            'position': 'below',  # 图下
        },
        'table_title': {
            'font_name': '宋体',
            'font_size': 10.5,  # 五号
            'bold': True,
            'position': 'above',  # 表上
        },
        'abstract': {
            'font_name': '宋体',
            'font_size': 12,
            'min_length': 250,  # 中文摘要最少字数
            'max_length': 350,  # 中文摘要最多字数
        },
        'references': {
            'min_count': 10,
            'recent_years_ratio': 0.3,  # 近三年比例
            'standard': 'GB/T 7714',
        }
    }


# Create upload directory if it doesn't exist
os.makedirs(Config.UPLOAD_FOLDER, exist_ok=True)