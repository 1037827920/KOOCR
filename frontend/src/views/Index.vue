<template>
  <div class="wrapper">
    <a-row>
      <a-col :lg="10" :md="10" :sm="9">
        <div class="left-wrapper">
          <!-- <div class="up-img-wrapper"> -->
          <!-- :beforeUpload="beforeUpload" -->
          <div class="upimg-dragger">
            <a-upload-dragger name="file" action="/tools/ocr_text/" @change="handleChange"
              accept=".jpg, .jpeg, .png, .gif, .ico" :beforeUpload="beforeUpload" listType="picture"
              :showUploadList="false">
              <p>点击、拖动、或者粘贴图片</p>
            </a-upload-dragger>
          </div>
          <div class="up-img-preview">
            <!--  -->
            <img :src="upImage" alt="预览图片" :hidden="previewImgHidden" />
          </div>
          <!-- </div> -->
        </div>
      </a-col>

      <a-col :lg="3" :md="4" :sm="6">
        <div class="split">
          <div class="divider"></div>
          <div class="btn-group">
            <a-button @click="handleUpload" :loading="isOCRing">识别</a-button>
            <!-- 压缩图片、显示检测后的图片、显示原始值、显示纯文字 -->
            <div style="margin-top:1rem;">
              <p>
                压缩图片:
                <a-switch style="width:auto;min-width:45%;" checked-children="开" un-checked-children="关" default-checked
                  @change="changeCompressBtn" />
              </p>
              <p :hidden="hiddenCompressBox">
                压缩尺寸:
                <a-input-number style="width:auto;max-width:45%;" id="compressSizeInput" size="small"
                  v-model="comporessSize" :min="1" />
                <!-- @change="onChange" -->
              </p>
            </div>
          </div>

        </div>
      </a-col>

      <a-col :lg="11" :md="10" :sm="9">
        <div class="right-wrapper">
          <div class="detected-img" :hidden="hiddenDetectedImg">
            <a-divider orientation="left">文字检测结果</a-divider>

            <img :src="detectedImg" alt="检测结果图片" />
          </div>

          <div class="ocr-raw" :hidden="hiddenOcrRaw">
            <a-divider orientation="left">原始结果</a-divider>
            <CodeHighlight :txt="ocrRaw" />
          </div>

          <div class="ocr-text" :hidden="hiddenOcrText">
            <a-divider orientation="left">识别的文字</a-divider>
            <CodeHighlight :txt="ocrText" />
          </div>
        </div>
      </a-col>
    </a-row>
  </div>
</template>

<script>
import { defineComponent } from 'vue'
import { message } from 'ant-design-vue'
import axios from 'axios'
import CodeHighlight from '../components/CodeHighlight.vue'

// 获取上传对象的临时链接
function getObjectURL(file) {
  let url = null
  if (window.createObjectURL != undefined) {
    url = window.createObjectURL(file)
  } else if (window.URL != undefined) {
    url = window.URL.createObjectURL(file)
  } else if (window.webkitURL != undefined) {
    url = window.webkitURL.createObjectURL(file)
  }
  return url
}

