"""
diagnose_novel.py
文本质量诊断 - 在切分前调用，识别常见问题
- 编码检测（GBK / UTF-8 / UTF-16）
- 章节结构（数、卷数、连续性、缺失）
- 广告/书友群/下载推广
- 屏蔽词/敏感词
- 错别字/谐音字
- 重复行/灌水

调用：
    python diagnose_novel.py
    python diagnose_novel.py --path /path/to/novel.txt
    python diagnose_novel.py --path novel.txt --save  # 报告保存到 diagnose_report.md
"""
# -*- coding: utf-8 -*-
import os
import re
import sys
import glob
import argparse

try:
    sys.stdout.reconfigure(encoding='utf-8')
except AttributeError:
    pass

CHINESE_NUMS = '零一二三四五六七八九十百千万'

CN_DIGIT_MAP = {
    '零': 0, '一': 1, '二': 2, '三': 3, '四': 4, '五': 5,
    '六': 6, '七': 7, '八': 8, '九': 9, '十': 10, '百': 100, '千': 1000,
}


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


def parse_chinese_num(s):
    """把中文数字字符串转 int，支持一/二/十/百/千 组合。"""
    if s.isdigit():
        return int(s)
    if s in CN_DIGIT_MAP:
        return CN_DIGIT_MAP[s]
    if '百' in s:
        parts = s.split('百')
        result = CN_DIGIT_MAP.get(parts[0], 1) * 100
        if len(parts) > 1 and parts[1]:
            tail = parts[1]
            if '十' in tail:
                tens = tail.split('十')
                result += CN_DIGIT_MAP.get(tens[0], 1) * 10
                if len(tens) > 1 and tens[1]:
                    result += CN_DIGIT_MAP.get(tens[1], 0)
            else:
                result += CN_DIGIT_MAP.get(tail, 0)
        return result
    if '十' in s:
        parts = s.split('十')
        result = CN_DIGIT_MAP.get(parts[0], 1) * 10
        if len(parts) > 1 and parts[1]:
            result += CN_DIGIT_MAP.get(parts[1], 0)
        return result
    return None


def detect_encoding(path):
    """自动检测文本编码：UTF-16 / UTF-8 / GBK

    策略：
    1. 看 BOM（前 2-3 字节）
    2. 在多个 offset（绕过 ASCII 头部）测试候选编码
    3. 选能完整解码的（按优先级 UTF-8 → GBK → GB18030）
    """
    with open(path, 'rb') as f:
        head = f.read(2)
    if head == b'\xff\xfe':
        return 'utf-16-le'
    elif head == b'\xfe\xff':
        return 'utf-16-be'

    # 头部可能是 ASCII（如标题/作者），所以要在多个 offset 测试
    with open(path, 'rb') as f:
        data = f.read()
    if not data:
        return 'utf-8'

    # 跳过文件头 4KB（避免 ASCII 标题干扰）
    for offset in [0, 4096, 16384, 65536, 262144]:
        if offset >= len(data):
            break
        sample = data[offset:offset + 8192]
        if not sample:
            continue
        for enc in ['utf-8', 'gbk', 'gb18030']:
            try:
                sample.decode(enc)
                return enc
            except UnicodeDecodeError:
                pass

    # fallback: 看整个文件 0xFFFD 数量
    for enc in ['gbk', 'gb18030', 'utf-8']:
        try:
            decoded = data[:65536].decode(enc, errors='replace')
            ff_count = decoded.count('�')
            if ff_count < 100:
                return enc
        except Exception:
            pass
    return 'utf-8'


def read_text_robust(path, enc):
    """读取文本，清理编码错误替换符

    策略：
    1. 用给定编码读（errors='replace' 防止崩溃）
    2. 清理 U+FFFD 替换字符（标记为"⚠编码错误⚠"）
    3. 报告被替换的字节数
    """
    with open(path, 'r', encoding=enc, errors='replace') as f:
        text = f.read()
    return text


