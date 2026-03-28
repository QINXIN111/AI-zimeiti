"""内容格式化工具 - Markdown 转 HTML"""


def markdown_to_html(markdown: str, platform: str = "wechat") -> str:
    """将 Markdown 文本转换为 HTML，适配不同平台

    Args:
        markdown: Markdown 格式的文本
        platform: 目标平台 (wechat/xiaohongshu/douyin)

    Returns:
        HTML 格式的文本
    """
    if not markdown:
        return ""

    # 简单的 Markdown 解析（避免引入额外依赖）
    html = markdown

    # 标题处理
    html = html.replace("### ", "<h3>").replace("\n", "</h3>\n", 1)
    html = html.replace("## ", "<h2>").replace("\n", "</h2>\n", 1)
    html = html.replace("# ", "<h1>").replace("\n", "</h1>\n", 1)

    # 加粗 **text** -> <strong>text</strong>
    import re
    html = re.sub(r'\*\*(.*?)\*\*', r'<strong>\1</strong>', html)

    # 斜体 *text* -> <em>text</em>
    html = re.sub(r'\*(.*?)\*', r'<em>\1</em>', html)

    # 换行 -> <br>
    html = html.replace("\n\n", "</p><p>")
    html = html.replace("\n", "<br>")

    # 段落包裹
    html = f"<p>{html}</p>"

    # 根据平台适配
    if platform == "xiaohongshu":
        # 小红书只支持基础样式，去掉不支持的标签
        html = html.replace("<h1>", "<strong>").replace("</h1>", "</strong>")
        html = html.replace("<h2>", "<strong>").replace("</h2>", "</strong>")
        html = html.replace("<h3>", "<strong>").replace("</h3>", "</strong>")
        html = html.replace("<em>", "").replace("</em>", "")

    elif platform == "douyin":
        # 抖音类似小红书，只保留基础样式
        html = html.replace("<h1>", "<strong>").replace("</h1>", "</strong>")
        html = html.replace("<h2>", "<strong>").replace("</h2>", "</strong>")
        html = html.replace("<h3>", "<strong>").replace("</h3>", "</strong>")
        html = html.replace("<em>", "").replace("</em>", "")

    # 微信公众号支持完整 HTML，不做额外处理

    return html


def is_markdown(text: str) -> bool:
    """检查文本是否是 Markdown 格式"""
    if not text:
        return False
    markdown_indicators = ["# ", "## ", "### ", "**", "* ", "- ", "1. "]
    return any(indicator in text for indicator in markdown_indicators)
