export interface BlueprintBlock {
  readonly type: string;
  readonly text?: string;
  readonly icon?: string;
  readonly color?: string;
  readonly columns?: ReadonlyArray<{ blocks: ReadonlyArray<BlueprintBlock> }>;
  readonly children_text?: string;
  readonly db_index?: number;
  readonly checked?: boolean;
  readonly language?: string;
  readonly url?: string;
}

export interface BlueprintDatabase {
  readonly title?: string;
  readonly is_inline?: boolean;
  readonly properties?: Record<string, unknown>;
  readonly views?: ReadonlyArray<{ type?: string; title?: string; name?: string }>;
  readonly sample_items?: ReadonlyArray<Record<string, unknown>>;
}

export interface BlueprintSubPage {
  readonly title?: string;
  readonly icon?: string;
  readonly blocks?: ReadonlyArray<BlueprintBlock>;
}

export interface BlueprintMainPage {
  readonly title?: string;
  readonly icon?: string;
  readonly cover_url?: string;
}

export interface ListingKit {
  readonly title?: string;
  readonly tagline?: string;
  readonly description?: string;
  readonly features?: ReadonlyArray<string>;
  readonly preview_script?: ReadonlyArray<string>;
  readonly suggested_price_band?: string;
}

export interface BlueprintMetadata {
  readonly title?: string;
  readonly template_type?: string;
  readonly color_theme?: string;
  readonly description?: string;
  readonly icon?: string;
  // 품질 신호 (Phase 2) — 백엔드 metadata에서 도착
  readonly premium_score?: number;
  readonly premium_band?: string;
  readonly premium_band_label?: string;
  readonly premium_ready?: boolean;
  readonly judge_pass?: boolean;
  readonly listing_kit?: ListingKit;
}

export interface NotionBlueprintData {
  readonly main_page?: BlueprintMainPage;
  readonly metadata?: BlueprintMetadata;
  readonly blocks?: ReadonlyArray<BlueprintBlock>;
  readonly databases?: ReadonlyArray<BlueprintDatabase>;
  readonly sub_pages?: ReadonlyArray<BlueprintSubPage>;
}