def diagnose_novel(path, save_report=False):
    """主诊断函数"""
    safe_print(f'=== 文本质量诊断 ===')
    safe_print(f'文件: {path}')
    if not os.path.exists(path):
        safe_print('!! 文件不存在')
        return None

    size = os.path.getsize(path)
    enc = detect_encoding(path)
    text = read_text_robust(path, enc)
    # 报告编码错误
    err_count = text.count('�')

    total_chars = len(text)
    safe_print(f'  大小: {size:,} 字节')
    safe_print(f'  编码: {enc}')
    safe_print(f'  字符数: {total_chars:,}')
    safe_print(f'  ⚠ 编码错误替换符 (U+FFFD): {err_count} 个' if err_count else f'  ✓ 无编码错误')
    if err_count > 100:
        safe_print(f'  ⚠ 警告：编码错误较多（{err_count}），文件可能存在混合编码或部分损坏')
    safe_print(f'')

    report = []
    report.append(f'# 文本质量诊断报告\n\n文件: {path}\n')
    report.append(f'- 大小: {size:,} 字节\n- 编码: {enc}\n- 字符数: {total_chars:,}\n\n')

    # 1. BOM 检查
    safe_print('=== 1. 编码/BOM ===')
    bom_info = []
    with open(path, 'rb') as f:
        head = f.read(3)
    if head[:3] == b'\xef\xbb\xbf':
        bom_info.append('  含 UTF-8 BOM（建议去除以便通用处理）')
    if head[:2] in (b'\xff\xfe', b'\xfe\xff'):
        bom_info.append('  含 UTF-16 BOM')
    if not bom_info:
        bom_info.append('  无 BOM')
    for s in bom_info:
        safe_print(s)
    report.append('## 1. 编码\n' + '\n'.join(bom_info) + '\n\n')

    # 2. 章节结构
    safe_print('\n=== 2. 章节结构 ===')
    chap_pat = re.compile(r'^第([0-9' + CHINESE_NUMS + r']+)章[^\n]*', re.MULTILINE)
    vol_pat = re.compile(r'^第([0-9' + CHINESE_NUMS + r']+)卷[^\n]*', re.MULTILINE)
    other_pat = re.compile(r'^第([0-9' + CHINESE_NUMS + r']+)([节回集部])[^\n]*', re.MULTILINE)
    chapters = list(chap_pat.finditer(text))
    vols = list(vol_pat.finditer(text))
    others = list(other_pat.finditer(text))

    chap_data = []
    for m in chapters:
        n = parse_chinese_num(m.group(1))
        if n is not None:
            chap_data.append((n, m.start(), m.group().strip()[:50]))

    nums = sorted(set(c[0] for c in chap_data))
    missing = []
    if nums:
        for i in range(nums[0], nums[-1] + 1):
            if i not in nums:
                missing.append(i)

    chap_info = []
    chap_info.append(f'  章节数: {len(chapters)}')
    chap_info.append(f'  卷数: {len(vols)}')
    if nums:
        chap_info.append(f'  章节号范围: {nums[0]} ~ {nums[-1]}')
    if missing:
        chap_info.append(f'  ⚠ 缺失章节号 ({len(missing)} 个): {missing[:30]}{"..." if len(missing) > 30 else ""}')
    else:
        chap_info.append('  ✓ 章节号连续')
    if others:
        chap_info.append(f'  其它章节标记 (节/回/集/部): {len(others)} 处')
    for s in chap_info:
        safe_print(s)
    report.append('## 2. 章节结构\n' + '\n'.join(chap_info) + '\n\n')

    # 3. 章节标题重复
    safe_print('\n=== 3. 章节标题重复 ===')
    from collections import Counter
    titles = [c[2] for c in chap_data]
    dup_titles = [t for t, c in Counter(titles).items() if c > 1]
    dup_info = []
    if dup_titles:
        dup_info.append(f'  ⚠ 重复标题 ({len(dup_titles)} 个): {dup_titles[:5]}')
    else:
        dup_info.append('  ✓ 无重复章节标题')
    for s in dup_info:
        safe_print(s)
    report.append('## 3. 章节标题\n' + '\n'.join(dup_info) + '\n\n')

    # 4. 广告/推广
    safe_print('\n=== 4. 广告/推广检测 ===')
    # 更精准的匹配，避免误报
    ad_patterns = [
        (r'关注[^，。\n]{0,30}(公众号|微信公众号|书友群|企鹅群|qq群|扣扣群|交流群)', '关注+群号'),
        (r'(扫码关注|扫一扫关注|长按识别)', '扫码关注'),
        (r'加我(微信|扣扣|qq|weixin)', '联系方式'),
        (r'下载.{0,15}(app|番茄|七猫|书旗|笔趣阁|纵横|起点|笔趣|得间|追书神器)', 'APP/盗版网站推广'),
        (r'本章.{0,5}(发?布于?网?.{0,5}站?|(首发|独发|首发于|更新于|连载于))', '发布平台'),
        (r'(求.{0,8}订阅|求.{0,8}推荐票|求.{0,8}月票|求.{0,8}打赏|求.{0,8}收藏)', '求票'),
        (r'精彩.{0,5}继续.{0,5}请.{0,5}(看|搜|关注|加|收藏)', '求关注'),
        (r'记住.{0,5}(本站|网址|本群)', '记网址'),
        (r'(笔趣阁|书友群|百度云|微盘|52book|208book)\.', '盗版平台'),
    ]
    ad_found = []
    for pat, desc in ad_patterns:
        matches = re.findall(pat, text)
        if matches:
            ad_found.append((desc, len(matches), matches[:2]))
    ad_info = []
    if ad_found:
        for desc, cnt, samples in ad_found:
            line = f'  ⚠ {desc}: {cnt} 处'
            ad_info.append(line)
            for s in samples:
                ad_info.append(f'    例: {str(s)[:80]}')
    else:
        ad_info.append('  ✓ 未检测到广告/推广')
    for s in ad_info:
        safe_print(s)
    report.append('## 4. 广告/推广\n' + '\n'.join(ad_info) + '\n\n')

    # 5. 屏蔽词/敏感词
    safe_print('\n=== 5. 屏蔽词/敏感词检测 ===')
    masked_patterns = [
        (r'[█▓▒░]{3,}', '方块字符（疑似屏蔽）'),
        (r'\*{3,}', '连续星号'),
        (r'\?{4,}', '连续问号'),
        (r'X{4,}', 'X 屏蔽'),
        (r'□{3,}', '空白方块'),
        (r'（未完.{0,5}待续）', '"未完待续"占位'),
    ]
    mask_found = []
    for pat, desc in masked_patterns:
        matches = re.findall(pat, text)
        if matches:
            mask_found.append((desc, len(matches)))
    mask_info = []
    if mask_found:
        for desc, cnt in mask_found:
            mask_info.append(f'  ⚠ {desc}: {cnt} 处')
    else:
        mask_info.append('  ✓ 未检测到明显屏蔽词')
    for s in mask_info:
        safe_print(s)
    report.append('## 5. 屏蔽词\n' + '\n'.join(mask_info) + '\n\n')

    # 6. 谐音字/同音字
    safe_print('\n=== 6. 谐音字/同音字检测 ===')
    # 注意：每对替换都附"语境"提示。子 Agent 在生成摘要时需结合上下文判断。
    typo_pairs = [
        ('做爱', ['做哎', '做暧', '做埃', '造爱', '座爱']),
        ('妓女', ['技女']),
        ('强奸', ['强坚', '强煎', '强歼']),
        ('阴茎', ['阴径', '阴经']),
        ('阴道', ['阴导', '阴岛']),
        ('操', ['草']),  # "草" 也作感叹词——子 Agent 需判断语境
        ('肏', ['操']),
        ('鸡巴', ['鸡吧', '鸡八']),
        ('屌', ['吊']),
        ('牛逼', ['牛比', '牛B']),
        ('日（动词）', ['入', '曰']),  # "入" 多数情况是正常词——子 Agent 需看上下文
    ]
    typo_found = []
    for orig, alts in typo_pairs:
        for alt in alts:
            cnt = text.count(alt)
            if cnt > 0:
                typo_found.append((orig, alt, cnt))
    typo_info = []
    if typo_found:
        typo_info.append('  ⚠ 谐音字检测（需子 Agent 在生成摘要时识别语境）:')
        for orig, alt, cnt in sorted(typo_found, key=lambda x: -x[2])[:15]:
            typo_info.append(f'    "{alt}" → 疑似"{orig}": {cnt} 处')
    else:
        typo_info.append('  ✓ 未检测到常见谐音字')
    for s in typo_info:
        safe_print(s)
    report.append('## 6. 谐音字\n' + '\n'.join(typo_info) + '\n\n')

    # 7. 错别字/语法错误（地的得）
    safe_print('\n=== 7. 常见错别字（的地得） ===')
    typo_de = re.findall(r'([一-龥])的([一-龥])的([一-龥])的([一-龥])', text)
    if typo_de:
        safe_print(f'  ⚠ 发现 "的...的...的" 连续模式: {len(typo_de)} 处')
    else:
        safe_print('  ✓ 的地得混用无显著模式')
    report.append(f'## 7. 错别字\n- 连续"的...的...的"模式: {len(typo_de)} 处\n\n')

    # 8. 灌水
    safe_print('\n=== 8. 重复行/灌水检测 ===')
    lines = [l.strip() for l in text.split('\n') if l.strip()]
    line_counts = {}
    for l in lines:
        line_counts[l] = line_counts.get(l, 0) + 1
    dup_long = [(l, c) for l, c in line_counts.items() if c >= 5 and len(l) > 20]
    filler_info = []
    if dup_long:
        filler_info.append(f'  ⚠ 出现 5+ 次的较长行 ({len(dup_long)} 种):')
        for l, c in sorted(dup_long, key=lambda x: -x[1])[:3]:
            filler_info.append(f'    {c} 次: {l[:60]}')
    else:
        filler_info.append('  ✓ 无明显灌水')
    for s in filler_info:
        safe_print(s)
    report.append('## 8. 灌水\n' + '\n'.join(filler_info) + '\n\n')

    # 9. 文本结构
    safe_print('\n=== 9. 文本结构 ===')
    total_lines = len(text.split('\n'))
    empty_lines = sum(1 for l in text.split('\n') if not l.strip())
    safe_print(f'  总行数: {total_lines}')
    safe_print(f'  空行: {empty_lines} ({empty_lines/total_lines*100:.1f}%)')
    safe_print(f'  平均行长: {sum(len(l) for l in text.split(chr(10)))/total_lines:.1f} 字符')
    safe_print(f'  首 50 字: {text[:50]!r}')
    safe_print(f'  末 50 字: {text[-50:]!r}')

    # 10. 推荐切分粒度
    safe_print('\n=== 10. 推荐切分粒度 ===')
    if total_chars < 300_000:
        recommend = '不切分（1 个 part，主 Agent 直接读）'
    elif total_chars < 2_000_000:
        recommend = '15-20 万字/段（2-13 个 part）'
    elif total_chars < 10_000_000:
        recommend = '20 万字/段（10-50 个 part）'
    else:
        recommend = '30 万字/段（30+ 个 part）'
    safe_print(f'  推荐: {recommend}')

    safe_print('\n=== 诊断完成 ===')

    if save_report:
        report_path = save_report
        with open(report_path, 'w', encoding='utf-8') as f:
            f.write('\n'.join(report))
        safe_print(f'报告已保存: {report_path}')

    return {
        'path': path, 'encoding': enc, 'total_chars': total_chars,
        'chapters': len(chapters), 'vols': len(vols),
        'missing_chaps': missing, 'dup_titles': dup_titles,
        'typos': typo_found, 'ad_count': sum(c for _, c, _ in ad_found),
        'recommend': recommend,
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--path', help='小说文件路径（默认自动找）')
    parser.add_argument('--save', help='报告保存路径（如 diagnose_report.md）')
    args = parser.parse_args()

    if args.path:
        path = args.path
    else:
        candidates = glob.glob('*.txt')
        if len(candidates) == 1:
            path = candidates[0]
        elif len(candidates) > 1:
            safe_print('找到多个 txt，请用 --path 指定:')
            for c in candidates:
                safe_print(f'  {c}')
            return
        else:
            safe_print('未找到 txt')
            return

    diagnose_novel(path, save_report=args.save)


if __name__ == '__main__':
    main()
