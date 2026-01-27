<template>
  <Teleport to="body">
    <Transition name="modal">
      <div class="dialog-overlay" v-if="open" @click.self="$emit('cancel')">
        <div class="dialog-panel">
          <h3 class="dialog-title">{{ title }}</h3>
          <p class="dialog-message">{{ message }}</p>
          <div class="dialog-actions">
            <button class="cancel-btn" @click="$emit('cancel')">Cancel</button>
            <button class="confirm-btn" @click="$emit('confirm')">Delete</button>
          </div>
        </div>
      </div>
    </Transition>
  </Teleport>
</template>

<script setup>
defineProps({
  open: Boolean,
  title: {
    type: String,
    default: 'Confirm'
  },
  message: {
    type: String,
    default: 'Are you sure?'
  }
})

defineEmits(['confirm', 'cancel'])
</script>

<style scoped>
.dialog-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.5);
  z-index: 1001;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 1rem;
}

.dialog-panel {
  background: var(--color-bg);
  border-radius: 12px;
  padding: 1.5rem;
  max-width: 400px;
  width: 100%;
  box-shadow: 0 20px 50px rgba(0, 0, 0, 0.2);
}

.dialog-title {
  font-size: 1.1rem;
  font-weight: 600;
  margin-bottom: 0.75rem;
  color: var(--color-text);
}

.dialog-message {
  color: var(--color-text-secondary);
  margin-bottom: 1.5rem;
  line-height: 1.5;
}

.dialog-actions {
  display: flex;
  justify-content: flex-end;
  gap: 0.75rem;
}

.cancel-btn,
.confirm-btn {
  padding: 0.6rem 1.25rem;
  border-radius: 6px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s;
  font-size: 0.95rem;
}

.cancel-btn {
  background: none;
  border: 1px solid var(--color-border);
  color: var(--color-text);
}

.cancel-btn:hover {
  background: var(--color-bg-secondary);
}

.confirm-btn {
  background: var(--color-danger);
  border: none;
  color: white;
}

.confirm-btn:hover {
  background: #dc2626;
}

/* Transition */
.modal-enter-active,
.modal-leave-active {
  transition: opacity 0.2s ease;
}

.modal-enter-active .dialog-panel,
.modal-leave-active .dialog-panel {
  transition: transform 0.2s ease;
}

.modal-enter-from,
.modal-leave-to {
  opacity: 0;
}

.modal-enter-from .dialog-panel,
.modal-leave-to .dialog-panel {
  transform: scale(0.95);
}
</style>
