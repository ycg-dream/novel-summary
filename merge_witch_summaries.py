"""
merge_witch_summaries.py
合并 27 份 part 摘要 + 生成最终的全书摘要汇总文件
"""
# -*- coding: utf-8 -*-
import os
import sys

# 让 stdout 在 Windows 控制台能正确输出 UTF-8
try:
    sys.stdout.reconfigure(encoding='utf-8')
except AttributeError:
    pass

WORK_DIR = r'H:\搜书吧'
NOVEL_NAME = '《放开那个女巫》 10.0 改 加料（作者：二目 / 惘离 10.0 改）'
OUT_NAME = '全书摘要汇总.md'
OUT_PATH = os.path.join(WORK_DIR, OUT_NAME)


def main():
    print('=== merge_witch_summaries.py 启动 ===', flush=True)

    # 收集所有 part 摘要
    part_files = []
    for f in sorted(os.listdir(WORK_DIR)):
        if f.startswith('witch_summary_part_') and f.endswith('.md'):
            part_files.append(os.path.join(WORK_DIR, f))

    if not part_files:
        print('!! 未找到 part 摘要文件', flush=True)
        return

    print(f'找到 {len(part_files)} 个 part 摘要', flush=True)

    # 计算总字符数
    total_chars = 0
    for pf in part_files:
        with open(pf, 'r', encoding='utf-8') as f:
            total_chars += len(f.read())

    print(f'摘要总字符数：{total_chars}', flush=True)

    # 写汇总文件
    with open(OUT_PATH, 'w', encoding='utf-8') as out:
        out.write(f'# {NOVEL_NAME} 全书摘要汇总\n\n')
        out.write(f'**生成方式**：LLM 生成式摘要（按章节切分为 27 个 part，由子 Agent 独立读全文后撰写，主 Agent 汇总）\n\n')
        out.write(f'**总 part 数**：{len(part_files)}\n\n')
        out.write(f'**摘要总字符数**：{total_chars} 字符\n\n')
        out.write(f'**每个 part 包含 6 大模块**：核心主线、关键剧情节点（8-25 条）、新增人物、世界观/设定扩充、政治格局变化、伏笔/未解线索\n\n')
        out.write('---\n\n')

        for i, pf in enumerate(part_files, 1):
            with open(pf, 'r', encoding='utf-8') as f:
                content = f.read().strip()
            out.write(content)
            out.write('\n\n---\n\n')

    print(f'已生成：{OUT_PATH}', flush=True)
    print(f'文件大小：{os.path.getsize(OUT_PATH)} 字节', flush=True)
    print('=== merge_witch_summaries.py 完成 ===', flush=True)


if __name__ == '__main__':
    main()
