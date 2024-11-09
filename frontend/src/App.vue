<template>
  <div>
    <a-layout class="layout">
      <a-layout-sider breakpoint="lg"></a-layout-sider>
      <a-layout-content>
        <router-view />
      </a-layout-content>
    </a-layout>
  </div>
</template>

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

}

.layout :deep(.arco-layout-content) {
  /* background-color: rgb(var(--arcoblue-6)); */
  /* 使内容区域自适应剩余宽度 */
  flex: 1;
  display: flex;
}
</style>
