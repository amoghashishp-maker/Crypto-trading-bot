import time
import ccxt
import numpy as np
import pandas as pd

exchange = ccxt.coinbase({
    'enableRateLimit': True,
    'timeout': 30000,
})

SYMBOL = 'BTC/USDT'
TIMEFRAME = '1h'
SHORT_WINDOW = 5
LONG_WINDOW = 20

def fetch_market_data(symbol, timeframe, limit=100):
    try:
        ohlv = exchange.fetch_ohlcv(symbol, timeframe, limit=limit)
        df = pd.DataFrame(ohlv, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
        df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
        df['close'] = df['close'].astype(float)
        return df
    except Exception as e:
        print(f"Data  Error: {e}")
        return pd.DataFrame()

def calculate_signals(df):
    if df.empty or len(df) < LONG_WINDOW:
        return df
    df['Short_MA'] = df['close'].rolling(window=SHORT_WINDOW).mean()
    df['Long_MA'] = df['close'].rolling(window=LONG_WINDOW).mean()
    df['Signal'] = 0.0
    df.loc[df['Short_MA'] > df['Long_MA'], 'Signal'] = 1.0
    df['Position'] = df['Signal'].diff()
    return df

def run_trading_bot():
    print(f"Engine Initialized")
    while True:
        try:
            df = fetch_market_data(SYMBOL, TIMEFRAME)
            if df.empty:
                time.sleep(60)
                continue
            df = calculate_signals(df)
            latest_row = df.iloc[-1]
            previous_row = df.iloc[-2]
            
            print(f"Price: ${latest_row['close']:,.2f} | Short MA: {latest_row['Short_MA']:.2f} | Long MA: {latest_row['Long_MA']:.2f}")
            
            if previous_row['Short_MA'] <= previous_row['Long_MA'] and latest_row['Short_MA'] > latest_row['Long_MA']:
                print(f" [EXECUTION ALERT] BUY SIGNAL TRIGGERED AT ${latest_row['close']:,.2f}")
            elif previous_row['Short_MA'] >= previous_row['Long_MA'] and latest_row['Short_MA'] < latest_row['Long_MA']:
                print(f" [EXECUTION ALERT] SELL SIGNAL TRIGGERED AT ${latest_row['close']:,.2f}")
            else:
                print(" Target metrics stable. Monitoring...")
            print("-" * 60)
            time.sleep(3600)
        except KeyboardInterrupt:
            print("\n Shutting down systems securely.")
            break
        except Exception as e:
            print(f" Exception Encountered: {e}")
            time.sleep(60)

if __name__ == "__main__":
    run_trading_bot()
