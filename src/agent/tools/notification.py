"""
通知工具 - 发送消息到各渠道
"""

import requests
import json
from typing import List, Dict, Optional


class NotificationTool:
    """通知工具"""
    
    def __init__(self, channels_config: List[str]):
        self.channels = channels_config
        self.channel_handlers = {
            'wecom': self._send_wecom,
            'wechat': self._send_wechat,
            'webhook': self._send_webhook
        }
    
    def send(self, user_id: str, message: str, channel: str = None) -> bool:
        """
        发送通知
        
        Args:
            user_id: 用户ID
            message: 消息内容
            channel: 指定渠道，不指定则使用默认渠道
            
        Returns:
            是否发送成功
        """
        if channel and channel in self.channel_handlers:
            return self.channel_handlers[channel](user_id, message)
        
        # 默认使用第一个可用渠道
        for ch in self.channels:
            if ch in self.channel_handlers:
                return self.channel_handlers[ch](user_id, message)
        
        return False
    
    def send_reminder(self, user_id: str, days_since_last: int) -> bool:
        """
        发送练习提醒
        
        Args:
            user_id: 用户ID
            days_since_last: 距离上次练习的天数
            
        Returns:
            是否发送成功
        """
        if days_since_last >= 3:
            message = f"📢 练习提醒\n\n你已经{days_since_last}天没有练习了！\n\n保持手感很重要，今天花5分钟练习一下吧 💪\n\n回复'练习'开始训练"
        else:
            message = "🌟 今日练习推荐\n\n根据你的薄弱点，建议今天练习【价格异议处理】\n\n回复'练习'开始！"
        
        return self.send(user_id, message)
    
    def send_daily_report(self, manager_id: str, report_data: Dict) -> bool:
        """
        发送团队日报给主管
        
        Args:
            manager_id: 主管ID
            report_data: 报告数据
            
        Returns:
            是否发送成功
        """
        message = f"""📊 团队日报（{report_data['date']}）

今日练习人数：{report_data['active_count']}/{report_data['total_count']}
人均练习次数：{report_data['avg_sessions']:.1f}
平均得分：{report_data['avg_score']:.1f}

🏆 今日之星：{report_data.get('top_performer', '无')}

⚠️ 需关注：
{chr(10).join(['• ' + c for c in report_data.get('concerns', [])])}

详细报告请登录管理后台查看"""
        
        return self.send(manager_id, message)
    
    def _send_wecom(self, user_id: str, message: str) -> bool:
        """发送到企业微信"""
        # 企业微信机器人 API 实现
        # 需要配置 webhook URL
        webhook_url = self._get_wecom_webhook(user_id)
        
        if not webhook_url:
            print(f"[WeCom] 未配置 webhook for {user_id}")
            return False
        
        payload = {
            "msgtype": "text",
            "text": {
                "content": message,
                "mentioned_list": [user_id] if user_id else []
            }
        }
        
        try:
            response = requests.post(
                webhook_url,
                json=payload,
                timeout=10
            )
            return response.status_code == 200
        except Exception as e:
            print(f"[WeCom] 发送失败: {e}")
            return False
    
    def _send_wechat(self, user_id: str, message: str) -> bool:
        """发送到微信小程序/公众号"""
        # 微信小程序订阅消息或公众号模板消息
        # 需要接入微信官方 API
        print(f"[WeChat] 发送消息给 {user_id}: {message[:50]}...")
        return True
    
    def _send_webhook(self, user_id: str, message: str) -> bool:
        """发送到自定义 Webhook"""
        webhook_url = self._get_webhook_url(user_id)
        
        if not webhook_url:
            return False
        
        payload = {
            "user_id": user_id,
            "message": message,
            "timestamp": int(time.time())
        }
        
        try:
            response = requests.post(
                webhook_url,
                json=payload,
                timeout=10
            )
            return response.status_code == 200
        except Exception as e:
            print(f"[Webhook] 发送失败: {e}")
            return False
    
    def _get_wecom_webhook(self, user_id: str) -> Optional[str]:
        """获取企业微信 webhook"""
        # 从配置或数据库读取
        # 简化实现
        return None
    
    def _get_webhook_url(self, user_id: str) -> Optional[str]:
        """获取自定义 webhook URL"""
        return None


import time
