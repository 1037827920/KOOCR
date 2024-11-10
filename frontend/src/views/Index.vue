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
              <div class="expand-modal-header">
                <div class="text-large">原始图片</div>
                <!-- 将header分为两部分 -->
                <a-divider direction="vertical" :size="5" />
                <div class="text-large">识别结果</div>
              </div>

              <!-- 分别header和content -->
              <a-divider direction="horizontal" :size="4" />

              <!-- content区域 -->

              <div class="expand-modal-content">
                <!-- 左侧区域 -->
                <div class="modal-left">
                  <a-image :src="preview_image_list[current_preview_index]" alt="原始图片" width="400" height="300"
                    fit="fill" />
                </div>
                <!-- 将content分为两部分 -->

                <a-divider direction="vertical" :size="5" type="dashed" />

                <!-- 右侧区域 -->
                <div class="modal-right">
                  <a-divider orientation="center">识别后的图片</a-divider>
                  <div class="right-image-container">
                    <a-image :src="detected_list[current_preview_index]" alt="识别后的图片" width="400" height="300"
                      fit="fill"></a-image>
                  </div>
                  <a-divider orientation="center">原始结果</a-divider>
                  <CodeHighlight class="code-highlight" :txt="ocr_raw[current_preview_index]" />
                  <a-divider orientation="center">识别的文字</a-divider>
                  <CodeHighlight class="code-highlight" :txt="ocr_text[current_preview_index]" />
                </div>
              </div>
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
    // 点击识别icon的回调函数，处理单个图片的识别
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
      const file = this.file_list[index]
      // console.log('file: ', file)

      // 创建一个 FormData 对象
      const formData = new FormData()
      formData.append('file', file)
      formData.append('compress', this.is_compress ? this.compress_size : 0)
      formData.append('is_draw', '1'); // 添加是否绘制检测框的参数

      // 日志输出formData
      // for (let [key, value] of formData.entries()) {
      //   console.log(`${key}:`, value)
      // }

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
          // 获取识别结果
          const result = response.data.data.results[0]
          // console.log('result: ', result)

          // 处理img_detected
          if (result.img_detected) {
            // console.log('result.img_detected: ', result.img_detected)
            this.detected_list[index] = result.img_detected
          } else {
            this.detected_list[index] = ''
          }

          // 处理raw_out
          if (result.raw_out) {
            // console.log('result.raw_out: ', result.raw_out)
            let new_ocr_raw = ''
            let new_ocr_text = ''
            result.raw_out.forEach((item, i) => {
              new_ocr_raw += JSON.stringify(item) + '\r'
              if (i < result.raw_out.length - 1) {
                const nextLineHeight = result.raw_out[i + 1][0][1]
                if (Math.abs(item[0][1] - nextLineHeight) < item[0][3] / 2) {
                  new_ocr_text += item[1] + ' '
                } else {
                  new_ocr_text += item[1] + '\r'
                }
              } else {
                new_ocr_text += item[1]
              }
            })
            // console.log('new_ocr_raw: ', new_ocr_raw)
            // console.log('new_ocr_text: ', new_ocr_text)
            this.ocr_raw[index] = new_ocr_raw
            this.ocr_text[index] = new_ocr_text
          } else {
            this.ocr_raw[index] = ''
            this.ocr_text[index] = ''
          }

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
          this.uploading = false;
          const errorInfo = error.response?.data?.msg || error.message
          this.$message.error({
            id: 'myError',
            content: '错误：' + errorInfo,
            closable: true,
          })
        })
    },
    // 点击开始识别按钮的回调函数，处理所有图片的识别
    handleUpload() {
      console.log('<handleUpload>')
      // 如果正在识别中，则提示用户
      if (this.is_ocring) {
        this.$message.warning({
          id: 'myWarning',
          content: '正在识别中，请稍后再次尝试',
          closable: true,
        })
        return
      }
      // 如果没有选择图片，则提示用户
      if (this.file_list.length < 1) {
        this.$message.warning({
          id: 'myWarning',
          content: '还没有选择图片',
          closable: true,
        })
        return
      }

      // 过滤出未被识别的图片及其索引
      const unprocessedFiles = []
      const unprocessedIndices = []
      this.file_list.forEach((file, index) => {
        if (!this.detected_list[index]) {
          unprocessedFiles.push(file)
          unprocessedIndices.push(index)
        }
      })
      // 如果所有图片都已经被识别过了，则提示用户
      if (unprocessedFiles.length === 0) {
        this.$message.warning({
          id: 'myWarning',
          content: '所有图片都已经识别过了, 无需再次提交',
          closable: true,
        })
        return
      }
      // console.log('未识别的文件列表: ', unprocessedFiles)
      // console.log('对应的索引: ', unprocessedIndices)


      // 创建一个 FormData 对象
      const formData = new FormData()
      // 遍历未识别的文件列表，将文件加入到 FormData 中
      unprocessedFiles.forEach(file => {
        formData.append('file', file)
      })
      // 将是否压缩图片的状态加入到 FormData 中
      formData.append('compress', this.is_compress ? this.compress_size : 0)
      // 添加是否绘制检测框的参数
      formData.append('is_draw', '1')

      // 日志输出：遍历 FormData
      // for (let [key, value] of formData.entries()) {
      //   console.log(`${key}:`, value)
      // }

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
          const response_data = response.data.data
          const results = response_data.results || []
          // console.log('results: ', results)

          // 遍历每个结果并更新对应的数据列表
          results.forEach((result, idx) => {
            const originalIndex = unprocessedIndices[idx]

            // 处理img_detected
            if (result.img_detected) {
              this.detected_list[originalIndex] = result.img_detected
            } else {
              this.detected_list[originalIndex] = ''
            }

            // 处理raw_out
            if (result.raw_out) {
              let new_ocr_raw = ''
              let new_ocr_text = ''
              result.raw_out.forEach((item, i) => {
                new_ocr_raw += JSON.stringify(item) + '\r'
                if (i < result.raw_out.length - 1) {
                  const nextLineHeight = result.raw_out[i + 1][0][1]
                  if (Math.abs(item[0][1] - nextLineHeight) < item[0][3] / 2) {
                    new_ocr_text += item[1] + ' '
                  } else {
                    new_ocr_text += item[1] + '\r'
                  }
                } else {
                  new_ocr_text += item[1]
                }
              })
              this.ocr_raw[originalIndex] = new_ocr_raw
              this.ocr_text[originalIndex] = new_ocr_text
            } else {
              this.ocr_raw[originalIndex] = ''
              this.ocr_text[originalIndex] = ''
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
          const errorInfo = error.response?.data?.msg || error.message
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

.expand-modal-header {
  display: flex;
  justify-content: center;
  align-items: center;
  height: 5px;
}

.text-large {
  width: 50%;
  font-size: 15px;
  display: flex;
  justify-content: center;
  align-items: center;
}

.expand-modal-content {
  display: flex;
  overflow-x: hidden;
  overflow-y: auto;
  max-height: 80vh;
}

.modal-left {
  width: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
}

.modal-right {
  width: 50%;
  box-sizing: border-box;
  overflow-y: auto;
  display: flex;
  flex-direction: column;
  padding-right: 15px;
}

.right-image-container {
  display: flex;
  justify-content: center;
  /* 水平居中 */
  align-items: center;
  /* 垂直居中 */
  margin: 10px 0;
  /* 根据需要调整上下间距 */
}

.code-highlight {
  /* 代码块之间的垂直间隔 */
  margin-bottom: 5px;
  /* 为滚动条留出空间 */
  padding-right: 7px;
  box-sizing: border-box;
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
</style>