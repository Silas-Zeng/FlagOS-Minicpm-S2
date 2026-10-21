#!/usr/bin/env python3
"""Render the repository's reviewed Markdown report; no experiment execution."""
from __future__ import annotations

import argparse
import html
from pathlib import Path
import re

from reportlab.lib import colors
from reportlab.lib.enums import TA_LEFT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import (
    LongTable, Paragraph, SimpleDocTemplate, Spacer, TableStyle,
)


ROOT = Path(__file__).resolve().parents[1]
NAVY = colors.HexColor('#19354B')
TEAL = colors.HexColor('#087E8B')
INK = colors.HexColor('#263746')
PALE = colors.HexColor('#EDF4F7')
WIDTH = A4[0] - 92


def build(source: Path, target: Path, font: Path, bold_font: Path) -> None:
    pdfmetrics.registerFont(TTFont('ReportCJK', str(font), subfontIndex=0))
    pdfmetrics.registerFont(TTFont('ReportCJKBold', str(bold_font), subfontIndex=0))
    pdfmetrics.registerFontFamily('ReportCJK', normal='ReportCJK', bold='ReportCJKBold')
    body = ParagraphStyle('Body', fontName='ReportCJK', fontSize=9.4,
                          leading=15, textColor=INK, wordWrap='CJK',
                          spaceAfter=8, alignment=TA_LEFT, splitLongWords=True)
    title = ParagraphStyle('Title', parent=body, fontName='ReportCJKBold',
                           fontSize=19, leading=28, textColor=NAVY, spaceAfter=16)
    heading = ParagraphStyle('Heading', parent=body, fontName='ReportCJKBold',
                             fontSize=12.2, leading=19, textColor=TEAL,
                             spaceBefore=14, spaceAfter=7, keepWithNext=True)
    cell = ParagraphStyle('Cell', parent=body, fontSize=8, leading=12,
                          spaceAfter=0)
    cell_head = ParagraphStyle('CellHead', parent=cell, fontName='ReportCJKBold',
                               textColor=colors.white)
    reference = ParagraphStyle('Reference', parent=body, fontSize=7.5,
                               leading=11, spaceAfter=6)
    links: list[tuple[str, str]] = []

    def inline(text: str) -> str:
        text = text.replace('\u2011', '-').replace('\u2013', '-').replace('\u2014', '-')

        def link(match: re.Match) -> str:
            label, path = match.group(1), match.group(2).strip('<>')
            pair = (label, path)
            if pair not in links:
                links.append(pair)
            return f'{label} [{links.index(pair) + 1}]'

        text = re.sub(r'\[([^\]]+)\]\(([^)]+)\)', link, text)
        text = html.escape(text)
        text = re.sub(r'\*\*(.+?)\*\*', r'<b>\1</b>', text)
        text = re.sub(r'`([^`]+)`', r'\1', text)
        return text

    flow = []
    lines = source.read_text(encoding='utf-8-sig').splitlines()
    i = 0
    while i < len(lines):
        line = lines[i].strip()
        if not line:
            i += 1
            continue
        if line.startswith('# '):
            flow.append(Paragraph(inline(line[2:]), title))
            i += 1
        elif line.startswith('## '):
            flow.append(Paragraph(inline(line[3:]), heading))
            i += 1
        elif line.startswith('|'):
            rows = []
            while i < len(lines) and lines[i].strip().startswith('|'):
                fields = [v.strip() for v in lines[i].strip().strip('|').split('|')]
                if not all(re.fullmatch(r':?-+:?', f) for f in fields):
                    rows.append(fields)
                i += 1
            count = len(rows[0])
            if any(len(row) != count for row in rows):
                raise ValueError('inconsistent Markdown table columns')
            ratios = {3: ([0.2, 0.57, 0.23] if rows[0][0] == '方向' else [0.2, 0.3, 0.5]),
                      6: [0.18, 0.12, 0.15, 0.15, 0.18, 0.22],
                      7: [0.18, 0.11, 0.14, 0.14, 0.15, 0.14, 0.14]}
            widths = [WIDTH * value for value in ratios.get(count, [1 / count] * count)]
            content = [[Paragraph(inline(v), cell_head if n == 0 else cell)
                        for v in row] for n, row in enumerate(rows)]
            table = LongTable(content, colWidths=widths, repeatRows=1,
                              hAlign='LEFT', splitByRow=1)
            table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), NAVY),
                ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, PALE]),
                ('VALIGN', (0, 0), (-1, -1), 'TOP'),
                ('LEFTPADDING', (0, 0), (-1, -1), 6),
                ('RIGHTPADDING', (0, 0), (-1, -1), 6),
                ('TOPPADDING', (0, 0), (-1, -1), 7),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 7),
                ('LINEBELOW', (0, 0), (-1, 0), 0.6, TEAL),
                ('LINEBELOW', (0, -1), (-1, -1), 0.4, colors.HexColor('#C8D7DF')),
            ]))
            flow.extend([table, Spacer(1, 10)])
        else:
            paragraph = [line]
            i += 1
            while i < len(lines) and lines[i].strip() and not lines[i].lstrip().startswith(('#', '|')):
                paragraph.append(lines[i].strip())
                i += 1
            flow.append(Paragraph(inline(' '.join(paragraph)), body))

    flow.append(Paragraph('证据索引（项目内相对路径）', heading))
    for number, (label, path) in enumerate(links, 1):
        if not path.startswith(('http://', 'https://')):
            resolved = (source.parent / path.split('#')[0]).resolve()
            if not resolved.exists():
                raise FileNotFoundError(f'missing report reference: {resolved}')
            path = resolved.relative_to(ROOT).as_posix()
        flow.append(Paragraph(html.escape(f'[{number}] {label} - {path}'), reference))

    def footer(canvas, doc):
        canvas.saveState()
        canvas.setStrokeColor(colors.HexColor('#C8D7DF'))
        canvas.line(46, 39, A4[0] - 46, 39)
        canvas.setFillColor(INK)
        canvas.setFont('ReportCJK', 7.2)
        canvas.drawString(46, 26, 'FlagOS S2 | MiniCPM5-2B | BI-V150 | 2026-10-22')
        canvas.drawRightString(A4[0] - 46, 26, f'{doc.page}')
        canvas.restoreState()

    target.parent.mkdir(parents=True, exist_ok=True)
    doc = SimpleDocTemplate(str(target), pagesize=A4, rightMargin=46,
                            leftMargin=46, topMargin=43, bottomMargin=52,
                            title='MiniCPM5-2B / BI-V150 技术报告',
                            author='MiniCPM throughput experiment', pageCompression=1)
    doc.build(flow, onFirstPage=footer, onLaterPages=footer)
    print(target.resolve())


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--source', type=Path, default=ROOT / 'docs/technical-report.md')
    parser.add_argument('--output', type=Path, default=ROOT / 'output/pdf/report.pdf')
    parser.add_argument('--font', type=Path, default=Path('C:/Windows/Fonts/msyh.ttc'))
    parser.add_argument('--bold-font', type=Path, default=Path('C:/Windows/Fonts/msyhbd.ttc'))
    args = parser.parse_args()
    build(args.source, args.output, args.font, args.bold_font)
