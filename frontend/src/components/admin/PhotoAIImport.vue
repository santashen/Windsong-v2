<template>
  <Teleport to="body">
    <Transition name="drawer">
      <div v-if="open" class="ai-import-overlay" @click.self="$emit('close')">
        <section class="ai-import-panel" aria-labelledby="ai-import-title">
          <header class="ai-import-header">
            <div>
              <p class="eyebrow">PHOTO METADATA</p>
              <h2 id="ai-import-title">AI Batch Import</h2>
              <p class="header-description">
                Paste unstructured notes for one or more photos. Nothing will be saved in this step.
              </p>
            </div>
            <button class="close-btn" type="button" aria-label="Close" @click="$emit('close')">
              <CloseIcon />
            </button>
          </header>

          <div class="ai-import-body">
            <section class="input-section">
              <label for="photo-notes">Photo notes</label>
              <textarea
                id="photo-notes"
                v-model="content"
                rows="10"
                placeholder="Photo 1:\nhttps://example.com/kyoto.jpg\nTaken in May 2024 near Kamo River in Kyoto. Cherry blossoms and a river are visible.\n\nPhoto 2:\nhttps://example.com/hangzhou.jpg\nAutumn evening at West Lake in Hangzhou..."
                :disabled="isParsing"
              ></textarea>
              <p class="field-hint">Separate photos with a blank line, a number, or another image URL.</p>
              <p v-if="errorMessage" class="error-message">{{ errorMessage }}</p>
              <button
                class="parse-btn"
                type="button"
                :disabled="isParsing || !content.trim()"
                @click="parseContent"
              >
                {{ isParsing ? 'Parsing...' : (drafts.length ? 'Parse Again' : 'Parse Notes') }}
              </button>
            </section>

            <section class="drafts-section">
              <div class="section-heading">
                <div>
                  <h3>Parsed drafts</h3>
                  <p v-if="drafts.length">{{ drafts.length }} photo drafts · review before importing</p>
                  <p v-else>Parsed photo information will appear here.</p>
                </div>
                <button
                  v-if="drafts.length"
                  class="clear-btn"
                  type="button"
                  @click="drafts = []"
                >
                  Clear
                </button>
              </div>

              <div v-if="!drafts.length" class="empty-drafts">
                <PhotoIcon />
                <p>No drafts yet</p>
              </div>

              <article
                v-for="(draft, index) in drafts"
                :key="draft._key"
                class="draft-card"
                :class="`draft-${draft.importStatus}`"
              >
                <div class="draft-card-header">
                  <label class="draft-select">
                    <input v-model="draft.selected" type="checkbox" />
                    <span>Photo {{ draft.index || index + 1 }}</span>
                  </label>
                  <button class="remove-btn" type="button" @click="removeDraft(index)">Remove</button>
                </div>

                <div class="draft-preview" v-if="draft.url">
                  <img :src="draft.url" :alt="draft.title || 'Photo preview'" @error="draft.imageError = true" />
                  <span v-if="draft.imageError">Preview unavailable</span>
                </div>

                <div class="draft-fields">
                  <label>
                    <span>Image URL <b>*</b></span>
                    <input v-model="draft.url" type="url" />
                  </label>
                  <label>
                    <span>Title <b>*</b></span>
                    <input v-model="draft.title" type="text" />
                  </label>
                  <label class="field-wide">
                    <span>Description</span>
                    <textarea v-model="draft.description" rows="2"></textarea>
                  </label>
                  <label>
                    <span>Date <b>*</b></span>
                    <input v-model="draft.date" type="date" />
                  </label>
                  <label>
                    <span>Location</span>
                    <input v-model="draft.location" type="text" />
                  </label>
                  <label>
                    <span>City</span>
                    <input v-model="draft.city" type="text" />
                  </label>
                  <label>
                    <span>Country</span>
                    <input v-model="draft.country" type="text" />
                  </label>
                  <label class="field-wide">
                    <span>Tags <small>comma separated</small></span>
                    <input v-model="draft.tagsText" type="text" />
                  </label>
                </div>

                <div v-if="draftValidation(draft).length || draft.warnings.length || draft.importError" class="draft-notices">
                  <p v-for="field in draftValidation(draft)" :key="`missing-${field}`" class="notice warning">
                    Required field: {{ field }}
                  </p>
                  <p v-for="warning in draft.warnings" :key="warning" class="notice">{{ warning }}</p>
                  <p v-if="draft.importError" class="notice error">{{ draft.importError }}</p>
                </div>

                <p v-if="draft.importStatus === 'success'" class="import-success">Imported successfully</p>
                <p v-else-if="draft.importStatus === 'duplicate'" class="import-duplicate">Already exists</p>
                <p v-else-if="draft.importStatus === 'submitting'" class="import-progress">Importing...</p>
              </article>
            </section>
          </div>

          <footer class="ai-import-footer">
            <span v-if="drafts.length" class="selection-count">
              {{ selectedCount }} selected<span v-if="summary"> · {{ summary }}</span>
            </span>
            <button class="cancel-btn" type="button" @click="$emit('close')">Close</button>
            <button
              class="submit-btn"
              type="button"
              :disabled="isSubmitting || !canSubmit"
              @click="submitSelected"
            >
              {{ isSubmitting ? 'Importing...' : `Confirm Import${selectedCount ? ` (${selectedCount})` : ''}` }}
            </button>
          </footer>
        </section>
      </div>
    </Transition>
  </Teleport>
