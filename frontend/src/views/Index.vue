<template>
  <div class="img-ocr-page">
    <!-- 上传区域 -->
    <div class="upload-box">
      <a-upload draggable name="file" action="/api/upload" :show-file-list="false" @change="handleChange"
        accept=".jpg, .jpeg, .png, .gif, .ico" />
    </div>

    <!-- 预览图片区域 -->
    <div class="preview-image-wall">
      <a-image-preview-group>
        <!-- 使用v-for循环渲染图片列表 -->
        <a-image v-for="(image, index) in preview_image_list" :key="index" :src="image" fit="cover" width="100"
          height="150" class="preview-image">
          <!-- 图片的slot -->
          <template #extra>
            <!-- 关闭icon -->
            <div class="close-icon">
              <span @click="handleClose(index)"><icon-close /></span>
            </div>
            <!-- 底部的icon -->
            <div class="icon-group">
              <!-- 识别icon -->
              <div class="scan-icon">
                <span @click="handleSingleUpload(index)"><icon-scan /></span>
              </div>
              <!-- 打开预览icon -->
              <div class="expand-icon">
                <span @click="handlePreview(index)"><icon-expand /></span>
              </div>
            </div>
            <!-- 预览modal，显示原始图片和识别结果 -->
            <a-modal v-if="show_preview_modal" :visible="show_preview_modal" @ok="handleOk" @cancel="handelCancel"
              :footer="false" width="80%" :mask="true" :hide-title="true">
              <!-- header区域 -->
              <a-space direction="horizontal" :size="250" class="expand-modal" fill>
                <!-- 将header分为两部分 -->
                <template #split>
                  <a-divider direction="vertical" :size="5" />
                </template>
                <div class="text-large">原始图片</div>
                <div class="text-large">识别结果</div>
              </a-space>

              <!-- 分别header和content -->
              <a-divider direction="horizontal" :size="4" />

              <!-- content区域 -->
              <a-space direction="horizontal" :size="85" class="expand-modal" fill>
                <!-- 将content分为两部分 -->
                <template #split>
                  <a-divider direction="vertical" :size="5" type="dotted" />
                </template>
                <!-- 左侧区域 -->
                <div class="drawer-left">
                  <a-image :src="preview_image_list[current_preview_index]" alt="原始图片" width="400" height="300"
                    fit="fill" />
                </div>

                <!-- 右侧区域 -->
                <div class="drawer-right">
                  <a-divider orientation="center">识别后的图片</a-divider>
                  <a-image :src="detected_list[current_preview_index]" alt="识别后的图片" width="400" height="300"
                    fit="fill"></a-image>
                  <a-divider orientation="center">原始结果</a-divider>
                  <CodeHighlight :txt="ocr_raw[current_preview_index]" />
                  <a-divider orientation="center">识别的文字</a-divider>
                  <CodeHighlight :txt="ocr_text[current_preview_index]" />
                  <!-- <CodeHighlight txt="[[313.5,315,347,87.71428680419922,0],OpenGL" /> -->
                  <!-- <CodeHighlight txt="OpenGL JO01 
吏用glad和

glfw创建  

歹 
31
32 glClearCo 
33
34" /> -->
                </div>
              </a-space>
            </a-modal>
          </template>
        </a-image>
      </a-image-preview-group>
    </div>


    <!-- 操作区域 -->
    <div class="operating-area">
      <p class="operating-item">
        压缩图片：
        <a-switch type="round" :default-checked="true" @change="changeCompressButton">
          <template #checked>
            ON
          </template>
          <template #unchecked>
            OFF
          </template>
        </a-switch>
      </p>

      <p class="operating-item" :hidden="!is_compress">
        压缩尺寸：
        <a-input-number placeholder="请输入压缩尺寸" :default-value="1600" mode="button" size="mini" />
      </p>

      <p class="operating-item">
        <a-button type="primary" shape="round" long size="large" :loading="is_ocring" @click="handleUpload">
          {{ is_ocring ? '正在识别' : '开始识别' }}
        </a-button>
      </p>

    </div>
  </div>
