import requests
import pandas as pd
import datetime
import os
import time

API_KEY = os.getenv('BASESCAN_API_KEY')
TOKEN_ADDRESS = "0x22af33fe49fd1fa80c7149773dde5890d3c76f3b"
BASE_URL = "https://api.etherscan.io/v2/api"
CSV_FILE = "bnkr_holders_history.csv"

def get_balance(address):
    params = {
        "chainid": "8453",
        "module": "account",
        "action": "tokenbalance",
        "contractaddress": TOKEN_ADDRESS,
        "address": address,
        "tag": "latest",
        "apikey": API_KEY
    }
    try:
        res = requests.get(BASE_URL, params=params, timeout=10).json()
        return float(res['result']) / 10**18 if res['status'] == '1' else 0
    except Exception as e:
        print(f"查询地址 {address} 失败: {e}")
        return 0

def main():
    if not os.path.exists(CSV_FILE):
        print("错误：找不到原始 CSV 文件，请先手动上传。")
        return

    # 1. 读取历史数据并清理格式
    try:
        df_history = pd.read_csv(CSV_FILE)
        # 统一清理列名中的空格
        df_history.columns = df_history.columns.str.strip()
    except Exception as e:
        print(f"读取 CSV 失败: {e}")
        return

    # 2. 识别地址列名
    addr_col = next((c for c in df_history.columns if 'Address' in c or 'Holder' in c), 'HolderAddress')
    
    # 3. 提取需要监控的地址（去重后的前 200 个）
    unique_addresses = df_history[addr_col].dropna().unique().tolist()[:200]
    
    bj_time = (datetime.datetime.utcnow() + datetime.timedelta(hours=8)).strftime('%Y-%m-%d %H:%M')
    print(f"开始更新 {len(unique_addresses)} 个大户的数据...")

    new_records = []
    for addr in unique_addresses:
        if not str(addr).startswith('0x'): continue
        
        curr_bal = get_balance(addr)
        
        # 获取该地址上一条记录的余额
        addr_hist = df_history[df_history[addr_col] == addr]
        last_bal = addr_hist['Balance'].iloc[-1] if not addr_hist.empty and 'Balance' in addr_hist.columns else curr_bal
        
        # 计算变动
        change = curr_bal - last_bal
        
        new_records.append({
            addr_col: addr,
            'Balance': curr_bal,
            'Change': change,
            'Date': bj_time
        })
        time.sleep(0.21) # 免费 API 频率限制

    # 4. 合并并保存
    df_new = pd.DataFrame(new_records)
    df_final = pd.concat([df_history, df_new], ignore_index=True)
    
    # 只保留最近 30 天/次的数据，防止 CSV 文件无限增大导致 Action 崩溃
    if len(df_final) > 10000:
        df_final = df_final.tail(10000)

    df_final.to_csv(CSV_FILE, index=False, encoding='utf-8-sig')
    print(f"✅ 数据更新成功，当前记录数: {len(df_final)}")

if __name__ == "__main__":
    main()