</template>

<script setup>
import { computed, ref, watch } from 'vue'
import { adminPhotoApi } from '@/api/admin/photos'
import { CloseIcon, PhotoIcon } from '@/components/icons'

const props = defineProps({
  open: Boolean
})

const emit = defineEmits(['close', 'imported'])

const content = ref('')
const drafts = ref([])
const isParsing = ref(false)
const isSubmitting = ref(false)
const errorMessage = ref('')
const summary = ref('')
let draftKey = 0

const selectedCount = computed(() => drafts.value.filter(draft => draft.selected).length)
const canSubmit = computed(() => drafts.value.some(draft => draft.selected && !draftValidation(draft).length))

function normalizeDraft(item, index) {
  return {
    ...item,
    _key: `${Date.now()}-${draftKey++}`,
    index: item.index || index + 1,
    tagsText: Array.isArray(item.tags) ? item.tags.join(', ') : '',
    missingFields: item.missingFields || [],
    warnings: item.warnings || [],
    selected: true,
    imageError: false,
    importStatus: 'idle',
    importError: ''
  }
}

async function parseContent() {
  if (!content.value.trim()) return
  isParsing.value = true
  errorMessage.value = ''
  try {
    const response = await adminPhotoApi.previewAIImport(content.value)
    drafts.value = (response.data.items || []).map(normalizeDraft)
    summary.value = ''
  } catch (error) {
    if (error.code === 'ECONNABORTED' || error.code === 'ETIMEDOUT') {
      errorMessage.value = 'Parsing took too long. Please try again or split the notes into smaller batches.'
    } else {
      errorMessage.value = error.response?.data?.message || error.response?.data?.detail || error.message || 'Failed to parse photo notes. Please try again.'
    }
  } finally {
    isParsing.value = false
  }
}

function removeDraft(index) {
  drafts.value.splice(index, 1)
}

function draftValidation(draft) {
  const missing = []
  if (!draft.url?.trim()) missing.push('url')
  if (!draft.title?.trim()) missing.push('title')
  if (!draft.date) missing.push('date')
  return missing
}

function toPhotoPayload(draft) {
  return {
    url: draft.url.trim(),
    thumbnail: draft.thumbnail?.trim() || '',
    title: draft.title.trim(),
    description: draft.description?.trim() || '',
    date: draft.date,
    location: draft.location?.trim() || '',
    city: draft.city?.trim() || '',
    country: draft.country?.trim() || '',
    tags: draft.tagsText
      .split(',')
      .map(tag => tag.trim())
      .filter(Boolean),
    aspectRatio: draft.aspectRatio || ''
  }
}

async function submitSelected() {
  const selected = drafts.value.filter(draft => draft.selected && !draftValidation(draft).length)
  if (!selected.length) return

  isSubmitting.value = true
  summary.value = ''
  let succeeded = 0
  let duplicates = 0
  let failed = 0

  for (const draft of selected) {
    draft.importStatus = 'submitting'
    draft.importError = ''
    try {
      await adminPhotoApi.createPhoto(toPhotoPayload(draft))
      draft.importStatus = 'success'
      succeeded += 1
    } catch (error) {
      if (error.response?.status === 409) {
        draft.importStatus = 'duplicate'
        draft.importError = 'A photo with this URL already exists.'
        duplicates += 1
      } else {
        draft.importStatus = 'failed'
        draft.importError = error.message || 'Failed to import this photo.'
        failed += 1
      }
    }
  }

  isSubmitting.value = false
  summary.value = `${succeeded} succeeded${duplicates ? `, ${duplicates} duplicate` : ''}${failed ? `, ${failed} failed` : ''}`
  if (succeeded) emit('imported', { succeeded, duplicates, failed })
}

watch(() => props.open, (open) => {
  if (!open) {
    content.value = ''
    drafts.value = []
    errorMessage.value = ''
    summary.value = ''
  }
})
</script>

<style scoped>
.ai-import-overlay {
  position: fixed;
  inset: 0;
  z-index: 1000;
  display: flex;
  justify-content: flex-end;
  background: rgba(15, 23, 42, 0.45);
}

.ai-import-panel {
  display: flex;
  flex-direction: column;
  width: min(960px, 100%);
  height: 100%;
  background: var(--color-bg);
  box-shadow: -8px 0 30px rgba(15, 23, 42, 0.16);
}

