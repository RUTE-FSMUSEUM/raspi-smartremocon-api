import json
import os
import argparse
from datetime import datetime
import time
import random

class dht20():
    def __init__(self, PATH_CURRENT, PATH_LOG, TEST=False) -> None:
        self.PATH_CURRENT = PATH_CURRENT
        self.PATH_LOG = PATH_LOG
        self.TEST = TEST

    # 単発イベントでセンサデータを取得する関数
    def getSensorData(self) -> None:
        data = self.fetchDht20SensorData()
        self.exportJson(data, isLogging=False)

    # 定期的にセンサデータを記録する関数
    def loggingSensorData(self):
        pass

    # Jsonにエクスポート
    def exportJson(self, data, isLogging=False):
        # ロギングとしてセンサデータを記録
        if isLogging:
            pass

        # 単発イベントとしてセンサデータを記録
        else:
            with open(self.PATH_CURRENT, 'w', encoding='utf-8') as json_file:
                json.dump(data, json_file, ensure_ascii=False, indent=4)

    # DHT20センサデータの取得
    def fetchDht20SensorData(self) -> dict:
        now = datetime.now()
        if not self.TEST:
            import smbus

            i2c = smbus.SMBus(1)

            time.sleep(0.1)
            ret = i2c.read_byte_data(0x38, 0x71)
            if ret != 0x18:
                return {"temprature": -40, "humidity": 0, "timestamp": now.strftime("%Y-%m-%d %H:%M:%S")}
            
            time.sleep(0.1)
            i2c.write_i2c_block_data(0x38, 0xAC, [0x33, 0x00])

            time.sleep(0.08)
            data = i2c.read_i2c_block_data(0x38, 0x00, 7)

            humi = data[1] << 12 | data[2] << 4 | ((data[3] & 0xF0) >> 4)
            tmep = ((data[3] & 0x0F) << 16) | data[4] << 8 | data[5]

            humi = humi / 2**20 * 100
            tmep = tmep / 2**20 * 200 - 50

            return {"temprature": tmep, "humidity": humi, "timestamp": now.strftime("%Y-%m-%d %H:%M:%S")}
        else:
            return {"temprature": random.uniform(25.9, 26.9), "humidity": random.uniform(76.0, 88.0), "timestamp": now.strftime("%Y-%m-%d %H:%M:%S")}
    

p = argparse.ArgumentParser()

p.add_argument("--logging", help="ロギングとして記録(falseの場合は単発イベントとして記録)", action="store_true")
p.add_argument("-pc", "--path_current", help="現在のセンシングデータを記録するjsonファイルのパス", required=True)
p.add_argument("-pl", "--path_log", help="センシングデータをロギングするjsonファイルのパス", required=True)
p.add_argument("--test", help="テストモード(ラズパイ以外をサーバとしてブラウザ画面のテストのみを実施したい場合)", action="store_true")

args = p.parse_args()
DHT20 = dht20(PATH_CURRENT=args.path_current, PATH_LOG=args.path_log, TEST=args.test)

# ロギングとしてセンサデータを記録
if args.logging:
    pass
# 単発イベントとしてセンサデータを記録
else:
    DHT20.getSensorData()