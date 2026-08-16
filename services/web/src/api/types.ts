export interface ItemResult {
  size: string | null;
  color: string | null;
  price: number | null;
  stock: number;
}

export interface ProductResult {
  title: string;
  description: string;
  category: string | null;
  image_url: string | null;
  items: ItemResult[];
}

export interface ChatResponse {
  search_id: string;
  answer: string;
  results: ProductResult[];
  offset: number;
  limit: number;
  has_more: boolean;
}

export interface SearchPageResponse {
  results: ProductResult[];
  offset: number;
  limit: number;
  has_more: boolean;
}

export interface ChatMessage {
  id: string;
  role: "user" | "assistant";
  text: string;
  searchId?: string;
  results?: ProductResult[];
  offset?: number;
  limit?: number;
  hasMore?: boolean;
}
