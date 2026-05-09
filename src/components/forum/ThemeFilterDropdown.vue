<template>
  <div class="theme-filter">
    <div class="custom-select" @click="toggleDropdown" :class="{ 'open': isOpen }">
      <div class="select-trigger">
        <span class="select-text">{{ getSelectedLabel() }}</span>
        <svg class="dropdown-arrow" :class="{ 'rotated': isOpen }" viewBox="0 0 24 24" fill="none">
          <path d="M6 9l6 6 6-6" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
        </svg>
      </div>

      <div class="select-dropdown" v-show="isOpen">
        <div
          v-for="option in options"
          :key="option.value"
          class="select-option"
          :class="{ 'selected': option.value === filterTheme }"
          @click="selectOption(option.value)"
        >
          {{ option.label }}
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, defineProps, defineEmits, onMounted, onUnmounted } from 'vue';

const props = defineProps({
  initialTheme: {
    type: String,
    default: ''
  }
});

const emits = defineEmits(['load-posts']);
const filterTheme = ref(props.initialTheme);
const isOpen = ref(false);

// 下拉选项
const options = [
  { value: '', label: '全部主题' },
  { value: 'tech', label: '技术' },
  { value: 'life', label: '生活' },
  { value: 'entertainment', label: '娱乐' },
  { value: 'other', label: '其他' }
];

// 获取当前选中的标签
const getSelectedLabel = () => {
  const selected = options.find(option => option.value === filterTheme.value);
  return selected ? selected.label : '全部主题';
};

// 切换下拉菜单
const toggleDropdown = () => {
  isOpen.value = !isOpen.value;
};

// 选择选项
const selectOption = (value) => {
  filterTheme.value = value;
  isOpen.value = false;
  emits('load-posts', filterTheme.value);
};

// 点击外部关闭下拉菜单
const handleClickOutside = (event) => {
  if (!event.target.closest('.theme-filter')) {
    isOpen.value = false;
  }
};

onMounted(() => {
  document.addEventListener('click', handleClickOutside);
});

onUnmounted(() => {
  document.removeEventListener('click', handleClickOutside);
});
</script>

<style scoped>
/* 深色主题筛选下拉菜单样式 */
.theme-filter {
  position: relative;
  min-width: 160px;
}

.custom-select {
  position: relative;
  cursor: pointer;
}

.select-trigger {
  display: flex;
  align-items: center;
  justify-content: space-between;
  background: var(--card-bg);
  border: 1px solid var(--border-color);
  color: var(--light-text);
  padding: 10px 16px;
  border-radius: 8px;
  font-size: 14px;
  font-weight: 500;
  transition: all 0.3s ease;
  gap: 12px;
}

.select-trigger:hover {
  background: #2a2a2a;
  border-color: rgba(255, 255, 255, 0.25);
}

.custom-select.open .select-trigger {
  border-color: rgba(255, 255, 255, 0.3);
  box-shadow: 0 0 0 2px rgba(255, 255, 255, 0.1);
  background: rgba(255, 255, 255, 0.1);
}

.select-text {
  flex: 1;
  text-align: left;
}

.dropdown-arrow {
  width: 16px;
  height: 16px;
  color: #b3b3b3;
  transition: all 0.3s ease;
  flex-shrink: 0;
}

.dropdown-arrow.rotated {
  transform: rotate(180deg);
  color: #ffffff;
}

.select-dropdown {
  position: absolute;
  top: 100%;
  left: 0;
  right: 0;
  background: rgba(0, 0, 0, 0.9);
  border: 1px solid rgba(255, 255, 255, 0.15);
  border-radius: 8px;
  margin-top: 4px;
  z-index: 1000;
  backdrop-filter: blur(10px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.3);
  overflow: hidden;
}

.select-option {
  padding: 12px 16px;
  color: rgba(255, 255, 255, 0.8);
  cursor: pointer;
  transition: all 0.3s ease;
  font-size: 14px;
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
}

.select-option:last-child {
  border-bottom: none;
}

.select-option:hover {
  background: rgba(255, 255, 255, 0.05);
  color: #ffffff;
}

.select-option.selected {
  background: rgba(255, 255, 255, 0.1);
  color: #ffffff;
  font-weight: 600;
}

.select-option.selected:hover {
  background: rgba(255, 255, 255, 0.15);
}

/* 动画效果 */
.select-dropdown {
  animation: slideDown 0.2s ease-out;
}

@keyframes slideDown {
  from {
    opacity: 0;
    transform: translateY(-8px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}
</style>