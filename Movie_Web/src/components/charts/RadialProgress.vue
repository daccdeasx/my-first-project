<!-- src/components/charts/RadialProgress.vue -->
<template>
  <div class="radial-progress">
    <div class="relative w-full h-40">
      <svg class="w-full h-full" viewBox="0 0 100 100">
        <circle 
          class="text-gray-200"
          stroke-width="10"
          :stroke-dasharray="circumference"
          stroke-linecap="round"
          fill="transparent"
          r="45"
          cx="50"
          cy="50"
        />
        <circle 
          :class="`text-${color}-500`"
          stroke-width="10"
          :stroke-dasharray="dashArray"
          stroke-linecap="round"
          fill="transparent"
          r="45"
          cx="50"
          cy="50"
          transform="rotate(-90 50 50)"
        />
      </svg>
      <div class="absolute inset-0 flex flex-col items-center justify-center">
        <div class="text-2xl font-bold" :class="`text-${color}-600`">
          {{ percentage }}%
        </div>
        <div class="text-sm text-gray-500">{{ label }}</div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  percentage: Number,
  label: String,
  color: {
    type: String,
    default: 'blue'
  }
})

const circumference = 2 * Math.PI * 45
const dashArray = computed(() => {
  const progress = props.percentage / 100
  return `${circumference * progress} ${circumference}`
})
</script>