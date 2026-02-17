"""
评估工具 - 对话质量多维度评估
"""

import re
from typing import Dict, List


class EvaluationTool:
    """对话评估工具"""
    
    def __init__(self, config: dict):
        self.dimensions = config['dimensions']
        self.weights = {d['name']: d['weight'] for d in self.dimensions}
    
    def evaluate(self, dialogue_history: List[dict], project: str, sensitive_words: List[str]) -> dict:
        """
        评估对话质量
        
        Args:
            dialogue_history: 对话历史记录
            project: 项目名称
            sensitive_words: 敏感词列表
            
        Returns:
            评估结果
        """
        # 提取咨询师的发言
        consultant_msgs = [d['content'] for d in dialogue_history if d['role'] == 'consultant']
        full_dialogue = '\n'.join([f"{'患者' if d['role'] == 'patient' else '咨询师'}：{d['content']}" for d in dialogue_history])
        
        # 各维度评估
        dimensions = {}
        
        # 1. 专业度评估
        dimensions['专业度'] = self._evaluate_professionalism(consultant_msgs, project)
        
        # 2. 共情力评估
        dimensions['共情力'] = self._evaluate_empathy(consultant_msgs, dialogue_history)
        
        # 3. 转化力评估
        dimensions['转化力'] = self._evaluate_conversion(consultant_msgs, dialogue_history)
        
        # 4. 合规性评估
        dimensions['合规性'] = self._evaluate_compliance(consultant_msgs, sensitive_words)
        
        # 计算总分
        total_score = sum(dimensions[dim] * (self.weights.get(dim, 25) / 25) for dim in dimensions)
        total_score = round(total_score)
        
        # 生成反馈
        highlights = self._extract_highlights(consultant_msgs, dialogue_history)
        improvements = self._extract_improvements(dimensions, consultant_msgs)
        suggestion = self._generate_suggestion(dimensions, project)
        
        return {
            'total_score': total_score,
            'dimensions': dimensions,
            'highlights': highlights,
            'improvements': improvements,
            'suggestion': suggestion,
            'dialogue_summary': full_dialogue
        }
    
    def _evaluate_professionalism(self, messages: List[str], project: str) -> int:
        """评估专业度"""
        score = 15  # 基础分
        
        all_text = ' '.join(messages)
        
        # 检查专业术语使用
        professional_terms = {
            '玻尿酸': ['透明质酸', '分子量', '交联度', '维持时间', '吸收'],
            '超声炮': ['SMAS层', '聚焦超声', '紧致', '提升', '无创'],
            '热玛吉': ['射频', '胶原蛋白', '紧致', '抗衰', '疗程'],
            '种植牙': ['种植体', '骨结合', '愈合期', '冠修复', '使用寿命'],
            '矫正': ['牙列不齐', '咬合', '矫治器', '保持器', '疗程']
        }
        
        terms = professional_terms.get(project, ['专业', '技术', '效果', '安全'])
        term_count = sum(1 for term in terms if term in all_text)
        score += min(5, term_count)  # 专业术语加分
        
        # 检查是否解释清晰
        if any(kw in all_text for kw in ['因为', '原理是', '原因是', '作用是']):
            score += 3
        
        # 检查是否有数据支撑
        if re.search(r'\d+%|\d+年|\d+个月|百分之', all_text):
            score += 2
        
        return min(25, score)
    
    def _evaluate_empathy(self, messages: List[str], dialogue_history: List[dict]) -> int:
        """评估共情力"""
        score = 12  # 基础分
        
        all_text = ' '.join(messages)
        
        # 共情词汇
        empathy_words = ['理解', '明白', '担心', '顾虑', '放心', '别着急', '慢慢来', '确实']
        empathy_count = sum(1 for word in empathy_words if word in all_text)
        score += min(6, empathy_count * 2)
        
        # 检查是否回应患者顾虑
        patient_concerns = []
        for i, d in enumerate(dialogue_history):
            if d['role'] == 'patient' and i < len(dialogue_history) - 1:
                concern = d['content']
                next_response = dialogue_history[i + 1]['content']
                # 简单检查是否回应
                if any(kw in concern for kw in ['担心', '怕', '疼', '贵', '效果']):
                    if any(kw in next_response for kw in ['理解', '确实', '放心', '说明']):
                        score += 2
        
        # 检查语气
        if any(kw in all_text for kw in ['您', '咱们', '一起']):
            score += 2
        
        # 负面检查：是否打断、否定患者
        if any(kw in all_text for kw in ['不对', '不是', '你错了']):
            score -= 3
        
        return min(25, max(0, score))
    
    def _evaluate_conversion(self, messages: List[str], dialogue_history: List[dict]) -> int:
        """评估转化力"""
        score = 10  # 基础分
        
        all_text = ' '.join(messages)
        
        # 检查是否有促成动作
        conversion_signals = [
            '预约', '安排', '确定', '现在就', '今天', '下次', '来院',
            '面诊', '设计', '方案', '体验一下', '试试看'
        ]
        
        for signal in conversion_signals:
            if signal in all_text:
                score += 2
                break  # 只加一次
        
        # 检查是否提出下一步
        if any(kw in all_text for kw in ['下一步', '接下来', '然后', '之后']):
            score += 3
        
        # 检查是否处理异议后推进
        objection_handled = False
        for i in range(len(dialogue_history) - 1):
            if dialogue_history[i]['role'] == 'patient':
                patient_msg = dialogue_history[i]['content']
                if any(kw in patient_msg for kw in ['贵', '考虑', '再想想']):
                    # 检查下一条咨询师回复是否处理并推进
                    if i + 1 < len(dialogue_history):
                        response = dialogue_history[i + 1]['content']
                        if len(response) > 20:  # 简单判断有内容
                            objection_handled = True
        
        if objection_handled:
            score += 5
        
        # 检查结尾
        if messages:
            last_msg = messages[-1]
            if any(kw in last_msg for kw in ['预约', '确定', '现在', '今天', '来院']):
                score += 5
        
        return min(25, score)
    
    def _evaluate_compliance(self, messages: List[str], sensitive_words: List[str]) -> int:
        """评估合规性"""
        score = 25  # 满分基础
        
        all_text = ' '.join(messages)
        
        # 检查敏感词
        violations = []
        for word in sensitive_words:
            if word in all_text:
                violations.append(word)
                score -= 5  # 每个敏感词扣5分
        
        # 检查绝对化用语
        absolute_words = ['一定', '肯定', '绝对', '保证', '100%', '百分百']
        for word in absolute_words:
            if word in all_text:
                score -= 2
        
        # 检查疗效承诺
        efficacy_promises = ['治愈', '根治', '包好', '肯定好', '绝对有效']
        for word in efficacy_promises:
            if word in all_text:
                score -= 5
        
        return max(0, score)
    
    def _extract_highlights(self, messages: List[str], dialogue_history: List[dict]) -> List[str]:
        """提取亮点"""
        highlights = []
        all_text = ' '.join(messages)
        
        # 专业术语使用
        if any(kw in all_text for kw in ['原理', '技术', '层次', '结构']):
            highlights.append("专业术语使用准确，体现了专业度")
        
        # 共情表达
        if any(kw in all_text for kw in ['理解您的', '明白您的', '确实']):
            highlights.append("善于使用共情语言，让患者感到被理解")
        
        # 结构化表达
        if any(kw in all_text for kw in ['首先', '其次', '最后', '第一', '第二']):
            highlights.append("表达条理清晰，逻辑性强")
        
        # 数据支撑
        if re.search(r'\d+%|\d+例|\d+年经验', all_text):
            highlights.append("善用数据增强说服力")
        
        # 促成技巧
        if any(kw in all_text for kw in ['预约', '安排', '确定']):
            highlights.append("有主动促成的意识")
        
        return highlights if highlights else ["完成了一次完整的对话练习"]
    
    def _extract_improvements(self, dimensions: dict, messages: List[str]) -> List[str]:
        """提取改进点"""
        improvements = []
        
        if dimensions['专业度'] < 20:
            improvements.append("可以增加更多专业术语和原理说明，提升专业形象")
        
        if dimensions['共情力'] < 20:
            improvements.append("多使用'我理解您'、'确实'等共情词汇，先认同再引导")
        
        if dimensions['转化力'] < 18:
            improvements.append("在合适时机提出明确的下一步行动，如'我帮您预约一下？'")
        
        if dimensions['合规性'] < 25:
            improvements.append("避免使用'绝对'、'保证'等过度承诺词汇，用'一般来说'、'大部分顾客'代替")
        
        if not improvements:
            improvements.append("继续保持，可以尝试在更复杂的异议场景下练习")
        
        return improvements
    
    def _generate_suggestion(self, dimensions: dict, project: str) -> str:
        """生成改进建议话术"""
        # 找出最低分维度
        weakest = min(dimensions, key=dimensions.get)
        
        suggestions = {
            '专业度': f"我们使用的是进口{project}，分子结构稳定，维持时间通常在6-12个月，具体要看个人代谢情况。",
            '共情力': "我完全理解您的担心，很多顾客第一次来都会有类似的顾虑。要不我先带您看看我们之前的案例效果？",
            '转化力': "您看这样，我帮您安排一下面诊，让医生给您做个详细的设计方案，到时候您再决定做不做，好吗？",
            '合规性': "根据大多数顾客的反馈，效果是比较满意的，但具体还是要看个人情况。我们建议您先来面诊看看。"
        }
        
        return suggestions.get(weakest, "继续保持，多练习不同类型的患者场景。")