export default defineComponent({
  name: 'IndexPage',
  components: {
    CodeHighlight
  },
  data: function () {
    return {
      upImage: '', // 上传后的图片预览地址
      fileList: [], // 上传图片的列表
      detectedImg: '', // 检测后的图片
      ocrRaw: ``, // 返回的原始结果
      ocrText: ``, // 经过提取后的文字结果

      uploading: false, //状态 原生 上传控件的状态
      previewImgHidden: true, // 状态 预览图片是否隐藏
      isOCRing: false, // 状态 是否在识别中
      hiddenDetectedImg: true, //状态  是否显示检测后的图片
      hiddenOcrRaw: true, // 状态  是否显示返回的原始结果
      hiddenOcrText: true, // 状态 是否显示经过提取后的文字结果
      comporessSize: 1600,
      hiddenCompressBox: false
    }
  },
  methods: {
    changeCompressBtn(checked) {
      this.hiddenCompressBox = !checked
    },
    handleChange(info) {
      const status = info.file.status
      if (status !== 'uploading') {
        this.fileList = [info.file]
        this.upImage = getObjectURL(info.file)
        this.previewImgHidden = false
        console.log('success')
      }
      if (status === 'done') {
        message.success(`${info.file.name} file uploaded successfully.`)
      } else if (status === 'error') {
        message.error(`${info.file.name} file upload failed.`)
        console.log('error')
      }
    },
    beforeUpload(file) {
      this.fileList = [file]
      return false
    },
    handleUpload() {
      if (this.fileList.length < 1) {
        message.warning('还没有选择图片')
        return
      }
      console.log('fileList', this.fileList)

      const formData = new FormData()
      this.fileList.forEach(file => {
        formData.append('file', file)
      })
      formData.append('compress', this.hiddenCompressBox ? 0 : this.comporessSize)

      // 遍历 FormData
      for (let [key, value] of formData.entries()) {
        console.log(`${key}:`, value)
      }


      this.isOCRing = true
      this.uploading = true

      axios({
        // url: '/api/tr-run/',
        url: '/api/tr-run/',
        method: 'post',
        headers: {
          'Content-Type': 'multipart/form-data',
          'X-Requested-With': 'XMLHttpRequest'
        },
        transformRequest: {},
        data: formData
      })
        .then(response => {
          this.detectedImg = response.data.data.img_detected
          this.ocrRaw = ''
          this.ocrText = ''

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
          this.isOCRing = false
          this.hiddenDetectedImg = false
          this.hiddenOcrRaw = false
          this.hiddenOcrText = false

          message.success('成功! 耗时：' + response.data.data.speed_time + ' 秒')
        })
        .catch(error => {
          this.isOCRing = false
          const errorInfo = error.response?.msg || error.message
          message.error('错误：' + errorInfo)
          this.hiddenDetectedImg = true
          this.hiddenOcrRaw = true
          this.hiddenOcrText = true
        })
    }
  },
  watch: {
    fileList(newVal) {
      if (newVal.length <= 0) {
        this.hiddenDetectedImg = true
        this.hiddenOcrRaw = true
        this.hiddenOcrText = true
      }
    }
  },
  mounted() {
    this.$nextTick(() => {
      document.addEventListener('paste', event => {
        const items = event.clipboardData?.items
        let file = null
        if (items && items.length) {
          for (let i = 0; i < items.length; i++) {
            if (items[i].type.includes('image')) {
              file = items[i].getAsFile()
              break
            }
          }
        }

        if (file) {
          this.fileList = [file]
          this.upImage = getObjectURL(file)
          this.previewImgHidden = false
        }
        console.log(this.fileList)
      })
    })
  }
})
</script>

<style>
/* >>>>>>  覆盖原生样式 */
.ant-divider-inner-text {
  font-size: 14px;
  color: gray;
}

/* <<<<<<  覆盖原生样式 */

.wrapper {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  min-height: 100%;
  height: auto;
}

.left-wrapper {
  min-height: 100vh;
  height: auto;
}

.upimg-dragger {
  height: 4rem;
  margin: 2.5rem 0 1rem 2.5rem;
}

.up-img-preview {
  text-align: center;

  margin: 1.5rem -1rem 1rem 1rem;
}

.up-img-preview img {
  object-fit: contain;
  max-width: 95%;
  max-height: 80vh;
}

.split {
  min-height: 100%;
  /* border: solid gray 1px; */
  height: 100vh;
  position: relative;
}

.divider {
  position: absolute;
  left: 50%;
  top: 0;
  min-height: 100%;
  height: auto;
  width: 1px;
  border-left: 1px solid #d3d3d36b;
}

.btn-group {
  text-align: center;
  margin: 2.5rem 0;
  padding: 1rem;
  background: white;
  width: 100%;
  position: absolute;
}

.btn-group button {
  width: 90%;
}

.right-wrapper {
  padding: 1rem 2.5rem 1rem 0;
}

.detected-img {
  max-height: 50%;
  /* border: 1px solid gray; */
  text-align: center;
}

.detected-img img {
  object-fit: contain;
  max-width: 100%;
  max-height: 40vh;
}

.detected-img .ocr-raw {
  max-height: 40vh;
}

.detected-img .ocr-text {
  max-height: 40vh;
}
</style>