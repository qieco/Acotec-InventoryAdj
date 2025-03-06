# -*- coding: utf-8 -*-
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import re
from decimal import Decimal, InvalidOperation
import json
import requests
from ns_upload import NetSuiteAPI


class DataProcessor:
    def __init__(self, data):
        # 假设传入的数据已经是一个字典
        self.data = data

    def adjust_data_types(self):
        """
        Adjust the types of the fields in the data structure.
        """
        # Ensure the main keys are integers where applicable
        for key in ['customform', 'subsidiary', 'account', 'department', 'calss']:
            if key in self.data['inventoryadjustment']:
                self.data['inventoryadjustment'][key] = int(self.data['inventoryadjustment'][key])

        # Handle the 'inventory' list
        if 'inventory' in self.data['inventoryadjustment']:
            for item in self.data['inventoryadjustment']['inventory']:
                item['item'] = int(item['item'])
                item['location'] = int(item['location'])  # Note: 'location' seems to be misspelled as 'localtion'
                if 'inventorydetail' in item:
                    for assignment in item['inventorydetail']['inventoryassignment']:
                        assignment['binnumber'] = int(assignment['binnumber'])

    def to_json(self):
        """
        Convert the processed data back to JSON string.
        """
        self.adjust_data_types()
        return self.data

try:
    from rc_utils import RcUtils
    isPROD = True
    rc_data = RcUtils.getData()
except Exception:
    print("测试环境")
    isPROD = False
def rc_todata(data):
    if isPROD:
        RcUtils.toData(data)
    else:
        print(data)
    #return data
try:
    if not isPROD:
        rc_data = [{"data":[{"inventoryadjustment":{"requestid":497836,"custbody5":"OO-000009","customform":117,"subsidiary":10,"account":"2615","memo":"13:55","department":"537","calss":"783","inventory":[{"item":"104969","location":"8","adjustqtyby":"-1.00","inventorydetail":{"inventoryassignment":[{"receiptinventorynumber":"A240401201","binnumber":"10713","quantity":"-1.00"}]}}]}}],"appkey":"670e16477c064f6e3c297049","P_ENDFLAG":"1"}]
    input_data = json.dumps(rc_data, indent=4)
    input_data = json.loads(input_data)

    entry = input_data[0]['data'][0]
    request_id = entry['inventoryadjustment'].get('requestid', None)
    #print(type(entry))
    processor = DataProcessor(entry)
    entry = processor.to_json()
    url = "https://7557353-sb1.restlets.api.netsuite.com/app/site/hosting/restlet.nl?script=1171&deploy=1"
    consumer_key = "84f0f9ad687eebcc17683f108acdbc424af1500df4ca26263abdf9d408f2b74d"
    consumer_secret = "6aa2602ed178dc27a15531a161d42c0a8fb121b2917923c2651d064ec8aa585f"
    token_key = "a20a5e6433cf124ba67975d66b82496a93023c066e5649a1bd530f5b6371d6b2"
    token_secret = "f232ab1cd049257c03d8525733cbedd67e9bf29728b8ce77db361d122bf3e08e"
    netsuite_api = NetSuiteAPI(consumer_key,consumer_secret,token_key,token_secret)
    response = netsuite_api.post(url, entry)
    #print(response)
    response.raise_for_status()
    response_data = json.loads(response.text)
    try:
        # 从字典中获取'success'值
        is_create_success = response_data['success']

        if is_create_success:
            ir_number = response_data['DocumentNumber']
                # 创建字典结构
            data_dict = {
                "success": True,
                "创建了采购订单": ir_number,
                "requesitId": request_id,
                "nskcdzdh": ir_number
            }
            data_list = [data_dict]

            # 将字典转换为 JSON 字符串
            data_json = json.dumps(data_dict, ensure_ascii=False)
            rc_todata(data_list)
            print(json.dumps({"success": "true", "requesitId": f"'{request_id}'", "nskcdzdh": f"'{ir_number}'"}))
        else:
            error_message = response_data['error']
            data_dict = {
                "success": False,
                "创建了采购订单": f'NS返回错误:{error_message}',
                "requesitId": request_id,
                "nskcdzdh": error_message
            }
            data_list = [data_dict]
            rc_todata(data_list)

    except Exception as e:
        error_message = str(e)
        print(e)
except Exception as e:
    error_message = str(e)
    data_dict = {
        "success": False,
        "用户": "无法获取",
        "创建了采购订单": error_message,
        "OA流程编号": "无法获取",
        "requestid": ""
    }
    data_list = [data_dict]
    data_json = json.dumps(data_dict, ensure_ascii=False)
    rc_todata(data_list)
    print(json.dumps({"success": False}))