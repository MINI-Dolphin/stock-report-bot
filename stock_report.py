#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
股票日报 - 盘前动量报告
GitHub Actions 云端推送版本
"""
import sys
import os
import requests
from datetime import datetime

class SinaAPI:
    BASE_URL = "http://hq.sinajs.cn/list="
    HEADERS = {"Referer": "http://finance.sina.com.cn"}
    
    @classmethod
    def get_quotes(cls, codes):
        try:
            url = cls.BASE_URL + ",".join(codes)
            resp = requests.get(url, headers=cls.HEADERS, timeout=10)
            text = resp.content.decode('gbk', errors='replace')
            return cls._parse(text)
        except:
            return []
    
    @classmethod
    def _parse(cls, text):
        results = []
        for line in text.strip().split("\n"):
            if not line or "=" not in line:
                continue
            try:
                left = line.split("=")[0].split("_")[-1]
                data_str = line.split('="')[1].strip().strip('"')
                if not data_str:
                    continue
                data = data_str.split(",")
                if len(data) < 10:
                    continue
                price = float(data[3]) if data[3] else 0
                close = float(data[2]) if data[2] else 0
                pct = round((price - close) / close * 100, 2) if close > 0 else 0
                results.append({"code": left, "name": data[0], "price": price, "pct": pct})
            except:
                continue
        return results

def generate_report():
    indices = SinaAPI.get_quotes(["sh000001", "sz399001", "sz399006", "sh000688", "sh000300"])
    tech = SinaAPI.get_quotes(["sh688981", "sh688256", "sh688072", "sz002230", "hk01810"])
    
    avg_pct = sum(i.get("pct", 0) for i in indices) / len(indices) if indices else 0
    
    if avg_pct > 1:
        attitude, position = "激进买入", "70-80%"
    elif avg_pct > 0.5:
        attitude, position = "保守买入", "55-65%"
    elif avg_pct > -0.5:
        attitude, position = "持币观望", "30-40%"
    else:
        attitude, position = "空仓避险", "0-20%"
    
    lines = []
    lines.append("=" * 40)
    lines.append("【每日动量报告】")
    lines.append(datetime.now().strftime("%Y-%m-%d"))
    lines.append("=" * 40)
    lines.append("")
    lines.append(f"🎯 态度：{attitude} | 仓位：{position}")
    lines.append("")
    
    lines.append("📊 A股指数")
    for idx in indices:
        pct = idx.get("pct", 0)
        arrow = "▲" if pct >= 0 else "▼"
        lines.append(f"  {arrow} {idx['name']} {idx['price']:.2f} ({pct:+.2f}%)")
    lines.append("")
    
    lines.append("🔥 核心标的")
    sorted_tech = sorted(tech, key=lambda x: x.get("pct", 0), reverse=True)
    for i, t in enumerate(sorted_tech, 1):
        pct = t.get("pct", 0)
        lines.append(f"  #{i} {t['name']} {t['code']}")
        lines.append(f"     涨幅: {pct:+.2f}% | 报价: {t['price']:.2f}")
    lines.append("")
    
    lines.append("⚠️ 风控")
    lines.append(f"  仓位 ≤ {position} | 单只 ≤ 15%")
    lines.append("  止损: -5~6%")
    lines.append("  盈亏比: 1:2 以上")
    lines.append("")
    lines.append("仅供参考，不构成投资建议。")
    
    return "\n".join(lines)

def send_to_wecom(webhook_url, content):
    payload = {"msgtype": "text", "text": {"content": content}}
    resp = requests.post(webhook_url, json=payload, headers={"Content-Type": "application/json"}, timeout=10)
    result = resp.json()
    print(f"[WeChat] errcode={result.get('errcode')} errmsg={result.get('errmsg')}")
    return result.get('errcode') == 0

if __name__ == "__main__":
    report = generate_report()
    print(report)
    
    webhook = os.environ.get("WECOM_WEBHOOK", "")
    if webhook:
        ok = send_to_wecom(webhook, report)
        sys.exit(0 if ok else 1)
    else:
        print("[INFO] WECOM_WEBHOOK not set, skipping send")
