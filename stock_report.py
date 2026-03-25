#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import sys
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
            # Keep as bytes, decode manually
            return cls._parse(resp.content.decode('gbk'))
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

def safe_str(s):
    """Convert to safe ASCII for WeChat"""
    if not s:
        return ""
    # Replace Chinese with English abbreviations
    replacements = {
        "上证指数": "SHANGZHENG",
        "深证成指": "SHENZHENG",
        "创业板指": "CHUANGYE",
        "科创50": "KECHUANG50",
        "沪深300": "HUASHEN300",
        "激进买入": "JIJIN MAIRU",
        "保守买入": "BAOSHOU MAIRU",
        "持币观望": "CHIBI GUANWANG",
        "仅供参考": "ZAN GONG CANKAO",
        "不构成投资建议": "BU GOUCHENG TOUZI JIANYI",
    }
    for cn, en in replacements.items():
        s = s.replace(cn, en)
    return s

def generate_report():
    indices = SinaAPI.get_quotes(["sh000001", "sz399001", "sz399006", "sh000688", "sh000300"])
    tech = SinaAPI.get_quotes(["sh688981", "sh688256", "sh688072", "sz002230", "hk01810"])
    
    avg_pct = sum(i.get("pct", 0) for i in indices) / len(indices) if indices else 0
    
    if avg_pct > 1:
        attitude, position = "JIJIN MAIRU", "70-80%"
    elif avg_pct > 0.5:
        attitude, position = "BAOSHOU MAIRU", "55-65%"
    else:
        attitude, position = "CHIBI GUANWANG", "30-40%"
    
    lines = []
    lines.append("=" * 40)
    lines.append("MEIRI DONGLIANG BAOGAO " + datetime.now().strftime("%Y-%m-%d"))
    lines.append("=" * 40)
    lines.append("")
    lines.append("[TAIDU] " + attitude + " | [CANGWEI] " + position)
    lines.append("")
    lines.append("[A GUSHO ZHISHI]")
    for idx in indices:
        pct = idx.get("pct", 0)
        arrow = "[+]" if pct >= 0 else "[-]"
        lines.append(arrow + " " + safe_str(idx['name']) + ": " + str(round(idx['price'], 2)) + " (" + ("+" if pct >= 0 else "") + str(pct) + "%)")
    
    lines.append("")
    lines.append("[HEXIN BIAODE]")
    sorted_tech = sorted(tech, key=lambda x: x.get("pct", 0), reverse=True)[:3]
    for i, t in enumerate(sorted_tech, 1):
        pct = t.get("pct", 0)
        name = safe_str(t['name'])
        lines.append("[" + str(i) + "] " + name + " " + t['code'])
        lines.append("    ZHANGFU: " + ("+" if pct >= 0 else "") + str(pct) + "% | RUCHANG: " + str(round(t['price'], 2)))
    
    lines.append("")
    lines.append("[FENGKONG]")
    lines.append("CANGWEI: " + position + " | DANZHI: 15%")
    lines.append("ZHUISUN: -5~6%")
    lines.append("")
    lines.append("ZAN GONG CANKAO, BU GOUCHENG TOUZI JIANYI")
    
    return "\n".join(lines)

if __name__ == "__main__":
    print(generate_report())
