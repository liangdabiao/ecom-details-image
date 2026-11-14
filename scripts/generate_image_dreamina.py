#!/usr/bin/env python3
"""图像生成脚本（即梦通道），通过 dreamina-canvas CLI 调用 Seedream 系列模型。

认证由 CLI 自行处理（OAuth 登录），本脚本不接触任何密钥。

流程：
  1. 解析目标画布：--canvas-id / DREAMINA_CANVAS_ID → 当前画布 → 自动创建
  2. 本地参考图 → `resource upload` 登记为画布素材，等待就绪
  3. `node create image --run --wait` 保存、报价（不超过 --credit-ceiling）并运行
  4. `resource download` 把节点产物下载到输出目录

配置（均可省略）：
- DREAMINA_IMAGE_MODEL: 图片模型，默认 seedream_5.5
- DREAMINA_CANVAS_ID:   画布 UUID；不设置时使用当前画布，无当前画布则自动创建
- DREAMINA_RESOLUTION:  默认 2K（Seedream 5.5 支持 1.5K / 2K）
- DREAMINA_CREDIT_CEILING: 单节点积分上限，默认 10
- DREAMINA_BIN:         可执行文件路径，默认从 PATH 查找
"""

from __future__ import annotations

import argparse
import json
import os
import shutil
import subprocess
import sys
import time
import uuid
from pathlib import Path

DEFAULT_MODEL = "seedream_5.5"
DEFAULT_RESOLUTION = "2K"
DEFAULT_CREDIT_CEILING = 10
DEFAULT_CANVAS_NAME = "ecom-details-image"
# Seedream 5.5 实际支持的比例；不在此列的按 RATIO_FALLBACK 换算并提示。
SUPPORTED_RATIOS = {"1:1", "3:4", "16:9", "4:3", "9:16", "2:3", "3:2", "21:9"}
RATIO_FALLBACK = {
    "4:5": "3:4", "5:4": "4:3", "2:1": "21:9", "1:2": "9:16",
    "9:21": "9:16", "3:1": "21:9", "1:3": "9:16", "16:10": "3:2", "10:16": "2:3",
}
PIXEL_TO_RATIO = {
    "1024x1024": "1:1", "2048x2048": "1:1",
    "1024x1536": "2:3", "1360x2048": "2:3",
    "768x1024": "3:4", "1536x2048": "3:4",
    "1536x1024": "3:2", "2048x1360": "3:2",
    "1024x768": "4:3", "2048x1536": "4:3",
    "1536x864": "16:9", "2048x1152": "16:9", "3840x2160": "16:9",
    "864x1536": "9:16", "1152x2048": "9:16", "2160x3840": "9:16",
    "2016x864": "21:9", "2688x1152": "21:9", "3840x1648": "21:9",
}
ENV_ALIASES = {
    "DREAMINA_IMAGE_MODEL": ("JIMENG_IMAGE_MODEL",),
    "DREAMINA_CANVAS_ID": ("JIMENG_CANVAS_ID",),
    "DREAMINA_RESOLUTION": ("JIMENG_RESOLUTION",),
    "DREAMINA_CREDIT_CEILING": ("JIMENG_CREDIT_CEILING",),
    "DREAMINA_BIN": ("JIMENG_BIN",),
}


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


def locate_dreamina() -> str:
    candidate = resolve_env("DREAMINA_BIN")
    if candidate:
        if Path(candidate).is_file():
            return candidate
        fail(f"DREAMINA_BIN 指向的文件不存在：{candidate}")
    found = shutil.which("dreamina-canvas") or shutil.which("dreamina-canvas.exe")
    if not found:
        fail(
            "找不到 dreamina-canvas CLI。请先安装并登录：\n"
            "  安装后运行 `dreamina-canvas auth login` 完成 OAuth 登录。"
        )
    return found


# ── dreamina-canvas CLI 封装 ────────────────────────────────

def run_cli(cli_bin: str, cli_args: list[str], timeout: int) -> dict:
    command = [cli_bin, *cli_args, "--format", "json"]
    try:
        completed = subprocess.run(
            command, capture_output=True, text=True, encoding="utf-8", errors="replace",
            timeout=timeout,
        )
    except FileNotFoundError:
        fail(f"无法执行 dreamina-canvas CLI：{cli_bin}")
    except subprocess.TimeoutExpired:
        fail(f"dreamina-canvas CLI 执行超时（{timeout}s）。可加大 --timeout 后重试。")
    if completed.returncode != 0:
        message = (completed.stderr or completed.stdout or "").strip()
        fail(f"dreamina-canvas 退出码 {completed.returncode}：{message[:1200]}")
    return parse_json_output(completed.stdout, "CLI 输出")


