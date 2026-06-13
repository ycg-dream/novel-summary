"""
split_novel2.py
将 537 万字长篇小说《放开那个女巫》按 20 万字/部分切分，输出 part_NNN.txt
- 读取 UTF-16-LE 编码源文件
- 写入 UTF-8 编码 part 文件
- 尽量在章节边界切分（不硬切）
- 编号 001-027
"""
# -*- coding: utf-8 -*-
import os
import re
import sys

WORK_DIR = r'H:\搜书吧'
NOVEL_NAME = '放开那个女巫 10.0改加料.txt'
NOVEL_PATH = os.path.join(WORK_DIR, NOVEL_NAME)
PART_SIZE = 200000  # 20 万字/部分
OUT_PREFIX = 'witch_part_'

# 章节标题：第 NNNN 章 ...（如 第0001章从今天开始做王子）
CHAPTER_RE = re.compile(r'第[0-9零一二三四五六七八九十百千]+章[^\n]*')


def safe_print(s):
    try:
        sys.stdout.write(s + '\n')
        sys.stdout.flush()
    except Exception:
        try:
            sys.stdout.buffer.write((s + '\n').encode('utf-8', errors='replace'))
            sys.stdout.buffer.flush()
        except Exception:
            pass


def main():
    safe_print('=== split_novel2.py 启动 ===')
    safe_print('源文件: ' + NOVEL_PATH)
    safe_print('每部分目标: {} 字符'.format(PART_SIZE))

    # 检测编码
    with open(NOVEL_PATH, 'rb') as f:
        head = f.read(2)
    if head == b'\xff\xfe':
        enc = 'utf-16-le'
    elif head == b'\xfe\xff':
        enc = 'utf-16-be'
    else:
        enc = 'utf-8'
    safe_print('检测编码: {}'.format(enc))

    with open(NOVEL_PATH, 'r', encoding=enc) as f:
        text = f.read()

    total_chars = len(text)
    safe_print('总字符数: {}'.format(total_chars))

    # 找所有章节起点
    chapter_starts = []
    for m in CHAPTER_RE.finditer(text):
        chapter_starts.append(m.start())
    safe_print('检测到 {} 个章节'.format(len(chapter_starts)))

    # 切分点
    splits = []  # list of (start_offset, end_offset)
    cur = 0
    while cur < total_chars:
        ideal_end = cur + PART_SIZE
        if ideal_end >= total_chars:
            splits.append((cur, total_chars))
            break
        # 在 [cur + PART_SIZE*0.85, cur + PART_SIZE*1.15] 范围内找最近的章节起点
        lo = cur + int(PART_SIZE * 0.85)
        hi = cur + int(PART_SIZE * 1.15)
        # 找在 [lo, hi] 内最接近 ideal_end 的章节起点
        candidates = [s for s in chapter_starts if lo <= s <= hi]
        if candidates:
            chosen = min(candidates, key=lambda s: abs(s - ideal_end))
        else:
            # 退而求其次，找 [cur+PART_SIZE*0.5, ideal_end+50%] 内的
            lo2 = cur + int(PART_SIZE * 0.5)
            hi2 = cur + int(PART_SIZE * 1.3)
            candidates = [s for s in chapter_starts if lo2 <= s <= hi2]
            if candidates:
                chosen = min(candidates, key=lambda s: abs(s - ideal_end))
            else:
                # 实在没有就硬切
                chosen = ideal_end
        splits.append((cur, chosen))
        cur = chosen
    safe_print('切分为 {} 个 part'.format(len(splits)))

    # 删除旧 part
    for f in os.listdir(WORK_DIR):
        m = re.match(r'witch_part_\d+\.txt$', f)
        if m:
            try:
                os.remove(os.path.join(WORK_DIR, f))
            except Exception as e:
                safe_print('!! 删除旧 part 失败: {} {}'.format(f, e))

    # 写文件
    written = []
    for i, (s, e) in enumerate(splits):
        idx = i + 1
        fname = '{}{:03d}.txt'.format(OUT_PREFIX, idx)
        fpath = os.path.join(WORK_DIR, fname)
        content = text[s:e]
        with open(fpath, 'w', encoding='utf-8') as f:
            f.write(content)
        written.append((fname, len(content), s, e))

    # 报告
    for fname, size, s, e in written:
        # 找这个 part 包含的章节范围
        chs = [cs for cs in chapter_starts if s <= cs < e]
        if chs:
            first_ch = CHAPTER_RE.match(text[chs[0]:chs[0]+30])
            last_ch = CHAPTER_RE.match(text[chs[-1]:chs[-1]+30])
            range_str = '{} - {}'.format(
                first_ch.group() if first_ch else '?',
                last_ch.group() if last_ch else '?'
            )
        else:
            range_str = '?'
        safe_print('  {}  {} 字  范围: 字符[{}, {}]  章节: {}'.format(
            fname, size, s, e, range_str))

    safe_print('=== split_novel2.py 完成，共 {} 个 part ==='.format(len(written)))
    return len(written), written


if __name__ == '__main__':
    main()
