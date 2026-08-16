import { useState } from "react";
import type { ProductResult } from "../api/types";

interface Props {
  product: ProductResult;
}

const COLOR_OVERRIDES: Record<string, string> = {
  cream: "#efe6d5",
  floral: "#d98ba6",
  "red plaid": "#8c2f24",
};

function swatchColor(color: string): string {
  const key = color.toLowerCase().trim();
  return COLOR_OVERRIDES[key] ?? key;
}

const MAX_SWATCHES = 4;

export function ProductCard({ product }: Props) {
  const [imageFailed, setImageFailed] = useState(false);
  const prices = product.items.map((i) => i.price).filter((p): p is number => p != null);
  const minPrice = prices.length ? Math.min(...prices) : null;
  const totalStock = product.items.reduce((sum, i) => sum + i.stock, 0);
  const showImage = product.image_url && !imageFailed;

  const colors = [...new Set(product.items.map((i) => i.color).filter((c): c is string => !!c))];
  const visibleColors = colors.slice(0, MAX_SWATCHES);
  const extraColorCount = colors.length - visibleColors.length;

  return (
    <div className="product-card" title={product.description}>
      <div className="product-card__image-wrapper">
        {showImage ? (
          <img
            className="product-card__image"
            src={product.image_url!}
            alt={product.title}
            loading="lazy"
            onError={() => setImageFailed(true)}
          />
        ) : (
          <div className="product-card__image-placeholder" aria-hidden="true">
            {product.title.charAt(0)}
          </div>
        )}
        {totalStock === 0 && <div className="product-card__oos-badge">Out of stock</div>}
      </div>
      <div className="product-card__body">
        <h3 className="product-card__title">{product.title}</h3>
        {minPrice != null && <div className="product-card__price">${minPrice.toFixed(2)}</div>}
        {visibleColors.length > 0 && (
          <div className="product-card__swatches">
            {visibleColors.map((color) => (
              <span
                key={color}
                className="product-card__swatch"
                style={{ backgroundColor: swatchColor(color) }}
                title={color}
              />
            ))}
            {extraColorCount > 0 && (
              <span className="product-card__swatch-more">+{extraColorCount}</span>
            )}
          </div>
        )}
      </div>
    </div>
  );
}