def parse_json_output(raw: str, context: str) -> dict:
    text = raw.strip()
    brace = text.find("{")
    if brace > 0:
        text = text[brace:]
    try:
        parsed = json.loads(text)
    except json.JSONDecodeError:
        fail(f"{context}不是有效 JSON：{raw[:500]}")
    if not isinstance(parsed, dict):
        fail(f"{context}格式不正确：顶层结果不是对象。")
    return parsed


def new_id() -> str:
    return str(uuid.uuid4())


# ── 画布解析 ──────────────────────────────────────────────

def resolve_canvas(cli_bin: str, canvas_id: str) -> str:
    if canvas_id:
        verify = run_cli(cli_bin, ["canvas", "use", canvas_id, "--yes"], timeout=60)
        project = (verify.get("data") or {}).get("currentCanvas") or (verify.get("data") or {}).get("project")
        resolved = (project or {}).get("projectId") or canvas_id
        log(f"[dreamina] 使用画布 {resolved}")
        return resolved
    current = run_cli(cli_bin, ["canvas", "current", "--yes"], timeout=60)
    canvas = ((current.get("data") or {}).get("currentCanvas") or {}).get("canvas") or {}
    if canvas.get("projectId"):
        log(f"[dreamina] 使用当前画布 {canvas['projectId']}")
        return canvas["projectId"]
    created = run_cli(
        cli_bin, ["canvas", "create", DEFAULT_CANVAS_NAME, "--use", "--yes"], timeout=120,
    )
    project = (created.get("data") or {}).get("project") or {}
    if not project.get("projectId"):
        fail(f"自动创建画布失败：{json.dumps(created, ensure_ascii=False)[:400]}")
    log(f"[dreamina] 已创建画布 {project['projectId']}（{project.get('webUrl', '')}）")
    return project["projectId"]


# ── 参考图上传 ──────────────────────────────────────────────

def upload_reference_images(cli_bin: str, project_id: str, image_paths: list[str]) -> list[str]:
    resource_ids: list[str] = []
    for image_path in image_paths:
        path = Path(image_path)
        if not path.is_file():
            fail(f"参考图片不存在：{image_path}")
        resource_id = new_id()
        log(f"[dreamina] 上传参考图 {path} ...")
        result = run_cli(
            cli_bin,
            ["resource", "upload", "--file", str(path), "--project-id", project_id,
             "--resource-id", resource_id, "--import-kind", "local_upload", "--yes"],
            timeout=300,
        )
        data = result.get("data") or {}
        uploaded = data.get("resource") or data
        rid = uploaded.get("resourceId") or resource_id
        wait_resource_ready(cli_bin, project_id, rid)
        resource_ids.append(rid)
        log(f"[dreamina] 参考图已登记: res:{rid}")
    return resource_ids


def wait_resource_ready(cli_bin: str, project_id: str, resource_id: str,
                        timeout_s: int = 180) -> None:
    deadline = time.monotonic() + timeout_s
    while time.monotonic() < deadline:
        result = run_cli(
            cli_bin, ["resource", "get", resource_id, "--project-id", project_id, "--yes"],
            timeout=60,
        )
        data = result.get("data") or {}
        resource = data.get("resource") or data
        status = str(resource.get("status", "")).lower()
        if status == "success":
            return
        if status == "failed":
            fail(f"参考图素材处理失败：{json.dumps(resource, ensure_ascii=False)[:400]}")
        time.sleep(3)
    fail(f"参考图素材 {resource_id} 在 {timeout_s}s 内未就绪。")


# ── 生成 ──────────────────────────────────────────────

def size_to_ratio(size: str) -> str:
    if ":" in size:
        ratio = size
    elif size.lower() in PIXEL_TO_RATIO:
        ratio = PIXEL_TO_RATIO[size.lower()]
    else:
        fail(f"无法识别尺寸 '{size}'。请使用比例格式（1:1、16:9、2:3 等）或 1024x1024 这类像素尺寸。")
    if ratio not in SUPPORTED_RATIOS:
        mapped = RATIO_FALLBACK.get(ratio)
        if not mapped:
            fail(f"模型不支持比例 {ratio}，且无自动换算。可用：{'、'.join(sorted(SUPPORTED_RATIOS))}")
        log(f"[dreamina] 比例 {ratio} 不被模型支持，已换算为 {mapped}。")
        ratio = mapped
    return ratio