</template>

<script>
import { defineComponent } from 'vue'
import axios from 'axios'
import CodeHighlight from '../components/CodeHighlight.vue'

export default defineComponent({
  name: 'IndexPage',
  components: {
    CodeHighlight
  },
  data: function () {
    return {
      file_list: [], // 上传的文件列表
      preview_image_list: [], // 上传后的图片预览地址
      current_preview_index: null, // 当前modal预览的图片索引（重要！！！modal内部不再对应于用户点击的图片，也就是index不再适用）
      is_ocring: false, // 状态 是否在识别中
      is_compress: true, // 是否压缩图片
      compress_size: 1600, // 压缩尺寸
      uploading: false, // 是否正在上传
      show_preview_modal: false, // 是否显示预览抽屉
      detected_list: [], // 检测后的图片
      ocr_raw: [], // 返回的原始结果
      ocr_text: [], // 经过提取后的文字结果
    }
  },
  methods: {
    // 上传文件时的回调函数
    handleChange(_, current_file) {
      console.log('<handleChange>')
      const status = current_file.status;
      if (status !== 'uploading') {
        // 检查file_list中是否已经存在该文件
        const file_exists = this.file_list.some(file => file.name === current_file.name)
        if (!file_exists) {
          console.log('success')
          this.file_list.push(current_file.file)
          // 获取预览地址
          let previewUrl = current_file.url;
          console.log('previewUrl: ', previewUrl)
          this.preview_image_list.push(previewUrl)
        }
      }
      if (status === 'done') {
        this.$message.success({
          id: 'mySuccess',
          content: '图片上传成功',
          closable: true,
        })
      } else if (status == 'error') {
        this.$message.error({
          id: 'myError',
          content: '图片上传失败',
          closable: true,
        })
      }
    },
    // 点击关闭按钮的回调函数
    handleClose(index) {
      console.log('<handleClose>')
      // 删除对应的文件
      this.file_list.splice(index, 1)
      // 删除对应的预览图片
      this.preview_image_list.splice(index, 1)
    },
    changeCompressButton() {
      console.log('<changeCompressButton>')
      this.is_compress = !this.is_compress
      console.log('is_compress: ', this.is_compress)
    },
    // 点击识别按钮的回调函数
    handleSingleUpload(index) {
      console.log('<handleSingleUpload>, index: ', index)
      // 如果正在识别中，则提示用户
      if (this.is_ocring) {
        this.$message.warning({
          id: 'myWarning',
          content: '正在识别中，请稍后再次尝试',
          closable: true,
        })
        return
      }
      // 如果当前索引的图片已经在detected_list存在，则不再重复识别
      if (this.detected_list[index]) {
        this.$message.warning({
          id: 'myWarning',
          content: '该图片已经识别过了',
          closable: true,
        })
        return
      }

      // 选择索引为index的图片
      console.log('file_list: ', this.file_list)
      const file = this.file_list[index]
      console.log('file: ', file)

      // 创建一个 FormData 对象
      const formData = new FormData()
      formData.append('file', file)
      formData.append('compress', this.is_compress ? this.compress_size : 0)
      // 日志输出formData
      for (let [key, value] of formData.entries()) {
        console.log(`${key}:`, value)
      }

      // 设置状态
      this.is_ocring = true
      this.uploading = true

      // 发送请求
      axios({
        url: '/api/tr-run/', // 请求地址
        method: 'post', // 请求方法
        headers: { // 请求头
          'Content-Type': 'multipart/form-data',
          'X-Requested-With': 'XMLHttpRequest'
        },
        transformRequest: {}, // 请求数据预处理
        data: formData // 请求数据
      })
        .then(response => {
          console.log('response: ', response)
          console.log('response.data.data.img_detected: ', response.data.data.img_detected)
          this.detected_list[index] = response.data.data.img_detected

          console.log('response.data.data.raw_out: ', response.data.data.raw_out)
          const raw_data = response.data.data.raw_out
          var new_ocr_raw = ''
          var new_ocr_text = ''
          raw_data.forEach((item, i) => {
            new_ocr_raw += JSON.stringify(item) + '\r'
            if (i < raw_data.length - 1) {
              const nextLineHeight = raw_data[i + 1][0][1]
              if (Math.abs(item[0][1] - nextLineHeight) < item[0][3] / 2) {
                new_ocr_text += item[1] + ' '
              } else {
                new_ocr_text += item[1] + '\r'
              }
            } else {
              new_ocr_text += item[1]
            }
          })
          console.log('new_ocr_raw: ', new_ocr_raw)
          console.log('new_ocr_text: ', new_ocr_text)
          this.ocr_raw[index] = new_ocr_raw
          this.ocr_text[index] = new_ocr_text

          this.uploading = false
          this.is_ocring = false

          this.$message.success({
            id: 'mySuccess',
            content: '成功! 耗时：' + response.data.data.speed_time + ' 秒',
            closable: true,
          })
        })
        .catch(error => {
          console.log('error: ', error)
          this.is_ocring = false
          const errorInfo = error.response?.msg || error.message
          this.$message.error({
            id: 'myError',
            content: '错误：' + errorInfo,
            closable: true,
          })
        })
    },
    handleUpload() {
      console.log('<handleUpload>')
      if (this.is_ocring) {
        this.$message.warning({
          id: 'myWarning',
          content: '正在识别中，请稍后再次尝试',
          closable: true,
        })
        return
      }
      if (this.file_list.length < 1) {
        this.$message.warning({
          id: 'myWarning',
          content: '还没有选择图片',
          closable: true,
        })
        return
      }
      console.log('file_list: ', this.file_list)

      // 创建一个 FormData 对象
      const formData = new FormData()
      // 遍历文件列表，将文件加入到 FormData 中
      this.file_list.forEach(file => {
        formData.append('file', file)
      })
      // 将是否压缩图片的状态加入到 FormData 中
      formData.append('compress', this.is_compress ? this.compress_size : 0)

      // 日志输出：遍历 FormData
      for (let [key, value] of formData.entries()) {
        console.log(`${key}:`, value)
      }

      // 设置状态
      this.is_ocring = true
      this.uploading = true

      // 发送请求
      axios({
        url: '/api/tr-run/', // 请求地址
        method: 'post', // 请求方法
        headers: { // 请求头
          'Content-Type': 'multipart/form-data',
          'X-Requested-With': 'XMLHttpRequest'
        },
        transformRequest: {}, // 请求数据预处理
        data: formData // 请求数据
      })
        .then(response => {
          console.log('response: ', response)
          this.detected_list = response.data.data.img_detected
          this.ocr_raw = ''
          this.ocr_text = ''

          const raw_data = response.data.data.raw_out
          raw_data.forEach((item, i) => {
            this.ocrRaw += JSON.stringify(item) + '\r'
            if (i < raw_data.length - 1) {
              const nextLineHeight = raw_data[i + 1][0][1]
              if (Math.abs(item[0][1] - nextLineHeight) < item[0][3] / 2) {
                this.ocrText += item[1] + ' '
              } else {
                this.ocrText += item[1] + '\r'
              }
            } else {
              this.ocrText += item[1]
            }
          })

          this.uploading = false
          this.is_ocring = false

          this.$message.success({
            id: 'mySuccess',
            content: '成功! 耗时：' + response.data.data.speed_time + ' 秒',
            closable: true,
          })
        })
        .catch(error => {
          console.log('error: ', error)
          this.is_ocring = false
          const errorInfo = error.response?.msg || error.message
          this.$message.error({
            id: 'myError',
            content: '错误：' + errorInfo,
            closable: true,
          })
        })
    },
    handlePreview(index) {
      console.log('<handlePreview>, index: ', index)
      this.current_preview_index = index
      this.show_preview_modal = true
    },
    handleOk() {
      console.log('<handleOk>')
      this.show_preview_modal = false
      // 重置当前预览的索引
      this.current_preview_index = null
    },
    handelCancel() {
      console.log('<handelCancel>')
      this.show_preview_modal = false
      // 重置当前预览的索引
      this.current_preview_index = null
    }
  },
})
</script>

