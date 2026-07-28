#!/usr/bin/env python3
"""
HIC Wiki Emoji 清除工具

逐个扫描文档中的 emoji，逐文件确认后清除。
"""

import re
import os
import sys

# Emoji 匹配模式（标准 Unicode emoji 范围）
EMOJI_PATTERN = re.compile(
    '[\U0001F600-\U0001F64F'   # Emoticons
    '\U0001F300-\U0001F5FF'    # Misc Symbols and Pictographs
    '\U0001F680-\U0001F6FF'    # Transport and Map
    '\U0001F1E0-\U0001F1FF'    # Regional indicator flags
    '\U0001F900-\U0001F9FF'    # Supplemental Symbols and Pictographs
    '\U0001FA00-\U0001FA6F'    # Chess Symbols
    '\U0001FA70-\U0001FAFF'    # Symbols Extended-A
    '\U00002702-\U000027B0'    # Dingbats
    '\U00002600-\U000026FF'    # Misc symbols
    '\U0000FE00-\U0000FE0F'    # Variation selectors
    '\U0000200D\U00002B50\U00002764\U0000203C\U00002049'
    '\U00002139\U0000231A-\U0000231B\U000023E9-\U000023F3'
    '\U000025AA-\U000025AB\U000025B6\U000025C0\U000025FB-\U000025FE'
    '\U0000260E\U00002611\U00002614-\U00002615\U00002618\U0000261D'
    '\U00002620-\U00002622\U00002624-\U00002628\U0000262A-\U0000263A'
    '\U00002640-\U00002642\U00002648-\U00002653\U00002654-\U0000265F'
    '\U00002660-\U00002667\U00002668-\U0000266F\U00002670-\U0000267F'
    '\U00002680-\U0000268A\U00002690-\U00002697\U00002699-\U0000269C'
    '\U000026A0-\U000026A1\U000026AA-\U000026AB\U000026B0-\U000026B1'
    '\U000026BD-\U000026BE\U000026C4-\U000026C5\U000026CE'
    '\U000026D0-\U000026D4\U000026E8-\U000026EA\U000026F0-\U000026F5'
    '\U000026F7-\U000026FA\U000026FD\U00002701-\U00002702'
    '\U00002708-\U0000270F\U00002712-\U00002714\U00002716\U0000271D'
    '\U00002721-\U00002722\U00002733-\U00002734\U00002744\U00002747'
    '\U0000274C\U0000274E\U00002753-\U00002755\U00002757'
    '\U00002760-\U00002764\U00002795-\U00002797\U000027A1\U000027B0'
    '\U000027BF\U00002B05-\U00002B07\U00002B1B-\U00002B1C\U00002B50'
    '\U00002B55\U00003030\U0000303D\U00003297\U00003299\U0000FE0F\U0000FE0E'
    ']', re.UNICODE
)

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def find_emoji(content: str) -> list[tuple[int, str, str]]:
    """返回 [(行号, emoji字符, 所在行内容), ...]"""
    results = []
    for i, line in enumerate(content.splitlines(), 1):
        emojis = EMOJI_PATTERN.findall(line)
        if emojis:
            for e in emojis:
                results.append((i, e, line.strip()))
    return results


def remove_emoji(content: str) -> str:
    return EMOJI_PATTERN.sub('', content)


def format_preview(line: str) -> str:
    """将行中的 emoji 用高亮标记包裹显示"""
    def replacer(m):
        return f'\033[41m{m.group()}\033[0m'
    return EMOJI_PATTERN.sub(replacer, line)


def main():
    md_files = []
    for root, dirs, files in os.walk(os.path.join(BASE_DIR, 'docs')):
        for f in sorted(files):
            if f.endswith('.md'):
                md_files.append(os.path.join(root, f))

    total_cleaned = 0
    total_skipped = 0

    print(f'找到 {len(md_files)} 个 Markdown 文件\n')
    print('─' * 60)

    for filepath in md_files:
        relpath = os.path.relpath(filepath, BASE_DIR)
        content = open(filepath, encoding='utf-8').read()
        hits = find_emoji(content)

        if not hits:
            print(f'  ✓ {relpath}  无 emoji')
            continue

        print(f'\n  ▶ {relpath}')
        print(f'    发现 {len(hits)} 个 emoji:')
        for lineno, emoji, line in hits:
            highlighted = format_preview(line)
            print(f'      L{lineno:4d}  {highlighted}')

        while True:
            answer = input(f'\n  清除以上 emoji？[Y/n/q] ').strip().lower()
            if answer in ('', 'y', 'yes'):
                cleaned = remove_emoji(content)
                open(filepath, 'w', encoding='utf-8').write(cleaned)
                print(f'  ✓ 已清除')
                total_cleaned += 1
                break
            elif answer in ('n', 'no'):
                print(f'  - 跳过')
                total_skipped += 1
                break
            elif answer in ('q', 'quit'):
                print(f'\n  退出。')
                print(f'\n{"─" * 60}')
                print(f'总计: {total_cleaned} 个文件已清除, {total_skipped} 个跳过')
                sys.exit(0)
            else:
                print(f'  请输入 Y/n/q')

        print('─' * 60)

    print(f'\n全部完成: {total_cleaned} 个文件已清除, {total_skipped} 个跳过')


if __name__ == '__main__':
    main()