def build_node_args(project_id: str, prompt: str, model: str, ratio: str,
                    resolution: str, count: int, ref_ids: list[str],
                    ceiling: int, title: str, submit_id: str) -> list[str]:
    cli_args = [
        "node", "create", "image",
        "--project-id", project_id,
        "--mode", "i2i" if ref_ids else "t2i",
        "--model", model,
        "--prompt", prompt,
        "--ratio", ratio,
        "--resolution", resolution,
        "--count", str(count),
        "--credit-ceiling", str(ceiling),
        "--title", title,
        "--submit-id", submit_id,
        "--run", "--wait",
        "--yes",
    ]
    for rid in ref_ids:
        cli_args += ["--ref", f"res:{rid}"]
    return cli_args


def generate_image(cli_bin: str, project_id: str, prompt: str, model: str, ratio: str,
                   resolution: str, count: int, ref_ids: list[str], ceiling: int,
                   timeout: int) -> tuple[list[str], str, str]:
    title = f"ecom-{time.strftime('%Y%m%d-%H%M%S')}"
    submit_id = new_id()
    mode = "i2i" if ref_ids else "t2i"
    log(f"[dreamina] 提交生成任务: model={model} mode={mode} ratio={ratio} "
        f"resolution={resolution} count={count} 积分上限={ceiling}，等待完成...")
    result = run_cli(cli_bin, build_node_args(
        project_id, prompt, model, ratio, resolution, count, ref_ids, ceiling, title, submit_id,
    ), timeout=timeout)
    node_id, resource_ids = extract_node_outputs(result)
    if not resource_ids and node_id:
        # --run --wait 的最终快照可能早于节点终态，改为显式轮询节点直到 success/failed。
        node_id, resource_ids = wait_for_node_outputs(cli_bin, project_id, node_id, timeout)
    if not resource_ids:
        fail(
            "生成节点未产出素材。"
            f" node_id={node_id or '未知'} submit_id={submit_id}，"
            f"原始输出：{json.dumps(result, ensure_ascii=False)[:600]}"
        )
    return resource_ids, node_id, submit_id


def wait_for_node_outputs(cli_bin: str, project_id: str, node_id: str,
                          timeout_s: int) -> tuple[str, list[str]]:
    deadline = time.monotonic() + max(60, timeout_s)
    last_status = ""
    while time.monotonic() < deadline:
        result = run_cli(
            cli_bin, ["node", "show", "--node-id", node_id, "--project-id", project_id, "--yes"],
            timeout=60,
        )
        nodes = ((result.get("data") or {}).get("nodes")) or []
        node = next(
            (entry.get("node") or {} for entry in nodes if (entry.get("node") or {}).get("nodeId") == node_id),
            {},
        )
        last_status = str(node.get("status", "")).lower()
        resource_ids = [
            resource.get("resourceId")
            for resource in node.get("resources") or []
            if resource.get("resourceId") and str(resource.get("status", "")).lower() == "success"
        ]
        if resource_ids:
            return node_id, resource_ids
        if last_status == "failed":
            fail(f"生成节点失败：{json.dumps(node, ensure_ascii=False)[:600]}")
        time.sleep(5)
    fail(f"节点 {node_id} 在 {timeout_s}s 内未进入终态（最后状态：{last_status or 'unknown'}）。")


def extract_node_outputs(result: dict) -> tuple[str, list[str]]:
    data = result.get("data") or {}
    node = data.get("node") or {}
    node_id = node.get("nodeId", "")
    resource_ids: list[str] = []
    for resource in node.get("resources") or []:
        rid = resource.get("resourceId")
        status = str(resource.get("status", "")).lower()
        if rid and status in {"", "success"}:
            resource_ids.append(rid)
    return node_id, resource_ids


# ── 下载 ──────────────────────────────────────────────

def download_resources(cli_bin: str, project_id: str, resource_ids: list[str],
                       output_dir: Path, fmt: str) -> list[Path]:
    output_dir.mkdir(parents=True, exist_ok=True)
    timestamp = time.strftime("%Y%m%d-%H%M%S")
    paths: list[Path] = []
    for index, rid in enumerate(resource_ids, start=1):
        output_path = output_dir / f"image-{timestamp}-{index:02d}.{fmt}"
        log(f"  下载图片 res:{rid} ...")
        run_cli(
            cli_bin,
            ["resource", "download", rid, "--project-id", project_id,
             "--output", str(output_path), "--yes"],
            timeout=300,
        )
        if not output_path.is_file():
            fail(f"下载后未找到文件：{output_path}")
        paths.append(output_path)
    return paths


# ── CLI ──────────────────────────────────────────────

