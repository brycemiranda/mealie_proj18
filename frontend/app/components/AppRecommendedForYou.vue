<template>
  <section
    v-if="!loading"
    class="recommendations-section"
  >
    <div class="d-flex flex-column flex-md-row align-md-center justify-space-between ga-3 mb-4">
      <div>
        <div class="text-h6 font-weight-medium">
          Recommended for You
        </div>
        <div class="text-body-2 text-medium-emphasis">
          Personalized recipes based on your tastes.
        </div>
      </div>
      <div>
        <v-btn
          color="primary"
          variant="outlined"
          size="small"
          @click="showGenrePicker = true"
        >
          Change Preferences
        </v-btn>
      </div>
    </div>

    <v-tabs v-model="activeTab" color="primary" class="mb-4">
      <v-tab value="foryou">For You</v-tab>
      <v-tab value="favorites">Favorites</v-tab>
    </v-tabs>

    <v-window v-model="activeTab">
      <v-window-item value="foryou">

        <!-- Carousel — unlocked after 5 ratings -->
        <template v-if="ratingCount >= RATING_THRESHOLD && carouselItems.length">
          <div class="text-subtitle-2 font-weight-medium text-medium-emphasis mb-2">
            Your Top Picks
          </div>
          <v-slide-group show-arrows class="discovery-carousel mb-6">
            <v-slide-group-item
              v-for="recipe in carouselItems"
              :key="recipe.recipeId"
            >
              <v-card
                class="recommendation-card cursor-pointer d-flex flex-column mx-2"
                width="280"
                variant="outlined"
                @click="openRecipeDetail(recipe)"
              >
                <div class="recommendation-image">
                  <div class="recommendation-overlay">
                    <div class="d-flex align-center justify-space-between px-3 pt-3">
                      <v-chip color="primary" size="x-small" variant="flat">
                        {{ recipe.category }}
                      </v-chip>
                      <span v-if="Math.round(recipe.score * 100) >= 1" class="text-caption text-white">
                        {{ Math.round(recipe.score * 100) }}% Match
                      </span>
                    </div>
                    <div class="recommendation-title-overlay px-3 pb-3">
                      {{ recipe.name }}
                    </div>
                  </div>
                </div>
                <v-card-text class="pb-3 flex-grow-1">
                  <p class="text-body-2 text-medium-emphasis recommendation-description mb-0">
                    {{ recipe.description || "A delicious recipe for you to try." }}
                  </p>
                  <div v-if="recipe.tags?.length" class="d-flex flex-wrap gap-1 mt-3">
                    <v-chip
                      v-for="tag in recipe.tags.slice(0, 3)"
                      :key="`carousel-${recipe.recipeId}-${tag}`"
                      size="x-small"
                      variant="outlined"
                    >
                      {{ tag }}
                    </v-chip>
                  </div>
                </v-card-text>
              </v-card>
            </v-slide-group-item>
          </v-slide-group>
        </template>

        <!-- Progress banner — shown until 5 ratings -->
        <v-alert
          v-if="ratingCount < RATING_THRESHOLD"
          type="info"
          variant="tonal"
          density="compact"
          class="mb-4"
          icon="mdi-star-outline"
        >
          Rate {{ RATING_THRESHOLD - ratingCount }} more {{ RATING_THRESHOLD - ratingCount === 1 ? 'recipe' : 'recipes' }} to unlock your personalized top picks.
          <v-progress-linear
            :model-value="(ratingCount / RATING_THRESHOLD) * 100"
            color="info"
            height="4"
            rounded
            class="mt-2"
          />
        </v-alert>

        <!-- Main grid feed — always shown -->
        <template v-if="feedItems.length">
          <div class="discovery-grid">
            <v-card
              v-for="recipe in feedItems"
              :key="recipe.recipeId"
              class="recommendation-card cursor-pointer d-flex flex-column"
              variant="outlined"
              @click="openRecipeDetail(recipe)"
            >
              <div class="recommendation-image">
                <div class="recommendation-overlay">
                  <div class="d-flex align-center justify-space-between px-3 pt-3">
                    <v-chip color="primary" size="x-small" variant="flat">
                      {{ recipe.category }}
                    </v-chip>
                    <span v-if="Math.round(recipe.score * 100) >= 1" class="text-caption text-white">
                      {{ Math.round(recipe.score * 100) }}% Match
                    </span>
                  </div>
                  <div class="recommendation-title-overlay px-3 pb-3">
                    {{ recipe.name }}
                  </div>
                </div>
              </div>
              <v-card-text class="pb-3 flex-grow-1">
                <p class="text-body-2 text-medium-emphasis recommendation-description mb-0">
                  {{ recipe.description || "A delicious recipe for you to try." }}
                </p>
                <div v-if="recipe.tags?.length" class="d-flex flex-wrap gap-1 mt-3">
                  <v-chip
                    v-for="tag in recipe.tags.slice(0, 3)"
                    :key="`feed-${recipe.recipeId}-${tag}`"
                    size="x-small"
                    variant="outlined"
                  >
                    {{ tag }}
                  </v-chip>
                </div>
              </v-card-text>
            </v-card>
          </div>

          <div class="d-flex justify-center mt-6">
            <v-btn
              v-if="hasMore"
              color="primary"
              variant="tonal"
              :loading="loadingMore"
              @click="loadMore"
            >
              Load More
            </v-btn>
          </div>
        </template>

        <v-card v-else class="recommendation-empty" variant="outlined">
          <v-card-text class="pa-6 pa-md-8 text-center">
            <div class="text-h6 font-weight-medium mb-2">No recommendations found</div>
            <p class="text-body-2 text-medium-emphasis mb-0">Try changing your preferences.</p>
          </v-card-text>
        </v-card>

      </v-window-item>

      <v-window-item value="favorites">
        <v-card class="recommendation-empty" variant="outlined">
          <v-card-text class="pa-6 pa-md-8 text-center">
            <div class="text-h6 font-weight-medium mb-2">Favorites</div>
            <p class="text-body-2 text-medium-emphasis mb-0">Coming soon. Rated recipes will appear here.</p>
          </v-card-text>
        </v-card>
      </v-window-item>
    </v-window>

    <GenrePicker
      v-model="showGenrePicker"
      :can-cancel="!needsOnboarding"
      @saved="onPreferencesSaved"
    />

    <RecipeDetailModal
      v-model="showRecipeModal"
      :recipe="selectedRecipe"
      @rated="onRecipeRated"
    />
  </section>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue';
