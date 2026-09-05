import re


def extract_artifacts(text: str) -> list[dict]:
    """
    Extract <artifact> blocks from an LLM response.
    """

    artifacts = []

    pattern = re.compile(
        r'<artifact\s+type="(markdown|html)"'
        r'(?:\s+title="([^"]*)")?'
        r'>(.*?)</artifact>',
        re.DOTALL | re.IGNORECASE,
    )

    for match in pattern.finditer(text):
        artifact_type = match.group(1).lower()
        title = match.group(2) or "Generated Artifact"
        content = match.group(3).strip()

        if not content:
            continue

        artifacts.append(
            {
                "artifact_type": artifact_type,
                "title": title,
                "content": content,
            }
        )

    return artifacts


def remove_artifact_blocks(text: str) -> str:
    """
    Remove artifact blocks from the normal chat response.
    """

    pattern = re.compile(
        r'<artifact\s+type="(markdown|html)"'
        r'(?:\s+title="([^"]*)")?'
        r'>(.*?)</artifact>',
        re.DOTALL | re.IGNORECASE,
    )

    return pattern.sub("", text).strip()


def is_html_artifact_request(message: str) -> bool:
    """
    Detect requests that explicitly ask for an HTML artifact.
    """

    lower_message = message.lower()

    html_phrases = [
        "html",
        "html page",
        "html artifact",
        "webpage",
        "web page",
        "landing page",
        "website",
        "complete html",
    ]

    return any(
        phrase in lower_message
        for phrase in html_phrases
    )