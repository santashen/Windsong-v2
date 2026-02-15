<template>
  <div class="chart-wrapper">
    <div ref="chartContainer" class="chart-container"></div>
  </div>
</template>

<script setup>
import { ref, onMounted, onBeforeUnmount } from 'vue'
import * as echarts from 'echarts'

const props = defineProps({
  config: { type: Object, required: true }
})

const chartContainer = ref(null)
let chartInstance = null
let intervalId = null
let dataBuffer = []
let resizeObserver = null

onMounted(() => {
  chartInstance = echarts.init(chartContainer.value)
  setChartOption()
  startDataGeneration()

  resizeObserver = new ResizeObserver(() => {
    chartInstance?.resize()
  })
  resizeObserver.observe(chartContainer.value)
})

onBeforeUnmount(() => {
  stopDataGeneration()
  resizeObserver?.disconnect()
  chartInstance?.dispose()
})

function setChartOption() {
  chartInstance.setOption({
    title: {
      text: props.config.title,
      textStyle: { fontSize: 14, color: '#1f2937' }
    },
    xAxis: {
      type: 'time',
      name: props.config.xAxisName,
      nameTextStyle: { color: '#6b7280', fontSize: 12 },
      axisLabel: { formatter: '{mm}:{ss}' },
      splitLine: { show: false }
    },
    yAxis: {
      type: 'value',
      name: props.config.yAxisName,
      nameTextStyle: { color: '#6b7280', fontSize: 12 },
      min: props.config.yMin,
      max: props.config.yMax,
      splitLine: { lineStyle: { color: '#f3f4f6' } }
    },
    series: [{
      type: 'line',
      showSymbol: false,
      data: [],
      smooth: true,
      lineStyle: { width: 2, color: '#3b82f6' },
      areaStyle: {
        color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
          { offset: 0, color: 'rgba(59, 130, 246, 0.15)' },
          { offset: 1, color: 'rgba(59, 130, 246, 0.02)' }
        ])
      }
    }],
    tooltip: {
      trigger: 'axis',
      formatter: (params) => {
        const p = params[0]
        if (!p) return ''
        const t = new Date(p.value[0])
        const time = `${String(t.getMinutes()).padStart(2, '0')}:${String(t.getSeconds()).padStart(2, '0')}`
        return `${time}<br/>${props.config.yAxisName}: ${p.value[1].toFixed(3)}`
      }
    },
    grid: { left: 60, right: 20, top: 40, bottom: 40 },
    animation: false
  })
}

function startDataGeneration() {
  const startTime = Date.now()
  intervalId = setInterval(() => {
    const now = Date.now()
    const elapsed = (now - startTime) / 1000
    const amplitude = (props.config.yMax - props.config.yMin) / 2
    const center = (props.config.yMax + props.config.yMin) / 2
    const value = center + amplitude * Math.sin(elapsed * 0.5) + (Math.random() - 0.5) * amplitude * 0.3

    dataBuffer.push({ value: [now, value] })

    const cutoff = now - props.config.timeWindow * 1000
    dataBuffer = dataBuffer.filter(d => d.value[0] >= cutoff)

    chartInstance.setOption({
      series: [{ data: dataBuffer }]
    })
  }, 100)
}

function stopDataGeneration() {
  if (intervalId) {
    clearInterval(intervalId)
    intervalId = null
  }
}
</script>

<style scoped>
.chart-wrapper {
  border: 1px solid var(--color-border);
  border-radius: 12px;
  background: var(--color-bg);
  overflow: hidden;
}

.chart-container {
  width: 100%;
  height: 300px;
}
</style>