import { useUserApi } from '~/composables/api';
import type { DiscoveryItem } from '~/lib/api/types/recommendations';

const api = useUserApi();
import GenrePicker from './GenrePicker.vue';
import RecipeDetailModal from './RecipeDetailModal.vue';

const RATING_THRESHOLD = 5;

const activeTab = ref('foryou');
const loading = ref(true);
const loadingMore = ref(false);

const showGenrePicker = ref(false);
const needsOnboarding = ref(false);
const ratingCount = ref(0);

const carouselItems = ref<DiscoveryItem[]>([]);
const feedItems = ref<DiscoveryItem[]>([]);
const currentPage = ref(1);
const hasMore = ref(true);

const showRecipeModal = ref(false);
const selectedRecipe = ref<DiscoveryItem | null>(null);

async function loadStatusAndData() {
  try {
    const status = await api.recommendations.getStatus();
    ratingCount.value = status.data?.ratingCount ?? 0;
    if (status.data?.needsOnboarding) {
      needsOnboarding.value = true;
      showGenrePicker.value = true;
      loading.value = false;
      return;
    }
    await Promise.all([fetchCarousel(), fetchFeed(1)]);
  } catch (err) {
    console.error('Failed to load recommendation status', err);
  } finally {
    loading.value = false;
  }
}

async function fetchCarousel() {
  try {
    const res = await api.recommendations.getDiscovery(1, null, 10);
    if (res.data?.items?.length) {
      carouselItems.value = res.data.items;
    }
  } catch (err) {
    console.error('Failed to fetch carousel', err);
  }
}

async function fetchFeed(page: number, append = false) {
  try {
    const res = await api.recommendations.getDiscovery(page, null, 20);
    if (res.data?.items?.length) {
      if (append) {
        feedItems.value.push(...res.data.items);
      } else {
        feedItems.value = res.data.items;
      }
      hasMore.value = res.data.items.length >= 20;
      currentPage.value = page;
    }
  } catch (err) {
    console.error('Failed to fetch feed', err);
  }
}

async function loadMore() {
  loadingMore.value = true;
  await fetchFeed(currentPage.value + 1, true);
  loadingMore.value = false;
}

function onPreferencesSaved() {
  needsOnboarding.value = false;
  showGenrePicker.value = false;
  Promise.all([fetchCarousel(), fetchFeed(1)]);
}

function openRecipeDetail(recipe: DiscoveryItem) {
  selectedRecipe.value = recipe;
  showRecipeModal.value = true;
}

function onRecipeRated() {
  ratingCount.value = Math.min(ratingCount.value + 1, RATING_THRESHOLD);
  Promise.all([fetchCarousel(), fetchFeed(1)]);
}

onMounted(loadStatusAndData);
</script>

<style scoped>
.recommendations-section {
  margin-top: 0.75rem;
}

.recommendation-empty {
  border-style: dashed;
}

.discovery-carousel {
  padding: 4px 0 8px;
}

.discovery-grid {
  display: grid;
  gap: 1rem;
  grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
}

.recommendation-card {
  height: 340px;
  transition: transform 0.2s;
}

.recommendation-card:hover {
  transform: translateY(-4px);
}

.recommendation-image {
  height: 160px;
  background: linear-gradient(135deg, rgba(32, 52, 84, 0.85), rgba(54, 122, 98, 0.75));
  position: relative;
}

.recommendation-overlay {
  display: flex;
  flex-direction: column;
  justify-content: space-between;
  height: 100%;
}

.recommendation-title-overlay {
  font-size: 1rem;
  font-weight: 600;
  color: #ffffff;
  line-height: 1.35;
  display: -webkit-box;
  -webkit-box-orient: vertical;
  -webkit-line-clamp: 2;
  overflow: hidden;
  text-shadow: 0 1px 3px rgba(0,0,0,0.4);
}

.recommendation-description {
  display: -webkit-box;
  margin-top: 0.5rem;
  overflow: hidden;
  -webkit-box-orient: vertical;
  -webkit-line-clamp: 2;
}

.gap-1 {
  gap: 4px;
}
</style>
