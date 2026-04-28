import { useUserApi } from "~/composables/api";
import type { Recipe } from "~/lib/api/types/recipe";
import { alert } from "~/composables/use-toast";

export const useRecipe = function (slug: string, eager = true) {
  const api = useUserApi();
  const loading = ref(false);

  const recipe = ref<Recipe | null>(null);

  async function fetchRecipe() {
    loading.value = true;
    const { data } = await api.recipes.getOne(slug);
    loading.value = false;
    if (data) {
      recipe.value = data;
    }
  }

  async function deleteRecipe() {
    loading.value = true;
    const { data } = await api.recipes.deleteOne(slug);
    loading.value = false;
    return data;
  }

  async function updateRecipe(updatedRecipe: Recipe) {
    loading.value = true;
    const { data } = await api.recipes.updateOne(slug, updatedRecipe);
    
    // Background task: Auto-tag user recipe
    if (updatedRecipe.recipeIngredient?.length) {
      const ingredients = updatedRecipe.recipeIngredient
        .map((i: any) => i.note || i.title || i.food?.name)
        .filter(Boolean) as string[];

      if (ingredients.length > 0) {
        api.recommendations.autoTag({ ingredients }).then((res) => {
          if (res.data?.categories?.length) {
            alert.success(`We tagged this as ${res.data.categories[0]} 🍝`);
          }
        }).catch(err => {
          console.warn("Auto-tag failed", err);
        });
      }
    }

    loading.value = false;
    return data;
  }

  onMounted(() => {
    if (eager) {
      fetchRecipe();
    }
  });

  return {
    recipe,
    loading,
    fetchRecipe,
    deleteRecipe,
    updateRecipe,
  };
};
