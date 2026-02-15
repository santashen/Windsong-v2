<template>
  <div class="config-card">
    <div class="config-header">
      <h3 class="config-title">{{ config.title }}</h3>
      <button class="btn-remove" @click="$emit('remove')" title="Remove">×</button>
    </div>

    <div class="config-fields">
      <div class="field">
        <label class="field-label">Title</label>
        <input
          type="text"
          class="field-input"
          :value="config.title"
          @input="$emit('update', { title: $event.target.value })"
        />
      </div>

      <div class="field">
        <label class="field-label">X-Axis Name</label>
        <input
          type="text"
          class="field-input"
          :value="config.xAxisName"
          @input="$emit('update', { xAxisName: $event.target.value })"
        />
      </div>

      <div class="field">
        <label class="field-label">Y-Axis Name</label>
        <input
          type="text"
          class="field-input"
          :value="config.yAxisName"
          @input="$emit('update', { yAxisName: $event.target.value })"
        />
      </div>

      <div class="field">
        <label class="field-label">Y-Axis Min</label>
        <input
          type="number"
          class="field-input"
          :value="config.yMin"
          @input="$emit('update', { yMin: Number($event.target.value) })"
        />
      </div>

      <div class="field">
        <label class="field-label">Y-Axis Max</label>
        <input
          type="number"
          class="field-input"
          :value="config.yMax"
          @input="$emit('update', { yMax: Number($event.target.value) })"
        />
      </div>

      <div class="field">
        <label class="field-label">Time Window (s)</label>
        <input
          type="number"
          class="field-input"
          :value="config.timeWindow"
          min="1"
          @input="$emit('update', { timeWindow: Number($event.target.value) })"
        />
      </div>
    </div>
  </div>
</template>

<script setup>
defineProps({
  config: { type: Object, required: true }
})

defineEmits(['remove', 'update'])
</script>

<style scoped>
.config-card {
  border: 1px solid var(--color-border);
  border-radius: 12px;
  padding: 1.25rem;
  background: var(--color-bg);
}

.config-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1rem;
}

.config-title {
  font-size: 1rem;
  font-weight: 600;
  color: var(--color-text);
  margin: 0;
}

.btn-remove {
  width: 28px;
  height: 28px;
  border: 1px solid var(--color-border);
  border-radius: 6px;
  background: var(--color-bg);
  color: var(--color-text-secondary);
  font-size: 1.1rem;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.15s;
}

.btn-remove:hover {
  border-color: #ef4444;
  color: #ef4444;
  background: #fef2f2;
}

.config-fields {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 0.75rem;
}

.field-label {
  display: block;
  font-size: 0.8rem;
  font-weight: 500;
  color: var(--color-text-secondary);
  margin-bottom: 0.25rem;
}

.field-input {
  width: 100%;
  padding: 0.5rem 0.75rem;
  border: 1px solid var(--color-border);
  border-radius: 8px;
  font-size: 0.9rem;
  color: var(--color-text);
  background: var(--color-bg);
  transition: border-color 0.15s;
  box-sizing: border-box;
}

.field-input:focus {
  outline: none;
  border-color: var(--color-primary);
}

@media (max-width: 768px) {
  .config-fields {
    grid-template-columns: 1fr;
  }
}
</style>
