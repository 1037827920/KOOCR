#!/usr/bin/env python
# encoding: utf-8
# author:alisen
# time: 2020/4/29 10:47

import time
import cv2
import numpy as np
from backend.tr import tr
import tornado.web
import tornado.gen
import tornado.httpserver
import base64
from PIL import Image, ImageDraw
from io import BytesIO
import datetime
import json

from backend.tools.np_encoder import NpEncoder
from backend.tools import log
import logging
import asyncio
from concurrent.futures import ThreadPoolExecutor

logger = logging.getLogger(log.LOGGER_ROOT_NAME + '.' + __name__)

# 将OCR处理逻辑封装为异步函数
def process_image(img, compress_size, is_draw, start_time):
    try:
        MAX_SIZE = 1600
        
        # 旋转图片
        if hasattr(img, '_getexif') and img._getexif() is not None:
            orientation = 274
            exif = dict(img._getexif().items())
            if orientation in exif:
                if exif[orientation] == 3:
                    img = img.rotate(180, expand=True)
                elif exif[orientation] == 6:
                    img = img.rotate(270, expand=True)
                elif exif[orientation] == 8:
                    img = img.rotate(90, expand=True)
        img = img.convert("RGB")

        # 压缩图片
        if compress_size is not None:
            compress_size = int(compress_size)
            MAX_SIZE = compress_size if compress_size >= 1 else max(img.height, img.width)

        # 是否开启图片压缩
        if img.height > MAX_SIZE or img.width > MAX_SIZE:
            scale = max(img.height / MAX_SIZE, img.width / MAX_SIZE)
            new_width = int(img.width / scale + 0.5)
            new_height = int(img.height / scale + 0.5)
            img = img.resize((new_width, new_height), Image.ANTIALIAS)

        # 执行OCR
        res = tr.run(img.copy().convert("L"), flag=tr.FLAG_ROTATED_RECT)
        result = {'raw_out': res, 'speed_time': round(time.time() - start_time, 2)}

        # 是否绘制检测框
        if is_draw != '0':
            img_detected = img.copy()
            img_draw = ImageDraw.Draw(img_detected)
            colors = ['red', 'green', 'blue', "purple"]

            for i, r in enumerate(res):
                rect, txt, confidence = r
                cx, cy, w, h, a = rect
                box = cv2.boxPoints(((cx, cy), (w, h), a))
                box = np.int0(np.round(box))

                for p1, p2 in [(0, 1), (1, 2), (2, 3), (3, 0)]:
                    img_draw.line(
                        xy=(box[p1][0], box[p1][1], box[p2][0], box[p2][1]),
                        fill=colors[i % len(colors)],
                        width=2
                    )

            # 将图片转为base64
            output_buffer = BytesIO()
            img_detected.save(output_buffer, format='JPEG')
            byte_data = output_buffer.getvalue()
            img_detected_b64 = base64.b64encode(byte_data).decode('utf8')

            result['img_detected'] = 'data:image/jpeg;base64,' + img_detected_b64

        return result

    except Exception as ex:
        logger.error(f"处理文件时出错: {str(ex)}", exc_info=True)
        return {'error': str(ex)}

