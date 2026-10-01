#!/usr/bin/env python3
"""根据 GitHub 贡献日历生成一张静态活动折线图 SVG。

数据来源：GitHub GraphQL API 的 contributionsCollection.contributionCalendar
输出文件：activity-graph.svg（默认写在仓库根目录）

环境变量
--------
GH_USERNAME     GitHub 用户名。依次回退：GH_USERNAME -> GITHUB_USERNAME ->
                GITHUB_REPOSITORY_OWNER（Actions 自动注入）
GITHUB_TOKEN    读取公开贡献数据只需 Actions 内置的 GITHUB_TOKEN 即可。
                也支持 GH_TOKEN 作为回退。
MAX_DAYS        绘制最近多少天的数据，默认 90
OUTPUT_PATH     输出路径，默认 activity-graph.svg
THEME           dark（默认，xcode 风格暗色）或 light

命令行
------
python scripts/generate_activity_graph.py --username Huaxidesu --theme dark
"""

from __future__ import annotations

import argparse
import os
import sys

import requests

GRAPHQL_URL = "https://api.github.com/graphql"

QUERY = """
query($login: String!) {
  user(login: $login) {
    contributionsCollection {
      contributionCalendar {
        weeks {
          contributionDays {
            contributionCount
            date
          }
        }
      }
    }
  }
}
"""

THEMES = {
    "dark": {
        "bg": "#0d1117",
        "border": "#30363d",
        "grid": "#21262d",
        "line": "#58a6ff",
        "area": "rgba(56, 139, 253, 0.20)",
        "text": "#8b949e",
        "title": "#c9d1d9",
    },
    "light": {
        "bg": "#ffffff",
        "border": "#d0d7de",
        "grid": "#eaeef2",
        "line": "#0969da",
        "area": "rgba(9, 105, 218, 0.15)",
        "text": "#57606a",
        "title": "#24292f",
    },
}

WIDTH = 1000
HEIGHT = 250
PADDING = 40


def resolve_username() -> str | None:
    """按优先级解析用户名，避开 Windows 自带的 USERNAME 环境变量。"""
    for key in ("GH_USERNAME", "GITHUB_USERNAME", "GITHUB_REPOSITORY_OWNER"):
        value = (os.getenv(key) or "").strip()
        if value:
            return value
    return None


def resolve_token() -> str | None:
    for key in ("GITHUB_TOKEN", "GH_TOKEN"):
        value = (os.getenv(key) or "").strip()
        if value:
            return value
    return None


def fetch_contributions(username: str, token: str, timeout: int = 30):
    """拉取贡献日历，返回 [(日期, 贡献数), ...]，按时间从早到晚。"""
    headers = {
        "Authorization": "bearer %s" % token,
        "Accept": "application/vnd.github+json",
    }
    response = requests.post(
        GRAPHQL_URL,
        json={"query": QUERY, "variables": {"login": username}},
        headers=headers,
        timeout=timeout,
    )
    response.raise_for_status()
    payload = response.json()

    if payload.get("errors"):
        raise RuntimeError("GraphQL error: %s" % payload["errors"])

    user = (payload.get("data") or {}).get("user")
    if not user:
        raise RuntimeError("用户 %r 不存在或没有可读取的数据" % username)

    weeks = user["contributionsCollection"]["contributionCalendar"]["weeks"]
    days = []
    for week in weeks:
        for day in week["contributionDays"]:
            days.append((day["date"], day["contributionCount"]))
    return days


