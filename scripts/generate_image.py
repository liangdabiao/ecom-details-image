#!/usr/bin/env python3
"""图像生成脚本，通过 apiz CLI（https://apiz.ai）提交生成任务并下载结果。

仅当运行环境没有 agent 内置 imagegen 工具时才使用本脚本（Codex 环境请直接使用
agent 内置 imagegen）。本脚本不直接调用 HTTP API，而是调用已安装并登录好的
apiz CLI，认证由 CLI 自行处理（`apiz auth login` 或 APIZ_API_KEY 环境变量）。

流程：
  1. 本地参考图 → `apiz upload` 换取公网 URL
  2. `apiz generate <prompt> --model <model> --aspect-ratio <ratio> --wait --json`
  3. 解析任务 JSON，下载 result.images[].url 到输出目录

配置（均可省略）：
- APIZ_IMAGE_MODEL: 图片模型，默认 openai/gpt-image-2（兼容 IMG_MODEL、OPENAI_IMAGE_MODEL）
- APIZ_API_KEY: 可选，apiz CLI 的 key；已 `apiz auth login` 时无需设置（兼容 IMG_API_KEY）
- APIZ_BASE_URL: 可选，CLI 后端地址（兼容 IMG_BASE_URL）
- APIZ_BIN: 可选，apiz 可执行文件路径，默认从 PATH 查找
"""

from __future__ import annotations

import argparse
import json
import os
import shutil
import subprocess
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

DEFAULT_MODEL = "openai/gpt-image-2"
PIXEL_TO_RATIO: dict[str, str] = {
    "1024x1024": "1:1", "2048x2048": "1:1",
    "1536x1024": "3:2", "2048x1360": "3:2",
    "1024x1536": "2:3", "1360x2048": "2:3",
    "1024x768": "4:3", "2048x1536": "4:3",
    "768x1024": "3:4", "1536x2048": "3:4",
    "1280x1024": "5:4", "2560x2048": "5:4",
    "1024x1280": "4:5", "2048x2560": "4:5",
    "1536x864": "16:9", "2048x1152": "16:9", "3840x2160": "16:9",
    "864x1536": "9:16", "1152x2048": "9:16", "2160x3840": "9:16",
    "2048x1024": "2:1", "2688x1344": "2:1", "3840x1920": "2:1",
    "1024x2048": "1:2", "1344x2688": "1:2", "1920x3840": "1:2",
    "2016x864": "21:9", "2688x1152": "21:9", "3840x1648": "21:9",
    "864x2016": "9:21", "1152x2688": "9:21", "1648x3840": "9:21",
}
ENV_ALIASES = {
    "APIZ_IMAGE_MODEL": ("IMG_MODEL", "OPENAI_IMAGE_MODEL", "OPENAI_MODEL"),
    "APIZ_API_KEY": ("IMG_API_KEY", "OPENAI_API_KEY"),
    "APIZ_BASE_URL": ("IMG_BASE_URL", "OPENAI_BASE_URL", "OPENAI_API_BASE"),
}
UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36"


def fail(message: str, exit_code: int = 1) -> None:
    print(f"错误：{message}", file=sys.stderr)
    raise SystemExit(exit_code)


def log(message: str) -> None:
    print(message, file=sys.stderr)


# ── 配置与环境 ──────────────────────────────────────────────

def read_prompt(args) -> str:
    if args.prompt:
        prompt = args.prompt.strip()
    else:
        try:
            prompt = Path(args.prompt_file).read_text(encoding="utf-8").strip()
        except OSError as exc:
            fail(f"无法读取 prompt 文件：{exc}")
    if not prompt:
        fail("prompt 不能为空。")
    return prompt


def strip_env_value(value: str) -> str:
    value = value.strip()
    if len(value) >= 2 and value[0] == value[-1] and value[0] in {"'", '"'}:
        return value[1:-1]
    return value


def find_default_env_file() -> Path | None:
    for directory in (Path.cwd(), *Path.cwd().parents):
        env_file = directory / ".env"
        if env_file.is_file():
            return env_file
    return None


def load_env_file(env_file: Path | None) -> None:
    """加载 .env（可选）。支持 APIZ_* 和旧 IMG_*/OPENAI_* 别名。"""
    if env_file is None:
        return
    try:
        lines = env_file.read_text(encoding="utf-8").splitlines()
    except OSError as exc:
        fail(f"无法读取 .env 文件：{exc}")
    for line_number, raw_line in enumerate(lines, start=1):
        line = raw_line.strip()
        if not line or line.startswith("#"):
            continue
        if line.startswith("export "):
            line = line[len("export "):].strip()
        if "=" not in line:
            fail(f".env 第 {line_number} 行格式不正确，应为 KEY=value。")
        key, value = line.split("=", 1)
        key = key.strip()
        if key and key not in os.environ:
            os.environ[key] = strip_env_value(value)
    for canonical, aliases in ENV_ALIASES.items():
        if not os.environ.get(canonical):
            for alias in aliases:
                value = os.environ.get(alias, "").strip()
                if value:
                    os.environ[canonical] = value
                    break