class TrRun(tornado.web.RequestHandler):
    # 初始化线程池
    executor = ThreadPoolExecutor(max_workers=4)

    def get(self):
        self.set_status(404)
        self.write("404 : Please use POST")

    # 并发处理OCR识别
    async def post(self):
        start_time = time.time()

        # 获取上传的图片
        img_ups = self.request.files.get('file', [])
        img_b64 = self.get_argument('img', None)
        compress_size = self.get_argument('compress', None)
        is_draw = self.get_argument("is_draw", None)

        self.set_header('content-type', 'application/json')

        response_data = {'code': 200, 'msg': '成功', 'data': {'results': [], 'speed_time': None}}

        if not img_ups and not img_b64:
            self.set_status(400)
            logger.error(json.dumps({'code': 400, 'msg': 'No incoming argument'}, cls=NpEncoder))
            self.finish(json.dumps({'code': 400, 'msg': 'No incoming argument'}, cls=NpEncoder))
            return

        loop = asyncio.get_event_loop()
        tasks = []

        for img_up in img_ups:
            try:
                img = Image.open(BytesIO(img_up.body))
                # 提交OCR处理任务到线程池
                task = loop.run_in_executor(
                    self.executor,
                    process_image,
                    img,
                    compress_size,
                    is_draw,
                    start_time
                )
                tasks.append(task)
            except Exception as ex:
                logger.error(f"处理文件 {img_up.filename} 时出错: {str(ex)}", exc_info=True)
                response_data['data']['results'].append({'error': str(ex)})

        # 等待所有OCR任务完成
        if tasks:
            results = await asyncio.gather(*tasks)
            for result in results:
                response_data['data']['results'].append(result)

        # 记录处理时间
        response_data['data']['speed_time'] = round(time.time() - start_time, 2)
        log_info = {
            'ip': self.request.host,
            'return': response_data,
            'time': datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }
        logger.info(json.dumps(log_info, cls=NpEncoder))
        self.finish(json.dumps(response_data, cls=NpEncoder))
        return
    
    # 还没有实现并发处理的函数
    # @tornado.gen.coroutine
    # def post(self):
    #     '''

    #     :return:
    #     报错：
    #     400 没有请求参数

    #     '''
    #     # 请求开始时间
    #     start_time = time.time()
    #     # 压缩图片的最大尺寸
    #     MAX_SIZE = 1600

    #     # 获取上传的图片
    #     img_ups = self.request.files.get('file', [])
    #     img_b64 = self.get_argument('img', None)
    #     compress_size = self.get_argument('compress', None)
    #     is_draw = self.get_argument("is_draw", None)

    #     # 判断是上传的图片还是base64
    #     self.set_header('content-type', 'application/json')

    #     response_data = {'code': 200, 'msg': '成功', 'data': {'results': [], 'speed_time': None}}

    #     print(img_ups)
    #     print(img_b64)
    #     if not img_ups and not img_b64:
    #         self.set_status(400)
    #         logger.error(json.dumps({'code': 400, 'msg': 'No incoming argument'}, cls=NpEncoder))
    #         self.finish(json.dumps({'code': 400, 'msg': 'No incoming argument'}, cls=NpEncoder))
    #         return

    #     # 处理多个上传文件
    #     for img_up in img_ups:
    #         try:
    #             # 读取图片
    #             img = Image.open(BytesIO(img_up.body))

    #             # 旋转图片
    #             if hasattr(img, '_getexif') and img._getexif() is not None:
    #                 # 274 是exif中的旋转信息
    #                 orientation = 274
    #                 exif = dict(img._getexif().items())
    #                 if orientation in exif:
    #                     if exif[orientation] == 3:
    #                         img = img.rotate(180, expand=True)
    #                     elif exif[orientation] == 6:
    #                         img = img.rotate(270, expand=True)
    #                     elif exif[orientation] == 8:
    #                         img = img.rotate(90, expand=True)
    #             img = img.convert("RGB")

    #             # 压缩图片
    #             if compress_size is not None:
    #                 compress_size = int(compress_size)
    #                 MAX_SIZE = compress_size if compress_size >= 1 else max(img.height, img.width)
                
    #             '''
    #             是否开启图片压缩
    #             默认为1600px
    #             值为 0 时表示不开启压缩
    #             非 0 时则压缩到该值的大小
    #             '''
    #             # 如果图片尺寸大于最大尺寸则进行压缩
    #             if img.height > MAX_SIZE or img.width > MAX_SIZE:
    #                 scale = max(img.height / MAX_SIZE, img.width / MAX_SIZE)
    #                 new_width = int(img.width / scale + 0.5)
    #                 new_height = int(img.height / scale + 0.5)
    #                 img = img.resize((new_width, new_height), Image.ANTIALIAS)

    #             # 执行ocr
    #             res = tr.run(img.copy().convert("L"), flag=tr.FLAG_ROTATED_RECT)
    #             result = {'raw_out': res, 'speed_time': round(time.time() - start_time, 2)}

    #             # 是否绘制检测框
    #             if is_draw != '0':
    #                 img_detected = img.copy()
    #                 img_draw = ImageDraw.Draw(img_detected)
    #                 colors = ['red', 'green', 'blue', "purple"]

    #                 for i,r in enumerate(res):
    #                     rect, txt, confidence = r
    #                     ''' 
    #                         cx: 中心点x
    #                         xy: 中心点y
    #                         w:  宽度
    #                         h:  高度
    #                         a:  旋转角度
    #                     '''
    #                     cx, cy, w, h, a = rect
    #                     box = cv2.boxPoints(((cx, cy), (w, h), a))
    #                     box = np.int0(np.round(box))

    #                     for p1, p2 in [(0, 1), (1, 2), (2, 3), (3, 0)]:
    #                         img_draw.line(xy=(box[p1][0], box[p1][1], box[p2][0], box[p2][1]),
    #                                       fill=colors[i % len(colors)], width=2)

    #                 # 将图片转为base64
    #                 output_buffer = BytesIO()
    #                 img_detected.save(output_buffer, format='JPEG')
    #                 byte_data = output_buffer.getvalue()
    #                 img_detected_b64 = base64.b64encode(byte_data).decode('utf8')

    #                 result['img_detected'] = 'data:image/jpeg;base64,' + img_detected_b64
    #             response_data['data']['results'].append(result)
    #         except Exception as ex:
    #             logger.error(f"处理文件 {img_up.filename} 时出错: {str(ex)}", exc_info=True)
    #             response_data['data']['results'].append({'error': str(ex)})

    #     # 记录处理时间
    #     response_data['data']['speed_time'] = round(time.time() - start_time, 2)
    #     log_info = {
    #         'ip': self.request.host,
    #         'return': response_data,
    #         'time': datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    #     }
    #     logger.info(json.dumps(log_info, cls=NpEncoder))
    #     self.finish(json.dumps(response_data, cls=NpEncoder))
    #     return