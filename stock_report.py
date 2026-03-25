#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
GitHub Actions 用的股票报告脚本
"""
import sys
import json
import os
import requests

class SinaAPI:
    BASE_URL = "http://hq.sinajs.cn/list="
    HEADERS = {"Referer": "http://finance.sina.com.cn"}
    
    @classmethod
    def get_quotes(cls, codes):
        try:
            url = cls.BASE_URL + ",".join(codes)
            resp = requests.get(url, headers=cls.HEADERS, timeout=10)
            resp.encoding = "gbk"
            return cls._parse(resp.text)
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

def generate_morning_report():
    """生成盘前报告"""
    indices = SinaAPI.get_quotes(["sh000001", "sz399001", "sz399006", "sh000688", "sh000300"])
    tech = SinaAPI.get_quotes(["sh688981", "sh688256", "sh688072", "sz002230", "hk01810"])
    hk = SinaAPI.get_quotes(["hk01810", "hk00700", "hk09988", "hk03690"])
    
    avg_pct = sum(i.get("pct", 0) for i in indices) / len(indices) if indices else 0
    
    if avg_pct > 1:
        attitude, position = "激进买入", "70-80%"
    elif avg_pct > 0.5:
        attitude, position = "保守买入", "55-65%"
    else:
        attitude, position = "持币观望", "30-40%"
    
    report = f"【每日动量报告】\n\n🎯 态度：{attitude} | 仓位：{position}\n\n📊 A股指数\n"
    for idx in indices:
        pct = idx.get("pct", 0)
        arrow = "[+]" if pct >= 0 else "[-]"
        report += f"{arrow} {idx['name']}: {idx['price']:.2f} ({pct:+.2f}%)\n"
    
    report += "\n🔥 核心标的\n"
    sorted_tech = sorted(tech, key=lambda x: x.get("pct", 0), reverse=True)[:3]
    for i, t in enumerate(sorted_tech, 1):
        pct = t.get("pct", 0)
        report += f"【{i}】{t['name']} {t['code']} {pct:+.2f}%\n"
    
    report += "\n⚠️ 风控\n"
    report += f"仓位≤{position.replace('%','')} | 单只≤15%\n"
    report += "仅供参考，不构成投资建议。"
    
    return report

def send_to_wecom(webhook_url, content):
    """发送到企业微信"""
    if not webhook_url:
        print("未配置Webhook，跳过发送")
        return
    
    data = {"msgtype": "text", "text": {"content": content}}
    resp = requests.post(webhook_url, json=data, timeout=10)
    print(f"发送结果: {resp.text}")

if __name__ == "__main__":
    webhook = os.environ.get("WECOM_WEBHOOK", "")
    report = generate_morning_report()
    print(report)
    send_to_wecom(webhook, report)