def resolve_env(name: str) -> str:
    return os.environ.get(name, "").strip()


def locate_apiz() -> str:
    candidate = resolve_env("APIZ_BIN")
    if candidate:
        if Path(candidate).is_file():
            return candidate
        fail(f"APIZ_BIN 指向的文件不存在：{candidate}")
    found = shutil.which("apiz") or shutil.which("apiz.exe")
    if not found:
        fail(
            "找不到 apiz CLI。请先安装并登录：\n"
            "  安装后运行 `apiz auth login` 保存 API key，或设置 APIZ_API_KEY 环境变量。"
        )
    return found


def size_to_ratio(size: str) -> str:
    if ":" in size:
        return size
    if size.lower() in PIXEL_TO_RATIO:
        return PIXEL_TO_RATIO[size.lower()]
    fail(f"无法识别尺寸 '{size}'。请使用比例格式（1:1、16:9、2:3 等）或 1024x1024 这类像素尺寸。")


# ── apiz CLI 封装 ──────────────────────────────────────────

def run_apiz(apiz_bin: str, cli_args: list[str], timeout: int) -> str:
    command = [apiz_bin, *cli_args, "--json"]
    try:
        completed = subprocess.run(
            command, capture_output=True, text=True, encoding="utf-8", errors="replace",
            timeout=timeout,
        )
    except FileNotFoundError:
        fail(f"无法执行 apiz CLI：{apiz_bin}")
    except subprocess.TimeoutExpired:
        fail(f"apiz CLI 执行超时（{timeout}s）。可加大 --timeout 后重试。")
    if completed.returncode != 0:
        message = (completed.stderr or completed.stdout or "").strip()
        fail(f"apiz CLI 退出码 {completed.returncode}：{message[:800]}")
    return completed.stdout


def parse_json_output(raw: str, context: str) -> dict:
    text = raw.strip()
    # CLI 可能在 JSON 前输出日志行，取第一个 { 开始的部分。
    brace = text.find("{")
    if brace > 0:
        text = text[brace:]
    try:
        parsed = json.loads(text)
    except json.JSONDecodeError:
        fail(f"{context}返回的不是有效 JSON：{raw[:500]}")
    if not isinstance(parsed, dict):
        fail(f"{context}返回格式不正确：顶层结果不是对象。")
    return parsed


def upload_reference_image(apiz_bin: str, image_path: str) -> str:
    path = Path(image_path)
    if not path.is_file():
        fail(f"参考图片不存在：{image_path}")
    log(f"[apiz] 上传参考图 {path} ...")
    raw = run_apiz(apiz_bin, ["upload", str(path)], timeout=120)
    result = parse_json_output(raw, "上传参考图")
    url = result.get("public_url")
    if not url:
        fail(f"上传结果缺少 public_url：{json.dumps(result)[:300]}")
    log(f"[apiz] 参考图已上传: {url}")
    return url


def build_generate_args(prompt: str, model: str, ratio: str,
                        image_url: str | None, wait_timeout: int) -> list[str]:
    cli_args = [
        "generate", prompt, "--model", model, "--aspect-ratio", ratio,
        "--wait", "--wait-timeout", f"{wait_timeout}s",
    ]
    if image_url:
        cli_args += ["--image-url", image_url]
    return cli_args


def generate_image(apiz_bin: str, prompt: str, model: str, ratio: str,
                   image_url: str | None, timeout: int) -> dict:
    # 给 CLI 的等待预算略小于子进程超时，让 apiz 优先优雅退出。
    wait_timeout = max(60, timeout - 15)
    cli_args = build_generate_args(prompt, model, ratio, image_url, wait_timeout)
    log(f"[apiz] 提交生成任务: model={model} aspect-ratio={ratio} "
        f"参考图={'有' if image_url else '无'}，等待完成（通常 30-90 秒）...")
    raw = run_apiz(apiz_bin, cli_args, timeout=timeout)
    task = parse_json_output(raw, "生成任务")

    status = str(task.get("status", ""))
    task_id = task.get("task_id", "")
    if task_id:
        log(f"[apiz] 任务 {task_id} 状态: {status or 'unknown'}")
    if status != "completed":
        error = task.get("error")
        hint = f"，可稍后用 `apiz tasks get {task_id}` 查询" if task_id else ""
        fail(f"生成任务未完成（status={status or 'unknown'}）：{json.dumps(error or task, ensure_ascii=False)[:500]}{hint}")

    price = task.get("price")
    if price is not None:
        log(f"[apiz] 生成完成，消耗积分 {price}")
    return task


