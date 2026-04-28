<template>
  <v-dialog v-model="isOpen" max-width="600" persistent>
    <v-card>
      <v-card-title class="text-h5 font-weight-bold pt-6 px-6">
        What do you like to eat?
      </v-card-title>
      <v-card-subtitle class="px-6 pb-2">
        Pick up to 3 genres to personalize your feed.
      </v-card-subtitle>
      
      <v-card-text class="px-6 py-4">
        <v-row dense>
          <v-col
            v-for="genre in availableGenres"
            :key="genre"
            cols="auto"
          >
            <v-btn
              :color="selectedGenres.includes(genre) ? 'primary' : 'grey-lighten-2'"
              :variant="selectedGenres.includes(genre) ? 'flat' : 'outlined'"
              rounded="pill"
              class="text-none mr-2 mb-2"
              @click="toggleGenre(genre)"
              :disabled="!selectedGenres.includes(genre) && selectedGenres.length >= 3"
            >
              {{ genre }}
            </v-btn>
          </v-col>
        </v-row>
      </v-card-text>

      <v-card-actions class="px-6 pb-6">
        <v-spacer></v-spacer>
        <v-btn
          v-if="canCancel"
          variant="text"
          @click="close"
        >
          Cancel
        </v-btn>
        <v-btn
          color="primary"
          variant="flat"
          :disabled="selectedGenres.length === 0"
          :loading="isSaving"
          @click="savePreferences"
        >
          Save Preferences
        </v-btn>
      </v-card-actions>
    </v-card>
  </v-dialog>
</template>

<script setup lang="ts">
import { ref, watch } from 'vue';
import { useUserApi } from '~/composables/api';

const api = useUserApi();

const props = defineProps<{
  modelValue: boolean;
  canCancel?: boolean;
  initialSelection?: string[];
}>();

const emit = defineEmits<{
  (e: 'update:modelValue', value: boolean): void;
  (e: 'saved', tags: string[]): void;
}>();

const isOpen = ref(props.modelValue);
const isSaving = ref(false);

const availableGenres = [
  'Italian', 'American', 'Indian', 'Chinese', 'Mexican', 'Vegetarian', 'Desserts'
];

const selectedGenres = ref<string[]>([]);

watch(() => props.modelValue, (newVal) => {
  isOpen.value = newVal;
  if (newVal) {
    selectedGenres.value = [...(props.initialSelection || [])].filter(g => availableGenres.includes(g));
  }
});

watch(isOpen, (newVal) => {
  emit('update:modelValue', newVal);
});

function toggleGenre(genre: string) {
  const index = selectedGenres.value.indexOf(genre);
  if (index > -1) {
    selectedGenres.value.splice(index, 1);
  } else if (selectedGenres.value.length < 3) {
    selectedGenres.value.push(genre);
  }
}

function close() {
  isOpen.value = false;
}

async function savePreferences() {
  isSaving.value = true;
  try {
    await api.recommendations.setPreferences({ tags: selectedGenres.value });
    emit('saved', selectedGenres.value);
    close();
  } catch (err) {
    console.error('Failed to save preferences', err);
  } finally {
    isSaving.value = false;
  }
}
</script>
