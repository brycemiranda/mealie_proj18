from fastapi import BackgroundTasks, Query
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from uuid import UUID

from mealie.db.models.recipe.recipe import RecipeModel
from mealie.routes._base import BaseUserController, controller
from mealie.routes._base.routers import UserAPIRouter
from mealie.schema.recommendations import (
    AutoTagIn,
    AutoTagResult,
    DiscoveryResult,
    DiscoveryRatingIn,
    RecommendationAck,
    RecommendationDismissIn,
    RecommendationPreferencesIn,
    RecommendationResult,
    RecommendationStatus,
)
from mealie.services.recommendation_service import (
    apply_dismiss_feedback,
    apply_rating_feedback,
    call_auto_tag,
    expand_categories_to_tags,
    fetch_discovery,
    fetch_recommendations,
    fetch_tag_vector,
    get_or_create_prefs,
    get_prefs,
)

router = UserAPIRouter(prefix="/recommendations", tags=["Recommendations"])


@controller(router)
class RecommendationController(BaseUserController):
    def _get_group_recipes(self) -> list[RecipeModel]:
        return (
            self.session.execute(
                select(RecipeModel)
                .options(selectinload(RecipeModel.tags))
                .filter(RecipeModel.group_id == self.group_id)
                .order_by(RecipeModel.name)
            )
            .scalars()
            .unique()
            .all()
        )

    @router.get("/status", response_model=RecommendationStatus)
    def status(self):
        prefs = get_prefs(self.session, self.user.id)
        return RecommendationStatus(
            needs_onboarding=prefs is None or not prefs.onboarding_tags,
            has_vector=bool(prefs and prefs.taste_vector),
            rating_count=prefs.rating_count if prefs else 0,
        )

    @router.post("/preferences", response_model=RecommendationAck)
    def set_preferences(self, body: RecommendationPreferencesIn):
        prefs = get_or_create_prefs(self.session, self.user.id)
        prefs.onboarding_tags = list(dict.fromkeys(tag.strip() for tag in body.tags if tag.strip()))
        # Expand category names (e.g. "Italian") to Food.com tag keywords before vectorizing
        expanded = expand_categories_to_tags(prefs.onboarding_tags)
        prefs.taste_vector = fetch_tag_vector(expanded)
        self.session.commit()
        return RecommendationAck()

    @router.get("", response_model=RecommendationResult)
    async def get_recommendations(self):
        recipes = self._get_group_recipes()
        return RecommendationResult(**await fetch_recommendations(self.session, self.user.id, recipes))

    @router.get("/discovery", response_model=DiscoveryResult)
    def get_discovery(
        self,
        page: int = Query(1, ge=1),
        page_size: int = Query(20, ge=1, le=50),
        category: str | None = Query(None),
    ):
        prefs = get_prefs(self.session, self.user.id)
        user_categories = prefs.onboarding_tags if prefs and prefs.onboarding_tags else None
        data = fetch_discovery(str(self.user.id), page=page, category=category, page_size=page_size, categories=user_categories)
        return DiscoveryResult(**data)

    @router.post("/auto-tag", response_model=AutoTagResult)
    def get_auto_tag(self, body: AutoTagIn):
        data = call_auto_tag(body.ingredients)
        return AutoTagResult(**data)

    @router.post("/dismiss", response_model=RecommendationAck)
    def dismiss(self, body: RecommendationDismissIn, background_tasks: BackgroundTasks):
        recipe_tags = list(dict.fromkeys(tag.strip() for tag in body.tags if tag.strip()))
        if not recipe_tags:
            try:
                recipe_id = UUID(body.recipe_id)
            except ValueError:
                recipe_id = None

            if recipe_id is not None:
                recipe = (
                    self.session.execute(
                        select(RecipeModel)
                        .options(selectinload(RecipeModel.tags))
                        .filter(
                            RecipeModel.id == recipe_id,
                            RecipeModel.group_id == self.group_id,
                        )
                    )
                    .scalars()
                    .first()
                )
                if recipe:
                    recipe_tags = [tag.name for tag in recipe.tags]

        background_tasks.add_task(
            apply_dismiss_feedback,
            self.user.id,
            body.recipe_id,
            recipe_tags,
        )
        return RecommendationAck()

    @router.post("/rate", response_model=RecommendationAck)
    def rate_discovery(self, body: DiscoveryRatingIn, background_tasks: BackgroundTasks):
        background_tasks.add_task(
            apply_rating_feedback,
            self.user.id,
            body.recipe_id,
            body.tags,
            body.rating,
        )
        return RecommendationAck()
