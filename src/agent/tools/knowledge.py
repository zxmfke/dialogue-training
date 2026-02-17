"""
知识库工具 - 读取和管理医院话术文档
"""

import os
import re
from pathlib import Path
from typing import Dict, List, Optional
import json


class KnowledgeTool:
    """知识库管理工具"""
    
    def __init__(self, config: dict):
        self.knowledge_path = Path(config['path'])
        self.auto_sync = config.get('auto_sync', True)
        self.cache = {}
        
        # 初始化时加载知识库
        if self.auto_sync:
            self.sync()
    
    def sync(self) -> str:
        """
        同步知识库，扫描并解析所有文档
        
        Returns:
            同步结果摘要
        """
        if not self.knowledge_path.exists():
            return f"知识库路径不存在: {self.knowledge_path}"
        
        loaded_projects = []
        
        # 扫描知识库目录
        for file_path in self.knowledge_path.rglob('*'):
            if file_path.is_file():
                project_name = self._extract_project_name(file_path)
                
                if file_path.suffix.lower() == '.pdf':
                    content = self._parse_pdf(file_path)
                elif file_path.suffix.lower() in ['.docx', '.doc']:
                    content = self._parse_docx(file_path)
                elif file_path.suffix.lower() == '.md':
                    content = self._parse_markdown(file_path)
                elif file_path.suffix.lower() == '.txt':
                    content = self._parse_text(file_path)
                else:
                    continue
                
                # 解析结构化信息
                knowledge = self._extract_knowledge(content, project_name)
                self.cache[project_name] = knowledge
                loaded_projects.append(project_name)
        
        return f"知识库同步完成，已加载 {len(loaded_projects)} 个项目: {', '.join(loaded_projects)}"
    
    def get_project_knowledge(self, project_name: str) -> dict:
        """
        获取指定项目的知识
        
        Args:
            project_name: 项目名称
            
        Returns:
            项目知识字典
        """
        # 模糊匹配
        for name, knowledge in self.cache.items():
            if project_name in name or name in project_name:
                return knowledge
        
        # 返回默认知识
        return self._get_default_knowledge(project_name)
    
    def search_faq(self, query: str, top_k: int = 3) -> List[dict]:
        """
        搜索 FAQ
        
        Args:
            query: 搜索关键词
            top_k: 返回结果数量
            
        Returns:
            FAQ 列表
        """
        results = []
        
        for project_name, knowledge in self.cache.items():
            for faq in knowledge.get('faq', []):
                if query in faq['question'] or query in faq['answer']:
                    results.append({
                        'project': project_name,
                        'question': faq['question'],
                        'answer': faq['answer']
                    })
        
        return results[:top_k]
    
    def get_objection_handling(self, objection_type: str) -> List[dict]:
        """
        获取异议处理话术
        
        Args:
            objection_type: 异议类型，如"价格","效果","安全"
            
        Returns:
            应对话术列表
        """
        results = []
        
        for knowledge in self.cache.values():
            for obj in knowledge.get('objections', []):
                if objection_type in obj['type']:
                    results.append(obj)
        
        return results
    
    def _extract_project_name(self, file_path: Path) -> str:
        """从文件名提取项目名"""
        # 移除扩展名和常见后缀
        name = file_path.stem
        name = re.sub(r'(手册|指南|话术|v\d+|\d+)', '', name)
        return name.strip()
    
    def _parse_pdf(self, file_path: Path) -> str:
        """解析 PDF 文件"""
        try:
            import PyPDF2
            text = ""
            with open(file_path, 'rb') as f:
                reader = PyPDF2.PdfReader(f)
                for page in reader.pages:
                    text += page.extract_text() + "\n"
            return text
        except ImportError:
            return f"[PDF解析需要PyPDF2] {file_path}"
    
    def _parse_docx(self, file_path: Path) -> str:
        """解析 Word 文件"""
        try:
            from docx import Document
            doc = Document(file_path)
            return "\n".join([para.text for para in doc.paragraphs])
        except ImportError:
            return f"[Word解析需要python-docx] {file_path}"
    
    def _parse_markdown(self, file_path: Path) -> str:
        """解析 Markdown 文件"""
        with open(file_path, 'r', encoding='utf-8') as f:
            return f.read()
    
    def _parse_text(self, file_path: Path) -> str:
        """解析文本文件"""
        with open(file_path, 'r', encoding='utf-8') as f:
            return f.read()
    
    def _extract_knowledge(self, content: str, project_name: str) -> dict:
        """从文本中提取结构化知识"""
        knowledge = {
            'name': project_name,
            'raw_content': content,
            'introduction': '',
            'indications': [],
            'contraindications': [],
            'price_range': '',
            'duration': '',
            'faq': [],
            'objections': [],
            'key_points': []
        }
        
        # 使用简单规则提取，实际可用 NLP
        lines = content.split('\n')
        current_section = None
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
            
            # 识别章节
            if '介绍' in line or '简介' in line:
                current_section = 'introduction'
            elif '适应症' in line or '适合人群' in line:
                current_section = 'indications'
            elif '禁忌' in line:
                current_section = 'contraindications'
            elif '价格' in line or '费用' in line:
                current_section = 'price'
            elif '维持' in line or '效果' in line:
                current_section = 'duration'
            elif 'FAQ' in line or '常见问题' in line:
                current_section = 'faq'
            elif '异议' in line:
                current_section = 'objections'
            elif '要点' in line or '重点' in line:
                current_section = 'key_points'
            else:
                # 收集内容
                if current_section == 'introduction':
                    knowledge['introduction'] += line + ' '
                elif current_section == 'indications':
                    if line.startswith(('•', '-', '*', '1.', '2.')):
                        knowledge['indications'].append(line.lstrip('•-*0123456789. '))
                elif current_section == 'contraindications':
                    if line.startswith(('•', '-', '*', '1.', '2.')):
                        knowledge['contraindications'].append(line.lstrip('•-*0123456789. '))
                elif current_section == 'price':
                    knowledge['price_range'] += line + ' '
                elif current_section == 'duration':
                    knowledge['duration'] += line + ' '
                elif current_section == 'faq':
                    # 简单解析 Q&A
                    if '？' in line or '?' in line:
                        knowledge['faq'].append({'question': line, 'answer': ''})
                    elif knowledge['faq']:
                        knowledge['faq'][-1]['answer'] += line + ' '
                elif current_section == 'objections':
                    # 解析异议类型和应对
                    if '：' in line or ':' in line:
                        parts = line.split('：', 1) if '：' in line else line.split(':', 1)
                        knowledge['objections'].append({
                            'type': parts[0].strip(),
                            'response': parts[1].strip() if len(parts) > 1 else ''
                        })
                elif current_section == 'key_points':
                    if line.startswith(('•', '-', '*')):
                        knowledge['key_points'].append(line.lstrip('•-* '))
        
        return knowledge
    
    def _get_default_knowledge(self, project_name: str) -> dict:
        """获取默认知识（当知识库中不存在时）"""
        return {
            'name': project_name,
            'introduction': f'{project_name}是本院热门项目，深受顾客好评。',
            'indications': ['有改善需求的顾客'],
            'contraindications': ['孕妇', '严重过敏体质'],
            'price_range': '价格根据方案不同有所差异',
            'duration': '效果维持时间因人而异',
            'faq': [
                {'question': f'{project_name}安全吗？', 'answer': '本院使用的都是经过认证的产品，由经验丰富的医生操作，安全性有保障。'}
            ],
            'objections': [
                {'type': '价格', 'response': '我们提供多种方案，可以根据您的预算来推荐最适合的。'},
                {'type': '效果', 'response': '根据顾客反馈，满意度很高，我们也可以看看案例效果。'}
            ],
            'key_points': ['强调安全性', '展示案例', '了解需求']
        }
