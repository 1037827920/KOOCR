<template>
  <div>
    <a-layout class="layout">
      <a-layout-sider breakpoint="lg">
        <div class="logo">
          <a-image src="/LOGO.png" width="150" />
        </div>
        <div class="option">
          <a-menu :style="{ width: '200px', height: '100%' }" :selected-keys="selectedKey"
            @menu-item-click="handleSelect">
            <a-menu-item key="0">图片文字提取</a-menu-item>
            <a-menu-item key="1">扫描PDF转文字</a-menu-item>
          </a-menu>
        </div>
      </a-layout-sider>
      <a-layout-content>
        <router-view />
      </a-layout-content>
    </a-layout>
  </div>
</template>

<script>

import { defineComponent, ref } from 'vue'

export default defineComponent({
  name: 'App',
  setup() {
    // 定义选中的菜单项
    const selectedKey = ref(['0'])

    // 处理菜单项选择事件
    const handleSelect = (key) => {
      selectedKey.value = [key]
    }

    return {
      selectedKey,
      handleSelect,
    }
  },
})
</script>

<!-- 定义scoped属性后，定义的CSS只作用于当前组件的元素，不会污染全局样式或影响其他组件 -->
<style scoped>
.layout {
  display: flex;
  /* 让布局占满视口高度 */
  height: 100vh;
}

.layout :deep(.arco-layout-sider-children),
.layout :deep(.arco-layout-content) {
  display: flex;
  flex-direction: column;
  justify-content: center;
  color: var(--color-white);
  font-size: 16px;
  font-stretch: condensed;
  text-align: center;
}

.layout :deep(.arco-layout-sider) {
  width: 206px;
  background-color: var(--color-primary-light-3);
  display: flex;
  flex-direction: column;
  /* 水平居中 */
  align-items: center;
  /* 从顶部开始排列 */
  justify-content: flex-start;
  /* 添加顶部内边距 */
  padding-top: 20px;
  /* 确保侧边栏高度占满视口 */
  height: 100vh;
}

/* 为 logo 添加样式 */
.logo {
  display: flex;
  justify-content: center;
  align-items: center;
  margin-top: 80px;
  /* 调整下边距，确保与 option 之间有间隔 */
}

/* 为 option 添加样式 */
.option {
  display: flex;
  justify-content: center;
  align-items: center;
  /* 自动填充顶部空间 */
  margin-top: 100px;
  /* 自动填充底部空间 */
  margin-bottom: auto;
  /* 确保菜单宽度适应容器 */
  width: 100%;
}

.layout :deep(.arco-layout-content) {
  /* 使内容区域自适应剩余宽度 */
  flex: 1;
  display: flex;
}
</style>
