from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings
import requests
import json

# ================== 普通页面视图 ==================

def index(request):
    return render(request, "index.html")

def customer_list(request):
    return render(request, "sales/customers.html")

def ai_page(request):
    """
    单独的 AI 文本生成页面视图
    """
    return render(request, "ai_generate.html")


# ================== 文本生成 API 部分 ==================

# 建议先用 1.5 版本（一般 free tier 都支持），后面你也可以改回 2.0
GEMINI_API_URL = (
    "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent"
)
# 如果你确认文档要求用 -latest，也可以换成：
# "gemini-1.5-flash-latest:generateContent"

@csrf_exempt
def generate_text(request):
    """
    POST /api/generate/
    接收: prompt (文字)
    调用 Google Gemini 文本模型，返回生成的文本：
    { "text": "..." }
    """
    if request.method != "POST":
        return JsonResponse({"error": "POST required"}, status=405)

    # 1. 从表单或 JSON 里取 prompt
    prompt = request.POST.get("prompt")

    if not prompt:
        # 可能是 application/json 方式
        try:
            body = request.body.decode("utf-8") or "{}"
            data = json.loads(body)
            prompt = data.get("prompt")
        except Exception:
            prompt = None

    if not prompt:
        return JsonResponse({"error": "prompt required"}, status=400)

    # 2. 从 settings 里取你的 API Key（settings.py 里要有 GEMINI_API_KEY）
    api_key = getattr(settings, "GEMINI_API_KEY", None)
    if not api_key:
        return JsonResponse(
            {
                "error": "server_not_configured",
                "detail": "GEMINI_API_KEY is not set in settings.py",
            },
            status=500,
        )

    # 3. 按 Google 要求构造请求体
    payload = {
        "contents": [
            {
                "parts": [
                    {"text": prompt}
                ]
            }
        ]
    }

    headers = {
        "Content-Type": "application/json",
        # 也可以不用 header 传 key，只用 URL ?key=...
        # "x-goog-api-key": api_key,
    }

    # 4. 调用 Gemini 接口（关键：这里统一用 api_key，不要用硬编码）
    try:
        resp = requests.post(
            GEMINI_API_URL + f"?key={api_key}",
            headers=headers,
            json=payload,
            timeout=60,
        )
    except requests.RequestException as e:
        return JsonResponse(
            {"error": "gemini_unreachable", "detail": str(e)},
            status=502,
        )

    # 5. 处理非 200 情况，直接把 Google 返回的内容给前端看
    if resp.status_code != 200:
        return JsonResponse(
            {
                "error": "gemini_error",
                "status_code": resp.status_code,
                "detail": resp.text,
            },
            status=500,
        )

    data = resp.json()

    # 6. 从返回结果里把文本抽出来（简单版）
    text = ""
    try:
        candidates = data.get("candidates", [])
        if candidates:
            content = candidates[0].get("content", {})
            parts = content.get("parts", [])
            pieces = []
            for p in parts:
                if "text" in p:
                    pieces.append(p["text"])
            text = "\n".join(pieces) if pieces else ""
    except Exception as e:
        return JsonResponse(
            {
                "error": "parse_error",
                "detail": f"Error parsing Gemini response: {e}",
                "raw": data,
            },
            status=500,
        )

    if not text:
        return JsonResponse(
            {"error": "no_text_in_response", "raw": data},
            status=500,
        )

    # 最终只返回 text，前端直接用
    return JsonResponse({"text": text})
