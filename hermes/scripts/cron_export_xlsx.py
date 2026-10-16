#!/usr/bin/env python3
# 导出 cron 清单到 xlsx，供华哥编辑后回传执行
import json

SRC = '/Users/hua/.hermes/cron/jobs.json'
OUT = '/Users/hua/cron清单_20261012.xlsx'

with open(SRC) as f:
    jobs = json.load(f)['jobs']

def sched(j):
    s = j.get('schedule_display') or ''
    if j.get('no_agent'):
        s += ' [脚本]'
    return s

def typ(j):
    return '脚本' if j.get('no_agent') else 'LLM'

def cls(j):
    n = j.get('name') or ''
    if any(k in n for k in ['守护', '监控', 'watchdog', 'Fallback', 'Token 异常', '生活流', '记忆压缩']):
        return '守护/监控'
    if any(k in n for k in ['心跳', '健康检查', '同步', '版本检查', '归档', '迁移', '压缩']):
        return '心跳/同步/健康'
    if any(k in n for k in ['日报', '汇报', '汇总', '摘要', '巡视']):
        return '汇报/日报'
    if any(k in n for k in ['调研', '采集', '学习', '轮换']):
        return '调研/采集'
    if '进化' in n:
        return '自进化'
    return '其他'

rows_en, rows_pa = [], []
for j in jobs:
    r = {
        'id': j.get('id', ''),
        'name': j.get('name') or '',
        'enabled': '启用' if j.get('enabled') else '暂停',
        'sched': sched(j),
        'typ': typ(j),
        'cls': cls(j),
        'model': (j.get('model') or '默认') if not j.get('no_agent') else '—',
        'last': (j.get('last_status') or '从未'),
    }
    (rows_en if j.get('enabled') else rows_pa).append(r)

rows_en.sort(key=lambda x: x['cls'])
rows_pa.sort(key=lambda x: x['cls'])

try:
    from openpyxl import Workbook
    from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
except ImportError:
    raise SystemExit('openpyxl not available')

wb = Workbook()
ws = wb.active
ws.title = 'cron清单'

headers = ['编号', '名称', '状态', '频率', '执行方式', '类别', '模型', '上次运行', '处理指令(填写)', '备注(填写)']
widths = [14, 40, 8, 16, 10, 12, 14, 10, 18, 24]

thin = Border(*[Side(style='thin', color='CCCCCC')] * 4)
hfill = PatternFill('solid', start_color='1F4E78')
hfont = Font(name='Arial', bold=True, color='FFFFFF', size=10)
bfont = Font(name='Arial', size=10)
en_fill = PatternFill('solid', start_color='E8F5E9')
pa_fill = PatternFill('solid', start_color='FFF3E0')
err_font = Font(name='Arial', size=10, color='CC0000', bold=True)

for c, (h, w) in enumerate(zip(headers, widths), 1):
    cell = ws.cell(row=1, column=c, value=h)
    cell.font = hfont
    cell.fill = hfill
    cell.alignment = Alignment(horizontal='center', vertical='center')
    ws.column_dimensions[cell.column_letter].width = w
ws.freeze_panes = 'A2'

r = 2
for grp in (rows_en, rows_pa):
    for d in grp:
        vals = [d['id'], d['name'], d['enabled'], d['sched'], d['typ'], d['cls'], d['model'], d['last'], '', '']
        for c, v in enumerate(vals, 1):
            cell = ws.cell(row=r, column=c, value=v)
            cell.font = bfont
            cell.border = thin
            cell.alignment = Alignment(vertical='center', wrap_text=(c == 2))
            cell.fill = en_fill if d['enabled'] == '启用' else pa_fill
            if c == 8 and d['last'] == 'error':
                cell.font = err_font
        r += 1

# 说明 sheet
ws2 = wb.create_sheet('说明')
notes = [
    ['cron 瘦身确认清单 — 2026-10-12', ''],
    ['', ''],
    ['总 数', len(jobs)],
    ['启 用', len(rows_en)],
    ['暂 停', len(rows_pa)],
    ['', ''],
    ['使用方法', '在「处理指令(填写)」列填入指令，整行发回给玉芬执行'],
    ['可用指令', '删除 / 暂停 / 恢复 / 降频(填目标频率) / 提频(填目标频率)'],
    ['留空', '= 保持现状不动'],
    ['', ''],
    ['底色说明', '绿色=启用中，橙色=暂停中，红色=上次运行报错'],
    ['[脚本]', '= 零token脚本任务，不过LLM'],
    ['', ''],
    ['备份', '~/.hermes/cron/jobs.json.bak-20261012-cron-slim'],
]
for i, (a, b) in enumerate(notes, 1):
    ws2.cell(row=i, column=1, value=a).font = Font(name='Arial', bold=(i == 1), size=11 if i == 1 else 10)
    ws2.cell(row=i, column=2, value=b).font = bfont
ws2.column_dimensions['A'].width = 16
ws2.column_dimensions['B'].width = 60

wb.save(OUT)
print(f'OK {OUT} | rows={r-2} (en={len(rows_en)}, pa={len(rows_pa)})')
