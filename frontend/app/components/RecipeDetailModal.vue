<template>
  <v-dialog v-model="isOpen" max-width="800" scrollable>
    <v-card v-if="recipe">
      <v-card-title class="d-flex align-center py-4 px-6 bg-grey-lighten-4">
        <span class="text-h5 font-weight-bold mr-auto">{{ recipe.name }}</span>
        <v-btn icon="mdi-close" variant="text" @click="close"></v-btn>
      </v-card-title>
      
      <v-card-text class="pa-6" style="max-height: 70vh;">
        <div class="mb-6 d-flex align-center flex-wrap gap-2">
          <v-chip color="primary" variant="flat" size="small" class="font-weight-bold">
            {{ recipe.category }}
          </v-chip>
          <v-chip v-for="tag in recipe.tags" :key="tag" size="small" variant="outlined">
            {{ tag }}
          </v-chip>
        </div>

        <p class="text-body-1 mb-6 text-grey-darken-2" v-if="recipe.description">
          {{ recipe.description }}
        </p>

        <v-row>
          <v-col cols="12" md="4">
            <h3 class="text-h6 font-weight-bold mb-4">Ingredients</h3>
            <v-list density="compact" class="bg-transparent">
              <v-list-item
                v-for="(ingredient, i) in recipe.ingredients"
                :key="i"
                class="px-0 py-1"
              >
                <template v-slot:prepend>
                  <v-icon icon="mdi-circle-small" size="x-small"></v-icon>
                </template>
                <v-list-item-title class="text-body-2" style="white-space: normal;">
                  {{ ingredient }}
                </v-list-item-title>
              </v-list-item>
            </v-list>
          </v-col>
          
          <v-col cols="12" md="8">
            <h3 class="text-h6 font-weight-bold mb-4">Instructions</h3>
            <v-list density="compact" class="bg-transparent">
              <v-list-item
                v-for="(step, i) in recipe.steps"
                :key="i"
                class="px-0 py-2 align-start"
              >
                <template v-slot:prepend>
                  <div class="mr-4 mt-1 font-weight-bold text-grey">{{ i + 1 }}.</div>
                </template>
                <v-list-item-title class="text-body-1" style="white-space: normal; line-height: 1.5;">
                  {{ step }}
                </v-list-item-title>
              </v-list-item>
            </v-list>
          </v-col>
        </v-row>
      </v-card-text>

      <v-divider></v-divider>

      <v-card-actions class="pa-4 bg-grey-lighten-4 d-flex flex-column align-center">
        <div class="text-subtitle-1 font-weight-medium mb-2">How does this look?</div>
        <v-rating
          v-model="rating"
          color="amber"
          hover
          size="large"
          @update:modelValue="submitRating"
        ></v-rating>
      </v-card-actions>
    </v-card>
  </v-dialog>
</template>

<script setup lang="ts">
import { ref, watch } from 'vue';
import { useUserApi } from '~/composables/api';
import type { DiscoveryItem } from '~/lib/api/types/recommendations';

const api = useUserApi();

const props = defineProps<{
  modelValue: boolean;
  recipe: DiscoveryItem | null;
}>();

const emit = defineEmits<{
  (e: 'update:modelValue', value: boolean): void;
  (e: 'rated'): void;
}>();

const isOpen = ref(props.modelValue);
const rating = ref<number>(0);

watch(() => props.modelValue, (newVal) => {
  isOpen.value = newVal;
  if (newVal && props.recipe) {
    const saved = localStorage.getItem(`rating_${props.recipe.recipeId}`);
    rating.value = saved ? parseInt(saved) : 0;
  }
});

watch(isOpen, (newVal) => {
  emit('update:modelValue', newVal);
});

function close() {
  isOpen.value = false;
}

async function submitRating(val: number) {
  if (!props.recipe || val === 0) return;
  
  try {
    await api.recommendations.rateDiscovery({
      recipeId: props.recipe.recipeId,
      tags: props.recipe.tags,
      rating: val
    });
    localStorage.setItem(`rating_${props.recipe.recipeId}`, val.toString());
    emit('rated');
    setTimeout(() => {
      close();
    }, 500);
  } catch (err) {
    console.error('Failed to submit rating', err);
  }
}
</script>

<style scoped>
.gap-2 {
  gap: 8px;
}
</style>
