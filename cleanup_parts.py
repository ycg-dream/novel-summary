"""
cleanup_parts.py
合并完成后清理 27 个 part 临时文件
- 仅删除 part_NNN.txt（每份约 600 KB，共释放 ~16 MB）
- 保留 part_NNN_summary.md 摘要文件
- 保留合并后的 全书摘要汇总.md
- 保留所有 .py 脚本和 .md 进度笔记

调用：
    python cleanup_parts.py
    python cleanup_parts.py --prefix my_novel_part_  # 自定义前缀
"""
# -*- coding: utf-8 -*-
import os
import re
import sys

try:
    sys.stdout.reconfigure(encoding='utf-8')
except AttributeError:
    pass

DEFAULT_PREFIX = 'witch_part_'
WORK_DIR = r'H:\搜书吧'


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


def main(prefix=None, work_dir=None):
    if prefix is None:
        prefix = DEFAULT_PREFIX
    if work_dir is None:
        work_dir = WORK_DIR

    safe_print('=== cleanup_parts.py 启动 ===')
    safe_print('工作目录: ' + work_dir)
    safe_print('匹配前缀: {}\\d+\\.txt'.format(prefix))

    # 找匹配文件
    matches = []
    total_size = 0
    pattern = re.compile(r'^{}\d+\.txt$'.format(re.escape(prefix)))
    for f in os.listdir(work_dir):
        if pattern.match(f):
            path = os.path.join(work_dir, f)
            size = os.path.getsize(path)
            matches.append((f, size))
            total_size += size

    if not matches:
        safe_print('未找到匹配文件，无需清理')
        return 0

    safe_print('找到 {} 个 part 临时文件，总大小 {:.1f} MB'.format(
        len(matches), total_size / 1024 / 1024))

    # 询问用户（避免误删）
    safe_print('即将删除以下文件:')
    for fname, size in sorted(matches):
        safe_print('  {} ({:.1f} KB)'.format(fname, size / 1024))

    if '--yes' not in sys.argv and '-y' not in sys.argv:
        try:
            answer = input('\n确认删除？(y/N): ').strip().lower()
        except EOFError:
            answer = 'n'
        if answer != 'y':
            safe_print('取消删除')
            return 0

    # 删除
    deleted = 0
    deleted_size = 0
    for fname, size in matches:
        try:
            os.remove(os.path.join(work_dir, fname))
            deleted += 1
            deleted_size += size
        except Exception as e:
            safe_print('!! 删除失败: {} {}'.format(fname, e))

    safe_print('已删除 {} 个文件，释放 {:.1f} MB'.format(
        deleted, deleted_size / 1024 / 1024))
    safe_print('保留: 全书摘要汇总.md + part_*_summary.md + 脚本 + 进度笔记')
    safe_print('=== cleanup_parts.py 完成 ===')


if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('--prefix', default=DEFAULT_PREFIX, help='part 文件名前缀')
    parser.add_argument('--work-dir', default=WORK_DIR, help='工作目录')
    parser.add_argument('--yes', '-y', action='store_true', help='跳过确认')
    args = parser.parse_args()
    main(prefix=args.prefix, work_dir=args.work_dir)