<style>
.img-ocr-page {
  display: flex;
  /* 垂直排列子元素 */
  flex-direction: column;
  /* 垂直排列子元素 */
  align-items: flex-start;
  top: 10px;
  left: 10px;
  /* 调整宽度以适应间隔 */
  /* width: calc(100% - 40px); */
  min-height: 100%;
  height: auto;
  /* margin-left: 20px; */
}

.upload-box {
  /* 宽度 */
  width: 100%;
  /* 高度 */
  height: auto;
  /* 布局 */
  display: flex;
  /* 对齐 */
  align-items: center;
  /* 水平方向上将内部内容居中对齐 */
  justify-content: center;
  /* 在上传区域底部添加外边距 */
  margin-bottom: 20px;
  /* 鼠标悬停时的样式 */
  cursor: pointer;
  /* 设置相对位置 */
  position: relative;
  /* 与下方预览墙的间距 */
  margin-bottom: 20px;
  /* 实线边框 */
  border: 2px solid #d9d9d9;
}

/* 预览图片墙样式 */
.preview-image-wall {
  display: flex;
  /* 允许换行 */
  flex-wrap: wrap;
  /* 从左侧开始排列 */
  justify-content: flex-start;
  /* 图片之间的间距 */
  gap: 10px;
  width: 100%;
  margin-left: 20px;
}

