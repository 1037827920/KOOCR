import { createApp } from 'vue'
import App from './App.vue'
import router from './router'
import {
  Button,
  Layout,
  Input,
  Row,
  Col,
  Divider,
  Upload,
} from 'ant-design-vue' // Vue3 没有Icon组件了，所以压缩图片那里按钮不见了
import 'ant-design-vue/dist/antd.css'
import axios from 'axios'
import Vue3HighlightJS from 'vue3-highlightjs'
// 导入字节ui库
import ArcoVue from '@arco-design/web-vue';
import ArcoVueIcon from '@arco-design/web-vue/es/icon';
import '@arco-design/web-vue/dist/arco.css';

const app = createApp(App)

app.use(router)
app.use(Vue3HighlightJS)


app.use(Button)
app.use(Layout)
app.use(Input)
app.use(Row)
app.use(Col)
app.use(Divider)
app.use(Upload)
app.use(ArcoVue)
app.use(ArcoVueIcon)

app.config.productionTip = false

axios.defaults.headers.post['Content-Type'] = 'application/x-www-form-urlencoded';
axios.defaults.headers.get['Content-Type'] = 'application/x-www-form-urlencoded';
axios.defaults.transformRequest = [
  function (data) {
    let ret = ''
    for (let it in data) {
      ret += encodeURIComponent(it) + '=' + encodeURIComponent(data[it]) + '&'
    }
    return ret
  },
]

app.mount('#app')