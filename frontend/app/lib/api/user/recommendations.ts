import { BaseAPI } from "../base/base-clients";
import type {
  RecommendationDismissIn,
  RecommendationPreferencesIn,
  RecommendationResult,
  RecommendationStatus,
  DiscoveryResult,
  AutoTagIn,
  AutoTagResult,
  DiscoveryRatingIn,
} from "../types/recommendations";

const prefix = "/api/recommendations";

const routes = {
  base: prefix,
  status: `${prefix}/status`,
  preferences: `${prefix}/preferences`,
  dismiss: `${prefix}/dismiss`,
  discovery: `${prefix}/discovery`,
  autoTag: `${prefix}/auto-tag`,
  rate: `${prefix}/rate`,
};

export class RecommendationApi extends BaseAPI {
  async getStatus() {
    return await this.requests.get<RecommendationStatus>(routes.status);
  }

  async getRecommendations() {
    return await this.requests.get<RecommendationResult>(routes.base);
  }

  async setPreferences(payload: RecommendationPreferencesIn) {
    return await this.requests.post<{ status: string }, RecommendationPreferencesIn>(routes.preferences, payload);
  }

  async dismiss(payload: RecommendationDismissIn) {
    return await this.requests.post<{ status: string }, RecommendationDismissIn>(routes.dismiss, payload);
  }

  async getDiscovery(page: number = 1, category: string | null = null, pageSize: number = 20) {
    let url = `${routes.discovery}?page=${page}&page_size=${pageSize}`;
    if (category) {
      url += `&category=${encodeURIComponent(category)}`;
    }
    return await this.requests.get<DiscoveryResult>(url);
  }

  async autoTag(payload: AutoTagIn) {
    return await this.requests.post<AutoTagResult, AutoTagIn>(routes.autoTag, payload);
  }

  async rateDiscovery(payload: DiscoveryRatingIn) {
    return await this.requests.post<{ status: string }, DiscoveryRatingIn>(routes.rate, payload);
  }
}
