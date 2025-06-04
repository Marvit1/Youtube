<template>
  <div class="min-h-screen bg-gray-100 py-8 px-4">
    <div class="max-w-4xl mx-auto">
      <h1 class="text-3xl font-bold text-center mb-8">YouTube-ի տեքստի դիտում</h1>
      
      <div class="bg-white rounded-lg shadow-md p-6 mb-6">
        <div class="mb-4">
          <label class="block text-gray-700 text-sm font-bold mb-2" for="url">
            YouTube վիդեոյի հղում
          </label>
          <input
            id="url"
            v-model="videoUrl"
            type="text"
            class="w-full px-3 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
            placeholder="Մուտքագրեք YouTube վիդեոյի հղումը"
          />
        </div>
        
        <button
          @click="fetchTranscript"
          class="w-full bg-blue-500 text-white py-2 px-4 rounded-lg hover:bg-blue-600 transition-colors flex items-center justify-center"
          :disabled="isLoading"
        >
          <span v-if="isLoading" class="mr-2">
            <svg class="animate-spin h-5 w-5 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
              <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
              <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
            </svg>
          </span>
          {{ isLoading ? 'Բեռնվում է...' : 'Ստանալ տեքստը' }}
        </button>
      </div>

      <div v-if="transcript.length > 0" class="bg-white rounded-lg shadow-md p-6">
        <div class="mb-4">
          <span class="text-sm">Էջ {{ currentPage }} / {{ totalPages }}</span>

          <label class="block text-gray-700 text-sm font-bold mb-2" for="keywords">
            Բանալի բառեր (բաժանված ստորակետերով)
          </label>
          <input
            id="keywords"
            v-model="keywords"
            type="text"
            class="w-full px-3 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
            placeholder="Մուտքագրեք բանալի բառերը"
          />
        </div>

        <div class="mb-4">
          <h3 class="text-sm font-bold mb-2">Առաջարկվող բանալի բառեր:</h3>
          <div class="flex flex-wrap gap-2">
            <button
              v-for="(word, index) in suggestedKeywords"
              :key="index"
              @click="toggleKeyword(word)"
              class="px-2 py-1 rounded transition-colors text-sm relative"
              :class="isKeywordActive(word) ? 'bg-blue-300 text-blue-800' : 'bg-blue-100 text-blue-700 hover:bg-blue-200'"
            >
              {{ word }}
              <span 
                v-if="isKeywordActive(word)"
                class="absolute -top-1 -right-1 bg-red-500 text-white rounded-full w-4 h-4 flex items-center justify-center text-xs"
              >x</span>
            </button>
          </div>
        </div>

        <div v-if="keywordMatches.length > 0" class="mb-6 p-4 bg-blue-50 rounded-lg">
          <h3 class="font-bold mb-3 text-lg">Բանալի բառերի հանդիպումներ:</h3>
          <div class="space-y-2">
            <div v-for="(match, index) in keywordMatches" :key="index" 
                 class="p-2 bg-white rounded border border-blue-100 hover:bg-blue-50 transition-colors">
              <span class="text-blue-600 font-medium">{{ match.timestamp }}</span>
              <span class="ml-2" v-html="match.text"></span>
            </div>
          </div>
        </div>

        <div class="mt-4 p-4 bg-gray-50 rounded-lg">
          <div v-for="(section, index) in currentPageSections" :key="index" class="mb-6">
            <p v-html="highlightText(section.text)" class="text-lg leading-relaxed whitespace-pre-wrap"></p>
          </div>
        </div>

        <div class="mb-4 flex items-center justify-between">
          <div class="text-sm text-gray-600">
            Լեզու: {{ language }}
          </div>
          <div class="flex items-center space-x-2">
            <button
              @click="currentPage--"
              :disabled="currentPage === 1"
              class="px-3 py-1 border rounded hover:bg-gray-100 disabled:opacity-50"
            >
              Նախորդ
            </button>
            <span class="text-sm">Էջ {{ currentPage }} / {{ totalPages }}</span>
            <button
              @click="currentPage++"
              :disabled="currentPage === totalPages"
              class="px-3 py-1 border rounded hover:bg-gray-100 disabled:opacity-50"
            >
              Հաջորդ
            </button>
          </div>
        </div>

        <div v-if="keywordMatches.length > 0" class="mt-6 p-4 bg-blue-50 rounded-lg">
          <h3 class="font-bold mb-3 text-lg">Բանալի բառերի հանդիպումներ տեքստի մեջ:</h3>
          <div class="space-y-2">
            <div v-for="(match, index) in keywordMatches" :key="index" 
                 class="p-2 bg-white rounded border border-blue-100 hover:bg-blue-50 transition-colors">
              <span class="text-blue-600 font-medium">{{ match.timestamp }}</span>
              <span class="ml-2" v-html="match.text"></span>
            </div>
          </div>
        </div>

        <div class="mt-4 flex items-center justify-center space-x-2">
          <button
            @click="currentPage--"
            :disabled="currentPage === 1"
            class="px-3 py-1 border rounded hover:bg-gray-100 disabled:opacity-50"
          >
            Նախորդ
          </button>
          <span class="text-sm">Էջ {{ currentPage }} / {{ totalPages }}</span>
          <button
            @click="currentPage++"
            :disabled="currentPage === totalPages"
            class="px-3 py-1 border rounded hover:bg-gray-100 disabled:opacity-50"
          >
            Հաջորդ
          </button>
        </div>
      </div>

      <div v-if="error" class="mt-4 p-4 bg-red-100 text-red-700 rounded-lg flex items-center justify-between">
        <span>{{ error }}</span>
        <button
          v-if="error.includes('ձախողվեց')"
          @click="retryFetch"
          class="ml-4 px-3 py-1 bg-red-600 text-white rounded hover:bg-red-700 transition-colors"
        >
          Կրկին փորձել
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, watch } from 'vue'
import axios from 'axios'

