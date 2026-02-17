"""
话术教练 Agent - 核心逻辑
基于 OpenClaw Agent 架构
"""

import json
import yaml
from typing import List, Dict, Optional
from datetime import datetime
from pathlib import Path

from .tools.knowledge import KnowledgeTool
from .tools.evaluation import EvaluationTool
from .tools.scenario import ScenarioTool
from .tools.notification import NotificationTool


class DialogueCoachAgent:
    """医院咨询师话术陪练 Agent"""
    
    def __init__(self, config_path: str = "config/agent.yaml"):
        with open(config_path, 'r', encoding='utf-8') as f:
            self.config = yaml.safe_load(f)
        
        # 初始化工具
        self.knowledge_tool = KnowledgeTool(self.config['knowledge_base'])
        self.evaluation_tool = EvaluationTool(self.config['evaluation'])
        self.scenario_tool = ScenarioTool()
        self.notification_tool = NotificationTool(self.config['channels'])
        
        # 会话管理
        self.active_sessions: Dict[str, dict] = {}
    
    def process_message(self, user_id: str, message: str, channel: str = "wecom") -> str:
        """
        处理用户消息，主入口
        
        Args:
            user_id: 用户唯一标识
            message: 用户发送的消息
            channel: 通信渠道
            
        Returns:
            Agent 回复
        """
        # 意图识别
        intent = self._recognize_intent(message)
        
        # 根据意图路由到不同处理逻辑
        if intent == "start_training":
            return self._handle_start_training(user_id, message)
        
        elif intent == "continue_dialogue":
            return self._handle_continue_dialogue(user_id, message)
        
        elif intent == "view_report":
            return self._handle_view_report(user_id)
        
        elif intent == "view_team_data":
            return self._handle_view_team_data(user_id)
        
        elif intent == "help":
            return self._handle_help()
        
        else:
            # 默认进入训练流程
            return self._handle_start_training(user_id, message)
    
    def _recognize_intent(self, message: str) -> str:
        """识别用户意图"""
        message = message.lower().strip()
        
        # 开始训练相关
        training_keywords = ["练习", "训练", "开始", "练", "想学", "陪练", "roleplay"]
        if any(kw in message for kw in training_keywords):
            return "start_training"
        
        # 查看报告
        report_keywords = ["报告", "成绩", "得分", "练得怎么样", "数据", "统计"]
        if any(kw in message for kw in report_keywords):
            return "view_report"
        
        # 查看团队数据
        team_keywords = ["团队", "科室", "大家", "整体", "所有人"]
        if any(kw in message for kw in team_keywords):
            return "view_team_data"
        
        # 帮助
        help_keywords = ["帮助", "怎么用", "help", "?", "？"]
        if any(kw in message for kw in help_keywords):
            return "help"
        
        # 检查是否有活跃会话
        # 如果有，认为是继续对话
        return "continue_dialogue"
    
    def _handle_start_training(self, user_id: str, message: str) -> str:
        """处理开始训练请求"""
        # 提取项目/场景
        project = self._extract_project(message)
        
        # 获取用户档案
        user_profile = self._get_user_profile(user_id)
        
        # 如果没有指定项目，根据薄弱点推荐
        if not project:
            project = user_profile.get('weak_area', '玻尿酸项目介绍')
        
        # 读取知识库
        knowledge = self.knowledge_tool.get_project_knowledge(project)
        
        # 生成场景
        scenario = self.scenario_tool.generate(
            project=project,
            user_weakness=user_profile.get('weaknesses', []),
            difficulty=user_profile.get('level', 'medium')
        )
        
        # 创建新会话
        session_id = f"{user_id}_{datetime.now().strftime('%Y%m%d%H%M%S')}"
        self.active_sessions[user_id] = {
            'session_id': session_id,
            'project': project,
            'scenario': scenario,
            'dialogue_history': [],
            'start_time': datetime.now(),
            'turn_count': 0
        }
        
        # 构建开场白
        response = f"""好的！为你准备【{project}】训练场景

👤 患者角色：
姓名：{scenario['patient']['name']}
年龄：{scenario['patient']['age']}岁
{type_text(scenario['patient']['type'])}：{scenario['patient']['concern']}
性格：{scenario['patient']['personality']}

💬 患者说：
"{scenario['opening']}"

请输入你的回复 👇"""
        
        return response
    
    def _handle_continue_dialogue(self, user_id: str, message: str) -> str:
        """处理对话继续"""
        session = self.active_sessions.get(user_id)
        
        if not session:
            # 没有活跃会话，引导开始训练
            return "请先告诉我你想练习什么项目？比如：\n• 我想练习玻尿酸\n• 练习超声炮\n• 练习种植牙"
        
        # 记录用户回复
        session['dialogue_history'].append({
            'role': 'consultant',
            'content': message,
            'timestamp': datetime.now().isoformat()
        })
        session['turn_count'] += 1
        
        # 检查是否结束（用户主动结束或达到最大轮数）
        if message in ['结束', 'finish', 'done'] or session['turn_count'] >= 8:
            return self._handle_end_dialogue(user_id)
        
        # AI 患者回应
        patient_response = self._generate_patient_response(session, message)
        session['dialogue_history'].append({
            'role': 'patient',
            'content': patient_response,
            'timestamp': datetime.now().isoformat()
        })
        
        # 检查是否自然结束（患者表达意向或拒绝）
        if self._is_dialogue_end(patient_response):
            return self._handle_end_dialogue(user_id)
        
        return f"患者说：\"{patient_response}\"\n\n你怎么回应？（回复'结束'可查看评估报告）"
    
    def _handle_end_dialogue(self, user_id: str) -> str:
        """处理对话结束，生成评估报告"""
        session = self.active_sessions.get(user_id)
        if not session:
            return "没有找到训练记录"
        
        # 评估对话
        evaluation = self.evaluation_tool.evaluate(
            dialogue_history=session['dialogue_history'],
            project=session['project'],
            sensitive_words=self.config['sensitive_words']
        )
        
        # 保存训练记录
        self._save_training_record(user_id, session, evaluation)
        
        # 清理会话
        del self.active_sessions[user_id]
        
        # 构建报告
        report = self._build_evaluation_report(evaluation)
        
        return report
    
    def _build_evaluation_report(self, evaluation: dict) -> str:
        """构建评估报告"""
        dimensions = evaluation['dimensions']
        total_score = evaluation['total_score']
        
        # 评级
        if total_score >= 90:
            grade = "S"
        elif total_score >= 80:
            grade = "A"
        elif total_score >= 70:
            grade = "B"
        else:
            grade = "C"
        
        report = f"""📊 训练完成！

综合得分：{total_score}/100  评级：{grade}

维度分析：
• 专业度：{dimensions['专业度']}/25
• 共情力：{dimensions['共情力']}/25
• 转化力：{dimensions['转化力']}/25
• 合规性：{dimensions['合规性']}/25

✨ 亮点：
{chr(10).join(['• ' + p for p in evaluation['highlights'][:3]])}

⚠️ 改进点：
{chr(10).join(['• ' + i for i in evaluation['improvements'][:3]])}

💡 更好的说法：
\"{evaluation['suggestion']}\"

回复"继续"开始新的训练，或回复"报告"查看历史成绩"""
        
        return report
    
    def _handle_view_report(self, user_id: str) -> str:
        """查看个人报告"""
        profile = self._get_user_profile(user_id)
        history = self._get_training_history(user_id, days=7)
        
        if not history:
            return '你还没有训练记录，回复"练习"开始你的第一次训练吧！'
        
        avg_score = sum(h['score'] for h in history) / len(history)
        
        # 找出强项和弱项
        dimension_scores = {}
        for h in history:
            for dim, score in h.get('dimensions', {}).items():
                if dim not in dimension_scores:
                    dimension_scores[dim] = []
                dimension_scores[dim].append(score)
        
        avg_dimensions = {
            dim: sum(scores) / len(scores) 
            for dim, scores in dimension_scores.items()
        }
        
        strongest = max(avg_dimensions, key=avg_dimensions.get)
        weakest = min(avg_dimensions, key=avg_dimensions.get)
        
        report = f"""📈 你的训练报告（近7天）

总练习次数：{len(history)}次
平均得分：{avg_score:.1f}分

能力分析：
• 最强项：{strongest}（{avg_dimensions[strongest]:.1f}分）
• 待提升：{weakest}（{avg_dimensions[weakest]:.1f}分）

建议：
本周重点练习【{weakest}】相关场景

回复"练习"开始针对性训练"""
        
        return report
    
    def _handle_view_team_data(self, user_id: str) -> str:
        """查看团队数据（仅主管）"""
        # 检查权限
        if not self._is_manager(user_id):
            return "你没有权限查看团队数据"
        
        team_data = self._get_team_data(user_id)
        
        report = f"""📊 团队概览

本周活跃：{team_data['active_count']}/{team_data['total_count']}人
人均练习：{team_data['avg_sessions']:.1f}次
平均得分：{team_data['avg_score']:.1f}分

⚠️ 需关注：
{chr(10).join(['• ' + m for m in team_data['concerns'][:3]])}

建议：
{team_data['suggestion']}

回复"导出"获取详细报告"""
        
        return report
    
    def _handle_help(self) -> str:
        """帮助信息"""
        return """🎓 话术教练 Agent 使用指南

【开始训练】
• "我想练习玻尿酸"
• "练习超声炮"
• "开始训练"

【查看成绩】
• "我练得怎么样"
• "查看报告"
• "我的数据"

【其他】
• "帮助" - 查看使用指南
• "结束" - 提前结束训练

随时发送消息即可开始练习！"""
    
    # 辅助方法
    def _extract_project(self, message: str) -> Optional[str]:
        """从消息中提取项目"""
        # 简单关键词匹配，实际可用 NLP
        projects = ["玻尿酸", "超声炮", "热玛吉", "水光针", "种植牙", "矫正", "双眼皮", "隆鼻"]
        for p in projects:
            if p in message:
                return p
        return None
    
    def _get_user_profile(self, user_id: str) -> dict:
        """获取用户档案"""
        # 从数据库读取
        # 简化实现
        return {
            'user_id': user_id,
            'level': 'medium',
            'weak_area': '价格谈判',
            'weaknesses': ['价格异议处理', '促成技巧']
        }
    
    def _get_training_history(self, user_id: str, days: int = 7) -> List[dict]:
        """获取训练历史"""
        # 从数据库读取
        return []
    
    def _save_training_record(self, user_id: str, session: dict, evaluation: dict):
        """保存训练记录"""
        # 保存到数据库
        pass
    
    def _is_manager(self, user_id: str) -> bool:
        """检查是否主管"""
        # 从用户角色判断
        return False
    
    def _get_team_data(self, user_id: str) -> dict:
        """获取团队数据"""
        return {
            'active_count': 10,
            'total_count': 15,
            'avg_sessions': 3.5,
            'avg_score': 76.5,
            'concerns': ['小张练习次数偏少', '价格谈判整体较弱'],
            'suggestion': '建议安排价格话术专项培训'
        }
    
    def _generate_patient_response(self, session: dict, consultant_msg: str) -> str:
        """生成患者回应"""
        # 调用 LLM 生成
        # 简化实现
        scenario = session['scenario']
        return "那大概要多少钱？效果能维持多久？"
    
    def _is_dialogue_end(self, patient_response: str) -> bool:
        """判断对话是否自然结束"""
        end_signals = ['确定要做', '预约', '考虑一下', '再对比', '决定了']
        return any(s in patient_response for s in end_signals)


def type_text(patient_type: str) -> str:
    """患者类型文本"""
    type_map = {
        'new': '初诊',
        'return': '复诊',
        'referral': '转介绍',
        'price_sensitive': '价格敏感型',
        'quality_focused': '品质优先型'
    }
    return type_map.get(patient_type, '初诊')


# 单例模式
_agent_instance = None

def get_agent() -> DialogueCoachAgent:
    """获取 Agent 实例"""
    global _agent_instance
    if _agent_instance is None:
        _agent_instance = DialogueCoachAgent()
    return _agent_instance
