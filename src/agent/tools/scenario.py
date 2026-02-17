"""
场景生成工具 - 生成训练场景和患者角色
"""

import random
from typing import Dict, List


class ScenarioTool:
    """场景生成工具"""
    
    def __init__(self):
        # 患者姓名库
        self.female_names = ['李女士', '王女士', '张女士', '陈女士', '刘女士', '赵女士', '孙女士', '周女士']
        self.male_names = ['李先生', '王先生', '张先生', '陈先生', '刘先生', '赵先生', '孙先生', '周先生']
        
        # 患者性格类型
        self.personalities = {
            '犹豫型': {
                'traits': ['反复确认', '需要 reassurance', '决策慢'],
                'questions': ['会不会有风险？', '效果能维持多久？', '会不会很疼？'],
                'objections': ['我再考虑考虑', '要回去商量一下', '有点担心']
            },
            '价格敏感型': {
                'traits': ['关注性价比', '会对比', '需要优惠'],
                'questions': ['多少钱？', '有没有活动？', '能不能便宜点？'],
                'objections': ['太贵了', '超预算了', '别的医院更便宜']
            },
            '品质优先型': {
                'traits': ['关注效果', '在意医生资历', '不怕花钱'],
                'questions': ['医生经验如何？', '用什么品牌？', '案例效果如何？'],
                'objections': ['担心效果不理想', '怕做出来不自然']
            },
            '冲动型': {
                'traits': ['决策快', '容易被打动', '即时行动'],
                'questions': ['现在做来得及吗？', '今天能做吗？', '多久能恢复？'],
                'objections': ['时间不合适', '恢复期内有事']
            },
            '理性型': {
                'traits': ['逻辑分析', '收集信息', '全面比较'],
                'questions': ['原理是什么？', '有什么副作用？', '和XX有什么区别？'],
                'objections': ['需要再了解一下', '想对比其他方案']
            }
        }
        
        # 项目关注点
        self.project_concerns = {
            '玻尿酸': {
                'age_range': (25, 45),
                'concerns': ['法令纹明显', '下巴后缩', '鼻梁不够高', '太阳穴凹陷', '唇部不够丰满'],
                'questions': ['会不会僵硬？', '能维持多久？', '用什么品牌好？'],
                'objections': ['怕打出玻尿酸脸', '担心吸收太快', '价格不便宜']
            },
            '超声炮': {
                'age_range': (30, 50),
                'concerns': ['面部松弛', '下颌线不明显', '法令纹加深', '眼周细纹'],
                'questions': ['疼不疼？', '需要做几次？', '多久能看到效果？'],
                'objections': ['听说很疼', '效果不如热玛吉', '价格贵']
            },
            '热玛吉': {
                'age_range': (35, 55),
                'concerns': ['皮肤松弛', '皱纹明显', '轮廓不清晰', '抗衰需求'],
                'questions': ['几代仪器？', '发数多少？', '维持多久？'],
                'objections': ['听说很疼', '效果不明显', '价格太高']
            },
            '种植牙': {
                'age_range': (35, 65),
                'concerns': ['缺牙影响咀嚼', '邻牙倾斜', '牙槽骨吸收', '美观问题'],
                'questions': ['能用多久？', '手术疼不疼？', '多久能好？'],
                'objections': ['怕手术', '费用太高', '周期长']
            },
            '矫正': {
                'age_range': (18, 35),
                'concerns': ['牙齿不齐', '龅牙', '地包天', '牙缝大'],
                'questions': ['需要多久？', '要不要拔牙？', '用什么矫治器？'],
                'objections': ['时间太长', '怕疼', '影响美观']
            }
        }
    
    def generate(self, project: str, user_weakness: List[str], difficulty: str = 'medium') -> Dict:
        """
        生成训练场景
        
        Args:
            project: 项目名称
            user_weakness: 用户薄弱环节
            difficulty: 难度级别 easy/medium/hard
            
        Returns:
            场景配置
        """
        # 根据用户薄弱点选择患者性格
        if user_weakness:
            # 针对薄弱点生成场景
            if '价格' in str(user_weakness):
                personality_key = '价格敏感型'
            elif '异议' in str(user_weakness):
                personality_key = '犹豫型'
            elif '促成' in str(user_weakness):
                personality_key = '理性型'
            else:
                personality_key = random.choice(list(self.personalities.keys()))
        else:
            personality_key = random.choice(list(self.personalities.keys()))
        
        personality = self.personalities[personality_key]
        
        # 生成患者信息
        project_info = self.project_concerns.get(project, {
            'age_range': (25, 50),
            'concerns': ['有改善需求'],
            'questions': ['效果怎么样？'],
            'objections': ['考虑一下']
        })
        
        # 根据项目选择性别倾向
        if project in ['玻尿酸']:
            name = random.choice(self.female_names)
        elif project in ['种植牙', '矫正']:
            name = random.choice(random.choice([self.male_names, self.female_names]))
        else:
            name = random.choice(self.female_names)
        
        age = random.randint(project_info['age_range'][0], project_info['age_range'][1])
        concern = random.choice(project_info['concerns'])
        
        # 生成开场白
        opening = self._generate_opening(name, age, project, concern, personality_key)
        
        # 生成预期对话流程（给AI患者参考）
        expected_flow = self._generate_expected_flow(
            project, personality_key, project_info
        )
        
        return {
            'patient': {
                'name': name,
                'age': age,
                'gender': '女' if name in self.female_names else '男',
                'concern': concern,
                'personality': personality_key,
                'traits': personality['traits'],
                'questions': personality['questions'] + project_info['questions'],
                'objections': personality['objections'] + project_info['objections']
            },
            'project': project,
            'difficulty': difficulty,
            'opening': opening,
            'expected_flow': expected_flow,
            'context': f"患者{name}，{age}岁，主要诉求是改善{concern}。性格属于{personality_key}，{random.choice(personality['traits'])}。"
        }
    
    def _generate_opening(self, name: str, age: int, project: str, concern: str, personality: str) -> str:
        """生成患者开场白"""
        openings = {
            '犹豫型': [
                f"你好，我是{name}，今年{age}岁。我最近看网上说{project}挺火的，但我不太了解，想先咨询一下。",
                f"您好，我主要是想改善{concern}，但对这个{project}有点担心，不知道安全吗？"
            ],
            '价格敏感型': [
                f"你好，我想咨询一下{project}，多少钱啊？",
                f"您好，我是{name}，听说你们这{project}不错，现在有什么优惠活动吗？"
            ],
            '品质优先型': [
                f"你好，我是{name}，朋友推荐我来咨询{project}。我想了解一下你们用的什么产品，医生经验怎么样？",
                f"您好，我对{concern}比较在意，想找一个效果好的方案。你们这{project}案例多吗？"
            ],
            '冲动型': [
                f"你好！我想做{project}，今天能做吗？",
                f"您好，我看小红书上说你们这{project}效果很好，我想预约做一下！"
            ],
            '理性型': [
                f"你好，我是{name}，想系统了解一下{project}。能给我介绍一下原理、效果、风险和价格吗？",
                f"您好，我做过一些功课，{project}主要是针对{concern}，但我想知道和XX项目有什么区别？"
            ]
        }
        
        return random.choice(openings.get(personality, openings['犹豫型']))
    
    def _generate_expected_flow(self, project: str, personality: str, project_info: dict) -> List[Dict]:
        """生成预期对话流程"""
        flow = []
        
        # 第一轮：需求确认
        flow.append({
            'turn': 1,
            'stage': '需求挖掘',
            'patient_goal': '表达诉求和顾虑',
            'consultant_goal': '了解需求，建立信任'
        })
        
        # 第二轮：产品介绍
        flow.append({
            'turn': 2,
            'stage': '产品介绍',
            'patient_goal': '了解方案详情',
            'consultant_goal': '专业介绍，消除顾虑'
        })
        
        # 第三轮：异议处理（根据性格）
        flow.append({
            'turn': 3,
            'stage': '异议处理',
            'patient_goal': f'提出{personality}典型顾虑',
            'consultant_goal': '有效回应异议'
        })
        
        # 第四轮：促成
        flow.append({
            'turn': 4,
            'stage': '促成转化',
            'patient_goal': '决定是否预约',
            'consultant_goal': '引导下一步行动'
        })
        
        return flow
    
    def generate_follow_up(self, scenario: dict, turn: int, consultant_msg: str) -> str:
        """
        生成患者回应
        
        实际实现中应该调用 LLM，这里用规则模拟
        """
        patient = scenario['patient']
        personality = patient['personality']
        
        # 根据轮数和咨询师回复生成回应
        if turn == 1:
            # 第一轮：回应咨询师的询问
            if personality == '价格敏感型':
                return f"我主要是想改善{patient['concern']}，大概多少钱啊？"
            elif personality == '犹豫型':
                return f"{patient['concern']}困扰我很久了，但怕疼，也怕效果不好..."
            else:
                return f"{patient['concern']}比较明显，想了解一下{scenario['project']}的效果。"
        
        elif turn == 2:
            # 第二轮：对介绍做出反应
            if '价格' in consultant_msg or '钱' in consultant_msg:
                return f"这个价格有点超预算，有没有优惠或者分期？"
            elif '效果' in consultant_msg:
                return f"能维持多久？需要经常补打吗？"
            elif '安全' in consultant_msg or '放心' in consultant_msg:
                return f"那具体怎么操作？疼不疼？"
            else:
                return random.choice(patient['questions'])
        
        elif turn == 3:
            # 第三轮：提出异议或表达意向
            if personality == '犹豫型':
                return f"{random.choice(patient['objections'])}，我想再考虑考虑。"
            elif personality == '价格敏感型':
                return f"{random.choice(patient['objections'])}，能不能再便宜点？"
            else:
                return f"听起来不错，那什么时候可以安排？"
        
        else:
            # 结束轮
            endings = [
                "好的，那帮我预约吧。",
                "行，那我先考虑一下，回头联系你。",
                "可以，我想先看看案例再决定。",
                f"这个价格还是有点贵，我再对比对比。"
            ]
            return random.choice(endings)
