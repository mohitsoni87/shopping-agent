import type { ProductResult } from "../api/types";
import { ProductCard } from "./ProductCard";

interface Props {
  results: ProductResult[];
  offset: number;
  hasMore: boolean;
  loading: boolean;
  onPrev: () => void;
  onNext: () => void;
}

export function ProductGrid({ results, offset, hasMore, loading, onPrev, onNext }: Props) {
  if (results.length === 0) {
    return <div className="product-grid__empty">No matching products found.</div>;
  }

  const canGoPrev = offset > 0;

  return (
    <div className="product-grid-wrapper">
      <div className="product-grid">
        {results.map((product, idx) => (
          <ProductCard key={`${offset}-${idx}`} product={product} />
        ))}
      </div>
      <div className="product-grid__pagination">
        <button onClick={onPrev} disabled={!canGoPrev || loading}>
          &larr; Previous
        </button>
        <span className="product-grid__page-info">
          Showing {offset + 1}&ndash;{offset + results.length}
        </span>
        <button onClick={onNext} disabled={!hasMore || loading}>
          Next &rarr;
        </button>
      </div>
    </div>
  );
}