def parse_args():
    parser = argparse.ArgumentParser(
        description="通过 dreamina-canvas CLI（即梦）生成图片，默认模型 Seedream 5.5。"
    )
    prompt_group = parser.add_mutually_exclusive_group(required=True)
    prompt_group.add_argument("--prompt", help="直接传入图片生成 Prompt。")
    prompt_group.add_argument("--prompt-file", help="从文本文件读取图片生成 Prompt。")
    parser.add_argument("--output-dir", default="generated-images",
                        help="图片输出目录，默认 generated-images。")
    parser.add_argument("--env-file", help="指定 .env 配置文件；不指定时从当前目录向上查找（可选）。")
    parser.add_argument("--model", help=f"即梦图片模型 id，默认 {DEFAULT_MODEL}（可用 DREAMINA_IMAGE_MODEL 覆盖）。")
    parser.add_argument("--size", default="1:1",
                        help="图片比例，默认 1:1；不支持的比例如 4:5 会自动换算到最接近的支持比例。")
    parser.add_argument("--resolution", choices=("1.5K", "2K"),
                        help=f"分辨率，默认 {DEFAULT_RESOLUTION}（可用 DREAMINA_RESOLUTION 覆盖）。")
    parser.add_argument("--image", action="append", default=[],
                        help="本地参考产品图片路径，可重复传入（最多 10 张），上传后走图生图。")
    parser.add_argument("--image-url", help="参考图公网 URL（仅支持单张；多参考图请用 --image）。")
    parser.add_argument("--count", type=int, default=1, help="单节点生成数量，1-8，默认 1。")
    parser.add_argument("--canvas-id", help="目标画布 UUID；默认用 DREAMINA_CANVAS_ID、当前画布或自动创建。")
    parser.add_argument("--credit-ceiling", type=int,
                        help=f"单节点积分消费上限，默认 {DEFAULT_CREDIT_CEILING}（可用 DREAMINA_CREDIT_CEILING 覆盖）。")
    parser.add_argument("--timeout", type=int, default=600,
                        help="单个生成任务等待上限秒数，默认 600。")
    parser.add_argument("--format", choices=("png", "jpeg", "webp"), default="png",
                        help="保存格式的默认扩展名，默认 png。")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    env_file = Path(args.env_file) if args.env_file else find_default_env_file()
    load_env_file(env_file)
    prompt = read_prompt(args)

    cli_bin = locate_dreamina()
    model = args.model or resolve_env("DREAMINA_IMAGE_MODEL") or DEFAULT_MODEL
    resolution = args.resolution or resolve_env("DREAMINA_RESOLUTION") or DEFAULT_RESOLUTION
    ceiling = args.credit_ceiling or int(resolve_env("DREAMINA_CREDIT_CEILING") or DEFAULT_CREDIT_CEILING)
    ratio = size_to_ratio(args.size)
    canvas_id = args.canvas_id or resolve_env("DREAMINA_CANVAS_ID") or ""

    if not 1 <= args.count <= 8:
        fail("--count 取值范围 1-8。")
    if len(args.image) > 10:
        fail("参考图最多 10 张。")

    project_id = resolve_canvas(cli_bin, canvas_id)

    ref_ids: list[str] = []
    if args.image:
        ref_ids = upload_reference_images(cli_bin, project_id, args.image)
    elif args.image_url:
        # 公网 URL 单张参考图：同样登记为画布素材，保持 i2i 引用一致。
        result = run_cli(
            cli_bin,
            ["resource", "upload", "--source-url", args.image_url, "--project-id", project_id,
             "--resource-id", new_id(), "--import-kind", "external_generated", "--yes"],
            timeout=300,
        )
        data = result.get("data") or {}
        uploaded = data.get("resource") or data
        rid = uploaded.get("resourceId")
        if not rid:
            fail(f"URL 参考图登记失败：{json.dumps(result, ensure_ascii=False)[:400]}")
        wait_resource_ready(cli_bin, project_id, rid)
        ref_ids = [rid]
        log(f"[dreamina] URL 参考图已登记: res:{rid}")

    resource_ids, node_id, submit_id = generate_image(
        cli_bin, project_id, prompt, model, ratio, resolution, args.count, ref_ids, ceiling, args.timeout,
    )
    log(f"[dreamina] 生成完成 node_id={node_id} submit_id={submit_id}")
    paths = download_resources(cli_bin, project_id, resource_ids, Path(args.output_dir), args.format)

    print("生成完成：")
    for path in paths:
        print(path)


if __name__ == "__main__":
    main()
