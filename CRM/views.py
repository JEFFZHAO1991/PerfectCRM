from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings
import requests
import json

# Create your views here.
def index(request):
    return render(request, "index.html")

def customer_list(request):
    return render(request, "sales/customers.html")


# ========= 下面是文本生成 API 部分 =========

# Google Gemini 文本接口地址（你给的那个）
GEMINI_API_URL = (
    "https://generativelanguage.googleapis.com/v1beta/models/"
    "gemini-2.0-flash:generateContent"
)

@csrf_exempt
def generate_text(request):
    """
    POST /api/generate/
    接收: prompt (文字)
    调用 Google Gemini 免费模型，返回生成的文本：
    { "text": "..." }
    """
    if request.method != "POST":
        return JsonResponse({"error": "POST required"}, status=405)

    # 1. 从表单或 JSON 里取 prompt
    prompt = request.POST.get("prompt")

    # 如果不是 form 提交，可能是 application/json，就从 body 里解析
    if not prompt:
        try:
            body = request.body.decode("utf-8") or "{}"
            data = json.loads(body)
            prompt = data.get("prompt")
        except Exception:
            prompt = None

    if not prompt:
        return JsonResponse({"error": "prompt required"}, status=400)

    # 2. 从 settings 里取你的 API Key（稍后在 settings.py 里配置）
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
        "X-goog-api-key": api_key,
    }

    # 4. 调用 Gemini 接口
    try:
        resp = requests.post(
            GEMINI_API_URL,
            headers=headers,
            json=payload,
            timeout=60,
        )
    except requests.RequestException as e:
        return JsonResponse(
            {"error": "gemini_unreachable", "detail": str(e)},
            status=502,
        )

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

    # 5. 从返回结果里把文本抽出来（简单版）
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