.ai-import-header,
.ai-import-footer {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 1rem;
  padding: 1.25rem 1.5rem;
  border-bottom: 1px solid var(--color-border);
}

.ai-import-header h2,
.section-heading h3 {
  margin: 0;
  color: var(--color-text);
}

.eyebrow {
  margin: 0 0 0.25rem;
  color: var(--color-primary);
  font-size: 0.7rem;
  font-weight: 700;
  letter-spacing: 0.12em;
}

.header-description,
.section-heading p,
.field-hint {
  margin: 0.35rem 0 0;
  color: var(--color-text-secondary);
  font-size: 0.85rem;
}

.close-btn,
.remove-btn,
.clear-btn {
  border: 0;
  background: transparent;
  color: var(--color-text-secondary);
  cursor: pointer;
}

.ai-import-body {
  flex: 1;
  overflow-y: auto;
  padding: 1.5rem;
}

.input-section {
  padding-bottom: 1.5rem;
  border-bottom: 1px solid var(--color-border);
}

.input-section > label,
.draft-fields label {
  display: flex;
  flex-direction: column;
  gap: 0.35rem;
  color: var(--color-text);
  font-size: 0.8rem;
  font-weight: 600;
}

.input-section textarea,
.draft-fields input,
.draft-fields textarea {
  width: 100%;
  box-sizing: border-box;
  border: 1px solid var(--color-border);
  border-radius: 6px;
  background: var(--color-bg);
  color: var(--color-text);
  font: inherit;
}

.input-section textarea {
  margin-top: 0.5rem;
  padding: 0.75rem;
  resize: vertical;
}

.draft-fields input,
.draft-fields textarea {
  padding: 0.55rem 0.65rem;
  font-size: 0.85rem;
}

.input-section textarea:focus,
.draft-fields input:focus,
.draft-fields textarea:focus {
  outline: none;
  border-color: var(--color-primary);
}

.parse-btn,
.submit-btn,
.cancel-btn {
  margin-top: 1rem;
  padding: 0.65rem 1rem;
  border: 0;
  border-radius: 6px;
  font-weight: 600;
  cursor: pointer;
}

.parse-btn,
.submit-btn {
  background: var(--color-primary);
  color: white;
}

.parse-btn:disabled,
.submit-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.cancel-btn {
  margin-left: auto;
  border: 1px solid var(--color-border);
  background: transparent;
  color: var(--color-text);
}

.error-message,
.warning {
  color: #b45309;
}

.error {
  color: #dc2626;
}

.import-success {
  margin: 0.85rem 0 0;
  color: #15803d;
  font-size: 0.85rem;
  font-weight: 600;
}

.import-progress {
  margin: 0.85rem 0 0;
  color: var(--color-primary);
  font-size: 0.85rem;
}

.import-duplicate {
  margin: 0.85rem 0 0;
  color: #a16207;
  font-size: 0.85rem;
  font-weight: 600;
}

.drafts-section {
  padding-top: 1.5rem;
}

.section-heading {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 1rem;
  margin-bottom: 1rem;
}

.empty-drafts {
  display: grid;
  justify-items: center;
  gap: 0.5rem;
  padding: 3rem 1rem;
  border: 1px dashed var(--color-border);
  border-radius: 8px;
  color: var(--color-text-secondary);
}

.draft-card {
  margin-bottom: 1rem;
  padding: 1rem;
  border: 1px solid var(--color-border);
  border-radius: 8px;
  background: var(--color-bg-secondary);
}

.draft-card-header {
  display: flex;
  justify-content: space-between;
  margin-bottom: 0.85rem;
}

.draft-select {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  color: var(--color-text);
  font-weight: 600;
}

.draft-preview {
  display: flex;
  align-items: center;
  justify-content: center;
  min-height: 120px;
  margin-bottom: 1rem;
  overflow: hidden;
  border-radius: 6px;
  background: var(--color-bg);
  color: var(--color-text-secondary);
}

.draft-preview img {
  display: block;
  width: 100%;
  max-height: 220px;
  object-fit: contain;
}

.draft-fields {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 0.85rem;
}

.field-wide {
  grid-column: 1 / -1;
}

.draft-fields b {
  color: #dc2626;
}

.draft-fields small {
  color: var(--color-text-secondary);
  font-weight: 400;
}

.draft-notices {
  margin-top: 0.85rem;
}

.notice {
  margin: 0.25rem 0;
  color: var(--color-text-secondary);
  font-size: 0.8rem;
}

.selection-count {
  color: var(--color-text-secondary);
  font-size: 0.85rem;
}

@media (max-width: 640px) {
  .ai-import-header,
  .ai-import-body,
  .ai-import-footer {
    padding: 1rem;
  }

  .draft-fields {
    grid-template-columns: 1fr;
  }

  .field-wide {
    grid-column: auto;
  }
}
</style>
