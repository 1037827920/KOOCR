import os
import tornado.web

# 上传文件保存目录
UPLOAD_DIR = os.path.join(os.path.dirname(__file__), "../uploads")
os.makedirs(UPLOAD_DIR, exist_ok=True)  # 确保上传目录存在

class FileUploadHandler(tornado.web.RequestHandler):
    def post(self):
        # 检查是否有文件上传
        if "file" not in self.request.files:
            self.set_status(400)
            print(f'没有文件上传')
            return

        # 获取上传的文件
        file_info = self.request.files["file"][0]
        filename = file_info["filename"]
        file_body = file_info["body"]

        # 将文件保存到指定目录
        file_path = os.path.join(UPLOAD_DIR, filename)
        with open(file_path, "wb") as f:
            f.write(file_body)

        print(f'文件上传成功, 文件名: {filename}')