const videoUrl = ref('')
const transcript = ref([])
const rawTranscript = ref([])
const keywords = ref('')
const isLoading = ref(false)
const error = ref('')
const currentPage = ref(1)
const language = ref('')
const sectionsPerPage = 5
const lastVideoUrl = ref('')

const totalPages = computed(() => {
  if (!transcript.value) return 1
  return Math.ceil(transcript.value.length / sectionsPerPage)
})

const currentPageSections = computed(() => {
  if (!transcript.value) return []
  const start = (currentPage.value - 1) * sectionsPerPage
  const end = start + sectionsPerPage
  return transcript.value.slice(start, end)
})

const keywordMatches = computed(() => {
  if (!keywords.value || !rawTranscript.value) return []

  const keywordList = keywords.value.split(',').map(k => k.trim()).filter(k => k)
  if (keywordList.length === 0) return []

  const matches = []
  rawTranscript.value.forEach(entry => {
    keywordList.forEach(keyword => {
      if (entry.text.toLowerCase().includes(keyword.toLowerCase())) {
        matches.push({
          text: highlightKeyword(entry.text),
          timestamp: formatTime(entry.start)
        })
      }
    })
  })
  return matches
})

const formatTime = (seconds) => {
  const minutes = Math.floor(seconds / 60)
  const remainingSeconds = Math.floor(seconds % 60)
  return `${minutes}:${remainingSeconds.toString().padStart(2, '0')}`
}

const highlightText = (text) => {
  if (!keywords.value) return text

  const keywordList = keywords.value.split(',').map(k => k.trim()).filter(k => k)
  if (keywordList.length === 0) return text

  let highlighted = text
  keywordList.forEach(keyword => {
    const regex = new RegExp(keyword, 'gi')
    highlighted = highlighted.replace(regex, match => 
      `<span class="text-red-500 font-bold">${match}</span>`
    )
  })
  return highlighted
}

const highlightKeyword = (text) => {
  if (!keywords.value) return text

  const keywordList = keywords.value.split(',').map(k => k.trim()).filter(k => k)
  if (keywordList.length === 0) return text

  let highlighted = text
  keywordList.forEach(keyword => {
    const regex = new RegExp(keyword, 'gi')
    highlighted = highlighted.replace(regex, match => 
      `<span class="text-red-500 font-bold">${match}</span>`
    )
  })
  return highlighted
}

const retryFetch = () => {
  if (lastVideoUrl.value) {
    videoUrl.value = lastVideoUrl.value
    fetchTranscript()
  }
}

const fetchTranscript = async () => {
  if (!videoUrl.value) {
    error.value = 'Խնդրում ենք մուտքագրել YouTube հղում'
    return
  }

  lastVideoUrl.value = videoUrl.value
  isLoading.value = true
  error.value = ''
  transcript.value = []
  rawTranscript.value = []
  currentPage.value = 1

  try {
    const response = await axios.post('http://localhost:5000/api/transcript', {
      url: videoUrl.value
    })
    transcript.value = response.data.transcript
    rawTranscript.value = response.data.raw_transcript
    language.value = response.data.language
  } catch (err) {
    error.value = err.response?.data?.error || 'Տեքստը ստանալը ձախողվեց'
  } finally {
    isLoading.value = false
  }
}

const suggestedKeywords = computed(() => {
  return ['Գագիկ', 'Ծառուկյան', 'բհկ']
})

const isKeywordActive = (word) => {
  if (!keywords.value) return false
  const currentKeywords = keywords.value.split(',').map(k => k.trim())
  return currentKeywords.includes(word)
}

const toggleKeyword = (word) => {
  const currentKeywords = keywords.value ? keywords.value.split(',').map(k => k.trim()) : []
  
  if (currentKeywords.includes(word)) {
    // Remove the word if it's already in the list
    keywords.value = currentKeywords.filter(k => k !== word).join(', ')
  } else {
    // Add the word if it's not in the list
    keywords.value = currentKeywords.length > 0 
      ? `${keywords.value}, ${word}`
      : word
  }
}
</script>

<style>
@tailwind base;
@tailwind components;
@tailwind utilities;

body {
  font-family: 'Noto Sans Armenian', system-ui, -apple-system, sans-serif;
}
</style> 