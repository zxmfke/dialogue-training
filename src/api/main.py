"""
FastAPI Web API - 话术演练场后端服务
提供 API 接口和静态文件服务
"""

from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, FileResponse
from pydantic import BaseModel
from typing import List, Optional
import uvicorn
import os

from ..agent import get_agent

# 获取当前文件所在目录
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
WEBAPP_DIR = os.path.join(BASE_DIR, "webapp")

app = FastAPI(
    title="话术演练场 API",
    description="医院咨询师话术陪练系统",
    version="1.0.0"
)

# CORS 配置
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 挂载静态文件目录
app.mount("/static", StaticFiles(directory=WEBAPP_DIR), name="static")

# 获取 Agent 实例
agent = get_agent()


# 数据模型
class MessageRequest(BaseModel):
    user_id: str
    message: str
    channel: str = "web"


class TrainingStartRequest(BaseModel):
    user_id: str
    project: Optional[str] = None


# ========== Web 页面路由 ==========

@app.get("/", response_class=HTMLResponse)
async def web_app():
    """咨询师端 Web 应用"""
    index_path = os.path.join(WEBAPP_DIR, "index.html")
    if os.path.exists(index_path):
        with open(index_path, 'r', encoding='utf-8') as f:
            return f.read()
    return "<h1>话术演练场</h1><p>前端页面未找到</p>"


@app.get("/admin", response_class=HTMLResponse)
async def admin_panel():
    """管理后台"""
    admin_path = os.path.join(WEBAPP_DIR, "admin.html")
    if os.path.exists(admin_path):
        with open(admin_path, 'r', encoding='utf-8') as f:
            return f.read()
    return "<h1>管理后台</h1><p>管理页面未找到</p>"


# ========== API 路由 ==========

@app.get("/api")
async def api_root():
    """API 根路径"""
    return {
        "message": "话术演练场 API 服务运行中",
        "version": "1.0.0",
        "docs": "/docs",
        "endpoints": {
            "chat": "/api/chat",
            "training": "/api/training/start",
            "user": "/api/user/{user_id}",
            "team": "/api/team/{department}"
        }
    }


@app.post("/api/chat")
async def chat(request: MessageRequest):
    """主对话接口"""
    try:
        response = agent.process_message(
            user_id=request.user_id,
            message=request.message,
            channel=request.channel
        )
        return {
            "success": True,
            "user_id": request.user_id,
            "response": response
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/training/start")
async def start_training(request: TrainingStartRequest):
    """开始训练"""
    try:
        message = f"我想练习{request.project}" if request.project else "我想练习"
        response = agent.process_message(
            user_id=request.user_id,
            message=message
        )
        return {
            "success": True,
            "user_id": request.user_id,
            "scenario_started": True,
            "response": response
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/training/dialogue")
async def continue_dialogue(request: MessageRequest):
    """继续对话"""
    return await chat(request)


# ========== 用户相关 API ==========

@app.get("/api/user/{user_id}/profile")
async def get_user_profile(user_id: str):
    """获取用户档案"""
    return {
        "user_id": user_id,
        "name": "张咨询师",
        "department": "医美科",
        "level": "中级",
        "total_sessions": 25,
        "avg_score": 78.5,
        "weak_areas": ["价格谈判", "促成技巧"],
        "strong_areas": ["产品知识", "共情表达"]
    }


@app.get("/api/user/{user_id}/history")
async def get_training_history(user_id: str, days: int = 7):
    """获取训练历史"""
    return {
        "user_id": user_id,
        "days": days,
        "sessions": [
            {
                "date": "2026-02-17",
                "project": "玻尿酸",
                "score": 82,
                "duration": 5
            },
            {
                "date": "2026-02-16",
                "project": "超声炮",
                "score": 76,
                "duration": 4
            },
            {
                "date": "2026-02-15",
                "project": "价格异议",
                "score": 71,
                "duration": 6
            }
        ]
    }


# ========== 团队管理 API ==========

@app.get("/api/team/{department}/dashboard")
async def get_team_dashboard(department: str):
    """获取团队数据看板"""
    return {
        "department": department,
        "total_members": 15,
        "active_today": 12,
        "avg_score": 74.5,
        "total_sessions_week": 156,
        "top_performers": ["李咨询师", "王咨询师"],
        "concerns": ["价格谈判整体较弱", "新咨询师练习不足"],
        "trend": [120, 135, 142, 156, 148, 130, 156]
    }


@app.get("/api/team/{department}/members")
async def get_team_members(department: str):
    """获取团队成员列表"""
    return {
        "department": department,
        "members": [
            {"id": "001", "name": "李雪", "role": "高级咨询师", "sessions": 18, "score": 88, "status": "excellent"},
            {"id": "002", "name": "王芳", "role": "高级咨询师", "sessions": 15, "score": 85, "status": "excellent"},
            {"id": "003", "name": "张敏", "role": "咨询师", "sessions": 12, "score": 82, "status": "good"},
            {"id": "004", "name": "陈静", "role": "咨询师", "sessions": 10, "score": 78, "status": "good"},
            {"id": "005", "name": "刘洋", "role": "咨询师", "sessions": 8, "score": 72, "status": "warning"},
            {"id": "006", "name": "赵新", "role": "新人", "sessions": 2, "score": 65, "status": "danger"}
        ]
    }


# ========== 知识库 API ==========

@app.get("/api/knowledge/projects")
async def get_projects():
    """获取可训练的项目列表"""
    return {
        "projects": [
            {"id": "玻尿酸", "name": "玻尿酸注射", "department": "医美科", "scenarios": 5},
            {"id": "超声炮", "name": "超声炮抗衰", "department": "医美科", "scenarios": 4},
            {"id": "热玛吉", "name": "热玛吉紧肤", "department": "医美科", "scenarios": 4},
            {"id": "种植牙", "name": "种植牙", "department": "口腔科", "scenarios": 6},
            {"id": "矫正", "name": "牙齿矫正", "department": "口腔科", "scenarios": 5},
            {"id": "价格异议", "name": "价格异议处理", "department": "通用技能", "scenarios": 8},
            {"id": "促成技巧", "name": "促成转化技巧", "department": "通用技能", "scenarios": 6}
        ]
    }


@app.get("/api/knowledge/scenarios/{project_id}")
async def get_scenarios(project_id: str):
    """获取项目的训练场景"""
    scenarios_map = {
        "玻尿酸": [
            {"id": "新手入门", "name": "基础介绍", "difficulty": "easy", "description": "适合新咨询师练习基础话术"},
            {"id": "品牌对比", "name": "品牌选择指导", "difficulty": "medium", "description": "帮助患者选择合适的品牌"},
            {"id": "效果疑虑", "name": "效果疑虑化解", "difficulty": "medium", "description": "处理对效果的担心"}
        ],
        "价格异议": [
            {"id": "太贵了", "name": "太贵了怎么办", "difficulty": "medium", "description": "应对价格敏感患者"},
            {"id": "要对比", "name": "要对比其他家", "difficulty": "hard", "description": "处理竞品对比"},
            {"id": "超预算", "name": "超出预算", "difficulty": "medium", "description": "灵活推荐方案"}
        ]
    }
    return {
        "project": project_id,
        "scenarios": scenarios_map.get(project_id, [])
    }


# ========== 启动函数 ==========

def start_server(host="0.0.0.0", port=8000, reload=True):
    uvicorn.run(
        "src.api.main:app",
        host=host,
        port=port,
        reload=reload
    )


if __name__ == "__main__":
    start_server()