def build_svg(days, username: str, theme: str = "dark",
              width: int = WIDTH, height: int = HEIGHT, padding: int = PADDING) -> str:
    """把 [(日期, 贡献数), ...] 渲染成 SVG 字符串。"""
    if not days:
        raise ValueError("没有可绘制的贡献数据")

    colors = THEMES.get(theme, THEMES["dark"])
    counts = [count for _, count in days]
    total = sum(counts)
    n = len(counts)
    max_count = max(counts) or 1

    baseline = height - padding
    plot_height = height - 2 * padding
    step_x = (width - 2 * padding) / (n - 1) if n > 1 else 0.0

    points = []
    for i, count in enumerate(counts):
        x = padding + i * step_x
        y = baseline - (count / max_count) * plot_height
        points.append((x, y))

    polyline_points = " ".join("%.2f,%.2f" % (x, y) for x, y in points)
    last_x = padding + (n - 1) * step_x
    area_path = "M %.2f,%.2f L %s L %.2f,%.2f Z" % (
        padding, baseline, polyline_points.replace(" ", " L "), last_x, baseline,
    )
    circles = "\n".join(
        '    <circle cx="%.2f" cy="%.2f" r="3" fill="%s" />' % (x, y, colors["line"])
        for x, y in points
    )

    grid_lines = []
    for fraction in (0.0, 0.5, 1.0):
        gy = baseline - fraction * plot_height
        grid_lines.append(
            '    <line x1="%.2f" y1="%.2f" x2="%.2f" y2="%.2f" stroke="%s" stroke-width="1" />'
            % (padding, gy, width - padding, gy, colors["grid"])
        )
        grid_lines.append(
            '    <text x="%.2f" y="%.2f" text-anchor="end">%d</text>'
            % (padding - 8, gy + 4, round(fraction * max_count))
        )
    grid = "\n".join(grid_lines)

    title = "GitHub Activity (Last %d Days) - %s" % (n, username)
    subtitle = "%s ~ %s   ·   共 %d 次贡献   ·   单日最高 %d" % (
        days[0][0], days[-1][0], total, max(counts),
    )

    return """<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}" role="img" aria-label="{title}">
  <title>{title}</title>
  <desc>{subtitle}</desc>
  <style>
    text {{ fill: {text}; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Helvetica, Arial, sans-serif; font-size: 14px; }}
    .title {{ fill: {title_color}; font-size: 15px; font-weight: 600; }}
    .subtitle {{ fill: {text}; font-size: 12px; }}
    .axis {{ stroke: {border}; stroke-width: 1; }}
    .area {{ fill: {area}; }}
    .line {{ fill: none; stroke: {line}; stroke-width: 2; stroke-linejoin: round; stroke-linecap: round; }}
  </style>
  <rect width="100%" height="100%" rx="10" ry="10" fill="{bg}" stroke="{border}" />
  <text class="title" x="{padding}" y="{title_y}">{title}</text>
  <text class="subtitle" x="{padding}" y="{subtitle_y}">{subtitle}</text>
{grid}
  <line class="axis" x1="{padding}" y1="{baseline}" x2="{right}" y2="{baseline}" />
  <line class="axis" x1="{padding}" y1="{padding}" x2="{padding}" y2="{baseline}" />
  <path class="area" d="{area_path}" />
  <polyline class="line" points="{polyline_points}" />
{circles}
</svg>
""".format(
        width=width, height=height,
        title=title, subtitle=subtitle,
        text=colors["text"], title_color=colors["title"], border=colors["border"],
        bg=colors["bg"], area=colors["area"], line=colors["line"],
        padding=padding, baseline=baseline, right=width - padding,
        title_y=padding - 22, subtitle_y=padding - 6,
        grid=grid, area_path=area_path, polyline_points=polyline_points, circles=circles,
    )


def main() -> int:
    parser = argparse.ArgumentParser(description="Generate a GitHub activity graph SVG.")
    parser.add_argument("--username", help="GitHub 用户名，默认取环境变量")
    parser.add_argument("--theme", default=os.getenv("THEME", "dark"), choices=sorted(THEMES))
    parser.add_argument("--max-days", type=int, default=int(os.getenv("MAX_DAYS", "90")))
    parser.add_argument("--output", default=os.getenv("OUTPUT_PATH", "activity-graph.svg"))
    args = parser.parse_args()

    username = args.username or resolve_username()
    token = resolve_token()

    if not username:
        print("Error: 缺少用户名，请设置 GH_USERNAME 或使用 --username。", file=sys.stderr)
        return 1
    if not token:
        print("Error: 缺少 GITHUB_TOKEN。", file=sys.stderr)
        return 1

    try:
        all_days = fetch_contributions(username, token)
    except Exception as exc:  # noqa: BLE001 - 顶层统一兜底，保证 Action 日志可读
        print("Error fetching data: %s" % exc, file=sys.stderr)
        return 1

    max_days = max(args.max_days, 1)
    days = all_days[-max_days:] if len(all_days) >= max_days else all_days
    if not days:
        print("No contribution data found.", file=sys.stderr)
        return 1

    svg = build_svg(days, username, theme=args.theme)

    output_path = args.output
    parent = os.path.dirname(os.path.abspath(output_path))
    if parent and not os.path.isdir(parent):
        os.makedirs(parent, exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as handle:
        handle.write(svg)

    print("Successfully generated %s (%d days, %d contributions)"
          % (output_path, len(days), sum(c for _, c in days)))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