.preview-image {
  /* 调整每张图片的宽度，根据需要调整比例 */
  width: calc(25% - 10px);
  height: 150px;
}

.close-icon {
  margin-left: 53px;
  margin-bottom: 115px;
  cursor: pointer;
  position: relative;
}

.close-icon:hover {
  background: rgba(100, 83, 83, 0.5);
}

.icon-group {
  display: flex;
  align-items: center;
  /* 设置图标间的间距 */
  gap: 5px;
  /* 根据需要调整位置 */
  position: absolute;
  bottom: 5px;
  right: 5px;
}

.scan-icon,
.expand-icon {
  cursor: pointer;
}

.scan-icon:hover,
.expand-icon:hover {
  background: rgba(100, 83, 83, 0.5);
}

.expand-modal {
  display: flex;
  justify-content: center;
  align-items: center;
}

.operating-area {
  /* 宽度 */
  width: 30%;
  /* 设置固定定位，使其相对于视口固定 */
  position: fixed;
  /* 距离视口底部和右侧的距离 */
  bottom: 30px;
  right: 30px;
  /* 设置块区域的背景和内边距 */
  background-color: rgba(255, 255, 255, 0.5);
  /* 半透明背景 */
  padding: 10px 20px;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.15);

  /* 确保内容水平排列 */
  display: flex;
  flex-direction: column;
  /* 关键属性：垂直排列 */

  /* 垂直方向上居中对齐 */
  align-items: center;

  /* 按钮间距 */
  gap: 10px;

  /* 确保在其他元素之上 */
  z-index: 1000;
}

/* 添加操作项的样式 */
.operating-item {
  display: flex;
  align-items: center;
  gap: 10px;
  width: 100%;
  /* 设置文本颜色为黑色 */
  color: black;
  /* 防止内容换行 */
  white-space: nowrap;
}

.operating-area a-button {
  width: 100%;
}

.text-large {
  font-size: 15px;
}
</style>