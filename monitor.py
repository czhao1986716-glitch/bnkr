import requests
import pandas as pd
import datetime
import os
import time

# 配置信息
API_KEY = os.getenv('BASESCAN_API_KEY')
TOKEN_ADDRESS = "0x22af33fe49fd1fa80c7149773dde5890d3c76f3b"
# 关键修改：必须使用 Etherscan V2 统一入口
BASE_URL = "https://api.etherscan.io/v2/api"
CSV_FILE = "bnkr_holders_history.csv"

def get_balance(address):
    """使用免费版支持的 V2 接口获取单个地址余额"""
    params = {
        "chainid": "8453",      # Base 链主网 ID
        "module": "account",
        "action": "tokenbalance",
        "contractaddress": TOKEN_ADDRESS,
        "address": address,
        "tag": "latest",
        "apikey": API_KEY
    }
    try:
        response = requests.get(BASE_URL, params=params, timeout=20)
        data = response.json()
        if data['status'] == '1':
            return float(data['result']) / 10**18
        return 0
    except:
        return 0

def main():
    # 检查是否有初始数据
    if not os.path.exists(CSV_FILE):
        print("未找到初始 CSV 文件，请确保已手动上传。")
        return

    # 读取大户名单
    df_history = pd.read_csv(CSV_FILE)
    # 自动识别地址列名
    addr_col = 'TokenHolderAddress' if 'TokenHolderAddress' in df_history.columns else 'Address'
    addresses = df_history[addr_col].unique().tolist()[:200]

    bj_time = (datetime.datetime.utcnow() + datetime.timedelta(hours=8)).strftime('%Y-%m-%d %H:%M')
    print(f"开始更新 {len(addresses)} 个大户余额...")

    new_data = []
    for addr in addresses:
        balance = get_balance(addr)
        new_data.append({addr_col: addr, "Balance": balance, "Date": bj_time})
        # 免费版 API 频率限制
        time.sleep(0.25)

    # 保存今日快照
    df_new = pd.DataFrame(new_data)
    # 合并到总表
    df_final = pd.concat([df_history, df_new], ignore_index=True)
    df_final.to_csv(CSV_FILE, index=False, encoding='utf-8-sig')
    print(f"✅ 更新成功：{bj_time}")

if __name__ == "__main__":
    main()