def extract_image_urls(task: dict) -> list[str]:
    result = task.get("result") or {}
    images = result.get("images")
    if not isinstance(images, list) or not images:
        fail(f"任务结果中缺少 images 数组：{json.dumps(task, ensure_ascii=False)[:300]}")
    urls: list[str] = []
    for item in images:
        if isinstance(item, str):
            urls.append(item)
        elif isinstance(item, dict) and item.get("url"):
            urls.append(item["url"])
    if not urls:
        fail(f"任务结果中缺少图片 URL：{json.dumps(images, ensure_ascii=False)[:300]}")
    return urls


def download_images(urls: list[str], output_dir: Path, fmt: str) -> list[Path]:
    output_dir.mkdir(parents=True, exist_ok=True)
    timestamp = time.strftime("%Y%m%d-%H%M%S")
    paths: list[Path] = []
    for index, url in enumerate(urls, start=1):
        suffix = _suffix_from_url(url, fmt)
        output_path = output_dir / f"image-{timestamp}-{index:02d}.{suffix}"
        log(f"  下载图片: {url}")
        request = urllib.request.Request(url, headers={"User-Agent": UA})
        try:
            with urllib.request.urlopen(request, timeout=120) as response:
                output_path.write_bytes(response.read())
        except urllib.error.HTTPError as exc:
            fail(f"下载图片失败（HTTP {exc.code}）：{url}")
        except (urllib.error.URLError, TimeoutError):
            fail(f"下载图片超时或连接失败：{url}")
        paths.append(output_path)
    return paths


# ── 工具函数 ──────────────────────────────────────────────

def _suffix_from_url(url: str, fallback: str) -> str:
    path = urllib.parse.urlparse(url).path
    suffix = Path(path).suffix.lower().lstrip(".")
    if suffix in {"png", "jpg", "jpeg", "webp"}:
        return "jpg" if suffix == "jpeg" else suffix
    return fallback


# ── CLI ──────────────────────────────────────────────

def parse_args():
    parser = argparse.ArgumentParser(
        description="通过 apiz CLI 生成图片（Codex 环境请直接使用 agent 内置 imagegen 工具）。"
    )
    prompt_group = parser.add_mutually_exclusive_group(required=True)
    prompt_group.add_argument("--prompt", help="直接传入图片生成 Prompt。")
    prompt_group.add_argument("--prompt-file", help="从文本文件读取图片生成 Prompt。")
    parser.add_argument("--output-dir", default="generated-images",
                        help="图片输出目录，默认 generated-images。")
    parser.add_argument("--env-file", help="指定 .env 配置文件；不指定时从当前目录向上查找（可选）。")
    parser.add_argument("--model", help=f"apiz 图片模型 id，默认 {DEFAULT_MODEL}（可用 APIZ_IMAGE_MODEL 覆盖）。")
    parser.add_argument("--size", default="1:1",
                        help="图片比例，默认 1:1（如 16:9、9:16、2:3、4:5；也兼容 1024x1024 像素写法）。")
    parser.add_argument("--image", help="本地参考产品图片路径，先上传 apiz CDN 再走图生图。")
    parser.add_argument("--image-url", help="参考图公网 URL（与 --image 二选一，URL 优先）。")
    parser.add_argument("--timeout", type=int, default=420,
                        help="单个生成任务等待上限秒数，默认 420。")
    parser.add_argument("--format", choices=("png", "jpeg", "webp"), default="png",
                        help="保存格式的默认扩展名（实际以后缀/类型为准），默认 png。")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    env_file = Path(args.env_file) if args.env_file else find_default_env_file()
    load_env_file(env_file)
    prompt = read_prompt(args)

    apiz_bin = locate_apiz()
    model = args.model or resolve_env("APIZ_IMAGE_MODEL") or DEFAULT_MODEL
    ratio = size_to_ratio(args.size)

    image_url = args.image_url
    if not image_url and args.image:
        image_url = upload_reference_image(apiz_bin, args.image)

    task = generate_image(apiz_bin, prompt, model, ratio, image_url, args.timeout)
    paths = download_images(extract_image_urls(task), Path(args.output_dir), args.format)

    print("生成完成：")
    for path in paths:
        print(path)


if __name__ == "__main__":
    main()
